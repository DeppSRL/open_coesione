from django import forms
from captcha.fields import ReCaptchaField
from progetti.models import SegnalazioneProgetto


class DescrizioneProgettoForm(forms.ModelForm):

    captcha = ReCaptchaField(label='Controllo anti-spam')
    #come_lo_conosci_descrizione = forms.CharField(widget=forms.Textarea, required=False)
    #authorization = forms.BooleanField(label='', required=True, help_text= 'Testo Autorizzazione', initial=True)

    def __init__(self, *args, **kwargs):

        super(DescrizioneProgettoForm, self).__init__(*args, **kwargs)

        self.fields['is_cipe'].widget = forms.HiddenInput()

    def send_mail(self):
        pass

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
