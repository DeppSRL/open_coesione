# coding=utf-8
from __future__ import absolute_import
from territori.models import Territorio
from open_coesione.widgets import AggregateWidget
from widgets.models import Widget
from django import forms
from api.query import request


__author__ = 'daniele'


class TerritorioWidget(AggregateWidget):

    code = 'territorio'
    title = 'Territorio'

    EXCLUDE_TITLE = True
    INITIAL_TOPIC = 'roma-comune', 'Roma'
    API_PATH = 'territori/'
    API_TOPIC = 'territorio'

    def get_title(self):
        return "{0}: {1}".format(self.title, Territorio.objects.get(slug=self.get_topic()).denominazione)


#class TerritorioWidget(Widget):
#
#    code = 'territori'
#    title = "Territori"
#
#    COMPONENTS = (
#        ('temi', 'Classificazione per tema'),
#        ('nature', 'Visualizza le nature'),
#        ('top_progetti', 'Visualizza i 5 progetti più finanziati'),
#        ('progetti_conclusi', 'Visualizza gli ultimi 5 progetti conclusi'),
#    )
#
#    def get_context_data(self):
#        context = super(TerritorioWidget, self).get_context_data()
#        if self.get_form().is_valid():
#            cleaned_data = self.get_form().cleaned_data
#            url = 'aggregati'
#            territorio = cleaned_data.get('territorio', None)
#            if territorio:
#                url += '/territori/{0}'.format(territorio)
#            context.update(request(url))
#
#            if 'top_progetti' in cleaned_data['component_set']:
#                data = {'order_by': '-costo', 'page_size': 5}
#                if territorio:
#                    data['territorio'] = territorio
#                context.update({'top_progetti': request('progetti', **data)})
#
#            if 'progetti_conclusi' in cleaned_data['component_set']:
#                data = {'order_by': '-data_fine_effettiva', 'page_size': 5}
#                if territorio:
#                    data['territorio'] = territorio
#                context.update({'progetti_conclusi': request('progetti', **data)})
#
#        return context
#
#    def build_form_fields(self, form):
#        #form.fields['tematizzazione'] = forms.ChoiceField(
#        #    label='Tematizzazione',
#        #    initial='costi',
#        #    choices=(('costi', 'Costi'), ('pagamenti', 'Pagamenti'), ('progetti', 'Progetti'))
#        #)
#        form.fields['territorio'] = forms.CharField(initial='roma-comune')
#        form.fields['component_set'] = forms.MultipleChoiceField(
#            label="Componenti da visualizzare", required=False, choices=self.COMPONENTS,
#            widget=forms.CheckboxSelectMultiple)
#
#    def get_initial(self):
#        initial = super(TerritorioWidget, self).get_initial()
#        initial.update({
#            'title': 'Roma',
#            'territorio': 'roma-comune',
#            'component_set': [x[0] for x in self.COMPONENTS],
#        })
#        return initial
