# coding=utf-8
from django import forms
from progetti.models import SegnalazioneProgetto

class DescrizioneProgettoForm(forms.ModelForm):

    come_lo_conosci_descrizione = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = SegnalazioneProgetto


#
#    TIPOLOGIE = (
#        ('FINAZIATORE', "Faccio parte dell'amministrazione che programma e finanzia" ),
#        ('ATTUATORE', "Faccio parte dell'organizzazione che gestisce l'attuazione del progetto" ),
#        ('REALIZZATORE', "Lavoro / ho lavorato per la realizzazione del progetto"),
#        ('OSSERVATORE', "Abito lì vicino"),
#        ('ALTRO', "conosco il progetto per un altro motivo"),
#    )
#
#    come_lo_conosci = forms.ChoiceField(choices=TIPOLOGIE, required=True)
#
#    cup = forms.CharField(max_length=15, min_length=3, required=True)
#    organizzazione = forms.CharField(max_length=255, required=False)
#    email = forms.EmailField(required=True)
#    descrizione = forms.CharField(widget=forms.Textarea, required=True)
#
#    # optional fields
#    risultati_conseguiti = forms.CharField(widget=forms.Textarea, required=False)
#    effetti_sul_territorio = forms.CharField(widget=forms.Textarea, required=False)
#    cosa_piace = forms.CharField(widget=forms.Textarea, required=False)
#    cosa_non_piace = forms.CharField(widget=forms.Textarea, required=False)
#    quanto_utile = forms.CharField(widget=forms.Textarea, required=False)
#    come_migliorare = forms.CharField(widget=forms.Textarea, required=False)
