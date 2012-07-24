# coding=utf-8
from django import forms
from django.conf import settings

class ContactForm(forms.Form):

    REASON_CHOICES = (
        ('', '--------------'),
        (1, 'domanda sui dati'),
        (2, 'domanda sul sito'),
        (3, 'esempio di riuso: applicazioni'),
        (4, 'esempio di riuso: visualizzazioni'),
        (5, 'esempio di riuso: analisi'),
        (6, 'segnalazione errore nei dati'),
        (7, 'segnalazione relativa a un progetto'),
        (8, 'suggerimenti e consigli'),
    )

    name = forms.CharField(max_length= 50, label='Nome')
    surname = forms.CharField(max_length= 100, label='Cognome')
    email = forms.EmailField()
    organization = forms.CharField(max_length= 100, label='Istituzione/Società/Ente')
    location = forms.CharField(max_length=300, label='Luogo')
    reason = forms.TypedChoiceField(choices=REASON_CHOICES, label='Motivo del contatto', coerce=int, empty_value= '-----')

    body = forms.CharField( widget=forms.Textarea, label='Messaggio' )

    def send_mail(self):
        from django.core.mail import EmailMultiAlternatives
        from django.utils.html import strip_tags
        from django.template.loader import render_to_string


        html_content = render_to_string('mail/info.html', {
            'body': self.cleaned_data.get('body','Testo del messaggio'),
            'sender': "{0} {1}".format( self.cleaned_data.get('name',''), self.cleaned_data.get('surname','')),
            'organization' : self.cleaned_data.get('organization',''),
            'location' : self.cleaned_data.get('location',''),
            'reason' : dict(self.REASON_CHOICES)[self.cleaned_data.get('reason')],
            'email': self.cleaned_data.get('email','')
        })

        text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.

        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives('Richiesta informazioni da opencoesione.gov.it', text_content, self.cleaned_data.get('email'), settings.CONTACTS_EMAIL)
        msg.attach_alternative(html_content, "text/html")
        msg.send()