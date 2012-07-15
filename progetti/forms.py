from django import forms
from progetti.models import SegnalazioneProgetto

class DescrizioneProgettoForm(forms.ModelForm):

    #come_lo_conosci_descrizione = forms.CharField(widget=forms.Textarea, required=False)

    def send_mail(self):
        pass

    class Meta:
        model = SegnalazioneProgetto
