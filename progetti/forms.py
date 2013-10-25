# -*- coding: utf8 -*-

from django import forms
from captcha.fields import ReCaptchaField
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.datastructures import SortedDict
from progetti.models import SegnalazioneProgetto, Progetto


class DescrizioneProgettoForm(forms.ModelForm):

    captcha = ReCaptchaField(label='Controllo anti-spam')

    def __init__(self, *args, **kwargs):
        super(DescrizioneProgettoForm, self).__init__(*args, **kwargs)
        self.fields['is_cipe'].widget = forms.HiddenInput()

    def send_mail(self):
        from django.core.mail import EmailMultiAlternatives
        from django.utils.html import strip_tags
        from django.template.loader import render_to_string

        come_lo_conosci = self.cleaned_data.get('come_lo_conosci', '')
        if come_lo_conosci == SegnalazioneProgetto.TIPOLOGIA_ALTRO:
            come_lo_conosci = self.cleaned_data.get('come_lo_conosci_altro', '')
        cup = self.cleaned_data.get('cup', '')

        domain = Site.objects.get(pk=settings.SITE_ID).domain

        segnalazione = self.instance
        segnalazione_url = "http://{0}/admin/progetti/segnalazioneprogetto/{1}".format(domain, segnalazione.pk)

        progetto_url = ''
        progetto = Progetto.objects.get(cup=cup)
        if progetto is not None:
            progetto_url = "http://{0}{1}".format(domain, progetto.get_absolute_url())

        values_dict = {
            'cup': cup,
            'utente': self.cleaned_data.get('utente',''),
            'email': self.cleaned_data.get('email',''),
            'progetto_url': progetto_url,
            'segnalazione_url': segnalazione_url,
            'organizzazione' : self.cleaned_data.get('organizzazione',''),
            'descrizione': {
                'label': 'Il progetto',
                'value': self.cleaned_data.get('descrizione','')
            },
            'come_lo_conosci': {
                'label': 'Come lo conosci',
                'value': come_lo_conosci,
            },
            'come_migliorare': {
                'label': 'Come si potrebbe migliorare',
                'value': self.cleaned_data.get('come_migliorare','')
            },
            'risultati_conseguiti': {
                'label': 'Quali i risultati conseguiti',
                'value': self.cleaned_data.get('risultati_conseguiti','')
            },
            'effetti_sul_territorio': {
                'label': 'Quali gli effetti sul territorio',
                'value': self.cleaned_data.get('effetti_sul_territorio','')
            },
            'cosa_piace': {
                'label': 'Cosa ti è piaciuto di più',
                'value': self.cleaned_data.get('cosa_piace','')
            },
            'cosa_non_piace': {
                'label': 'Cosa ti è piaciuto di meno',
                'value': self.cleaned_data.get('cosa_non_piace','')
            },
            'quanto_utile': {
                'label': 'Per cosa è stato utile il progetto',
                'value': self.cleaned_data.get('quanto_utile','')
            },
        }


        html_content = render_to_string('mail/segnalazione.html', values_dict)
        text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.

        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(
            'Notifica segnalazione progetto da opencoesione.gov.it',
            text_content, self.cleaned_data.get('email'), settings.CONTACTS_EMAIL)
        msg.attach_alternative(html_content, "text/html")
        msg.send()


    def clean(self):

        cleaned_data = super(DescrizioneProgettoForm, self).clean()

        come_lo_conosce = cleaned_data.get("come_lo_conosci")

        if come_lo_conosce == SegnalazioneProgetto.TIPOLOGIA_ALTRO:
            # We know these are not in self._errors now (see discussion below)
            if not str(cleaned_data.get("come_lo_conosci_altro")).strip():
                self._errors["come_lo_conosci"] = self.error_class([u"Hai selezionato un altro motivo, inserisci la descrizione qui sotto."])
                self._errors["come_lo_conosci_altro"] = self.error_class([u"Descrizione obbligatoria."])
                # These fields are no longer valid. Remove them from the
                # cleaned data.
                del cleaned_data["come_lo_conosci"]
                del cleaned_data["come_lo_conosci_altro"]

        # Always return the full collection of cleaned data.
        return cleaned_data

    class Meta:
        model = SegnalazioneProgetto
        exclude = ('pubblicato',)
