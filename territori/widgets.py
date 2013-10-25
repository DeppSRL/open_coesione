from __future__ import absolute_import
from widgets.models import Widget
from django import forms
from api.query import request


__author__ = 'daniele'


class TerritoriWidget(Widget):

    code = 'territori'
    title = "Territori"

    def get_context_data(self):
        context = super(TerritoriWidget, self).get_context_data()
        if self.get_form().is_valid():
            cleaned_data = self.get_form().cleaned_data
            url = 'aggregati'
            if 'territorio' in cleaned_data:
                url += '/territori/{0}'.format(cleaned_data.get('territorio'))
            context.update(request(url))
        return context

    def build_form(self):
        form = super(TerritoriWidget, self).build_form()
        form.fields['tematizzazione'] = forms.ChoiceField(
            label='Tematizzazione',
            initial='costi',
            choices=(('costi', 'Costi'), ('pagamenti', 'Pagamenti'), ('progetti', 'Progetti'))
        )
        form.fields['territorio'] = forms.CharField(initial='ambito-nazionale-nazionale')
        form.fields['show_temi'] = forms.BooleanField(label="Visualizza i temi", initial=True, required=False)
        form.fields['show_nature'] = forms.BooleanField(label="Visualizza i temi", initial=True, required=False)
        return form
