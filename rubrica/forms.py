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
    email = forms.EmailField(label="Email *")
    title = forms.CharField(max_length=80, label='Qualifica', required=False)
    role = forms.CharField(max_length=80, label='Ruolo', required=False)
    user_type = forms.TypedChoiceField(choices=USER_TYPES, label='Tipologia di utente *', empty_value= '-----')
    notes = forms.CharField(widget=forms.Textarea, label='Note', required=False, help_text="Note su questo contatto")
    privacy = forms.BooleanField(required=True, label='Autorizzazione utilizzo dati personali *')

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

        # source is fixed for this website
        source, created = Fonte.objects.get_or_create(
            slug='opencoesione',
            defaults={
                'name': 'Opencoesione',
                'uri': 'http://www.opencoesione.gov.it/iscrizione-newsletter'
            }
        )
        contact, created = Contatto.objects.get_or_create(
            email=email,
            defaults=contatto_defaults_dict
        )

        i = Iscrizione(**iscrizione_dict)
        i.contact = contact
        i.source = source
        i.save()




