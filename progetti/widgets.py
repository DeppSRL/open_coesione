# coding=utf-8
from __future__ import absolute_import
from django import forms
from open_coesione.widgets import AggregateWidget
from progetti.models import Tema, ClassificazioneAzione
from territori.widgets import TerritorioWidget
from api.query import request

__author__ = 'daniele'



#class TemaWidget(TerritorioWidget):
#
#    code = 'tema'
#    title = "Tema"
#
#    COMPONENTS = (
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
#            tema = cleaned_data.get('tema', None)
#            if tema:
#                url += '/temi/{0}'.format(tema)
#            context.update(request(url))
#
#            if 'top_progetti' in cleaned_data['component_set']:
#                data = {'order_by': '-costo', 'page_size': 5}
#                if tema:
#                    data['tema'] = tema
#                context.update({'top_progetti': request('progetti', **data)})
#
#            if 'progetti_conclusi' in cleaned_data['component_set']:
#                data = {'order_by': '-data_fine_effettiva', 'page_size': 5}
#                if tema:
#                    data['tema'] = tema
#                context.update({'progetti_conclusi': request('progetti', **data)})
#
#        return context
#
#    def build_form_fields(self, form):
#        super(TerritorioWidget, self).build_form_fields(form)
#        form.fields['tema'] = forms.ChoiceField(choices=[(t.slug, t.short_label) for t in Tema.objects.principali()])
#        form.fields['component_set'] = forms.MultipleChoiceField(
#            label="Componenti da visualizzare", required=False, choices=self.COMPONENTS,
#            widget=forms.CheckboxSelectMultiple)
#
#    def get_initial(self):
#        initial = super(TemaWidget, self).get_initial()
#        initial.update({
#            'title': 'Agenda digitale',
#            'tema': 'agenda-digitale',
#        })
#        del initial['territorio']
#        return initial


class TemaWidget(AggregateWidget):

    code = 'tema'
    title = 'Tema'

    EXCLUDE_TITLE = True
    EXCLUDED_COMPONENT = 'temi'
    API_PATH = 'temi/'
    API_TOPIC = 'tema'

    def get_topic_choices(self):
        if not hasattr(self, '_topic_choices'):
            self._topic_choices = [(t.slug, t.short_label) for t in Tema.objects.principali()]
        return self._topic_choices


class NaturaWidget(AggregateWidget):

    code = 'natura'
    title = 'Natura'

    EXCLUDE_TITLE = True
    EXCLUDED_COMPONENT = 'nature'
    API_PATH = 'nature/'
    API_TOPIC = 'natura'

    def get_topic_choices(self):
        if not hasattr(self, '_topic_choices'):
            self._topic_choices = [(t.slug, t.short_label) for t in ClassificazioneAzione.objects.nature()]
        return self._topic_choices
