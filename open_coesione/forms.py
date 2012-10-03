# coding=utf-8
from django import forms
from django.conf import settings
from open_coesione.models import ContactMessage

class ContactForm(forms.Form):

    name = forms.CharField(max_length= 50, label='Nome')
    surname = forms.CharField(max_length= 100, label='Cognome')
    email = forms.EmailField()
    organization = forms.CharField(max_length= 100, label='Istituzione/Società/Ente')
    location = forms.CharField(max_length=300, label='Luogo')
    reason = forms.TypedChoiceField(choices=ContactMessage.REASON_CHOICES, label='Motivo del contatto', coerce=int, empty_value= '-----')

    body = forms.CharField( widget=forms.Textarea, label='Messaggio' )

    def execute(self):
        from django.core.mail import EmailMultiAlternatives
        from django.utils.html import strip_tags
        from django.template.loader import render_to_string

        values_dict = {
            'body': self.cleaned_data.get('body','Testo del messaggio'),
            'sender': "{0} {1}".format( self.cleaned_data.get('name',''), self.cleaned_data.get('surname','')),
            'organization' : self.cleaned_data.get('organization',''),
            'location' : self.cleaned_data.get('location',''),
            'reason' : self.cleaned_data.get('reason'),
            'email': self.cleaned_data.get('email','')
        }

        # create new ContactMessage
        omsg = ContactMessage()
        for k in values_dict:
            setattr(omsg, k, values_dict[k])
        omsg.save()

        # convert selected choice to text
        values_dict['reason'] = dict(ContactMessage.REASON_CHOICES)[self.cleaned_data.get('reason')]

        html_content = render_to_string('mail/info.html', values_dict)

        text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.

        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives('Richiesta informazioni da opencoesione.gov.it', text_content, self.cleaned_data.get('email'), settings.CONTACTS_EMAIL)
        msg.attach_alternative(html_content, "text/html")
        msg.send()


