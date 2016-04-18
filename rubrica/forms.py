# coding=utf-8
from django import forms
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from rubrica.models import Iscrizione, IscrizioneManager


class NLContactForm(forms.Form):
    """
    The custom form to subscribe to the Newsletter.
    """
    USER_TYPES = ((u'', u'--------------'),) + tuple(Iscrizione.TYPES)

    first_name = forms.CharField(max_length= 80, label='Nome', required=False)
    last_name = forms.CharField(max_length= 80, label='Cognome', required=False)
    email = forms.EmailField(label='Email *')
    user_type = forms.TypedChoiceField(choices=USER_TYPES, label='Tipologia di utente *', empty_value= '-----')
    notes = forms.CharField(widget=forms.Textarea, label='Note', required=False, help_text='Spazio per delle note libere')
    privacy = forms.BooleanField(required=True, label='Autorizzazione all\'utilizzo dei dati personali *')

    def execute(self):
        source_dict = {
            'slug': 'opencoesione',
            'name': 'Opencoesione',
            'uri': 'http://www.opencoesione.gov.it/iscrizione-newsletter'
        }
        contact_dict = {
            'email': self.cleaned_data.get('email', ''),
            'first_name': self.cleaned_data.get('first_name',''),
            'last_name': self.cleaned_data.get('last_name',''),
        }
        iscrizione_dict = {
            'title': '',
            'role': '',
            'user_type': self.cleaned_data.get('user_type', ''),
            'notes': self.cleaned_data.get('notes', ''),
        }

        IscrizioneManager.add_iscrizione_complessa(
            source_dict, contact_dict, iscrizione_dict,
        )

        html_content = render_to_string('mail/iscrizione.html', dict(contact_dict.items() + iscrizione_dict.items()))
        text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.

        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives('Notifica iscrizione alla newsletter di opencoesione.gov.it', text_content, settings.EMAIL_DEFAULT_FROM, settings.CONTACTS_EMAIL)
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
