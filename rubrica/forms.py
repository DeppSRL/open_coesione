# coding=utf-8
from django import forms
from rubrica.models import Contatto, Iscrizione, Fonte


class NLContactForm(forms.Form):
    """
    The custom form to subscribe to the Newsletter.
    """
    USER_TYPES = ((u'', u'--------------'),) + tuple(Iscrizione.TYPES)

    first_name = forms.CharField(max_length= 80, label='Nome', required=False)
    last_name = forms.CharField(max_length= 80, label='Cognome', required=False)
    email = forms.EmailField()
    title = forms.CharField(max_length=80, label='Qualifica', required=False)
    role = forms.CharField(max_length=80, label='Ruolo', required=False)
    user_type = forms.TypedChoiceField(choices=USER_TYPES, label='Tipologia di utente', empty_value= '-----')
    notes = forms.CharField(widget=forms.Textarea, label='Note', required=False)
    privacy = forms.BooleanField(required=True, help_text="Possiamo rivendere questi tuoi dati a chi ci pare?")

    def execute(self):
        email = self.cleaned_data.get('email','')
        contatto_defaults_dict = {
            'first_name': self.cleaned_data.get('first_name',''),
            'last_name': self.cleaned_data.get('last_name',''),
        }
        iscrizione_dict = {
            'title': self.cleaned_data.get('title', ''),
            'role': self.cleaned_data.get('role', ''),
            'user_type': self.cleaned_data.get('user_type', ''),
            'notes': self.cleaned_data.get('notes', ''),
        }

        # TODO: change this, must be resilient to change to the URL
        source = Fonte.objects.get(uri='http://www.opencoesione.gov.it/iscrizione-newsletter')

        contact, created = Contatto.objects.get_or_create(
            email=email,
            defaults=contatto_defaults_dict
        )

        i = Iscrizione(**iscrizione_dict)
        i.contact = contact
        i.source = source
        i.save()




