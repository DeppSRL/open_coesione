# coding=utf-8
from __future__ import absolute_import
from django import forms
from open_coesione.widgets import AggregateWidget
from progetti.models import Tema, ClassificazioneAzione, Progetto
from territori.widgets import TerritorioWidget
from api.query import request
from widgets.models import Widget

__author__ = 'daniele'


class TemaWidget(AggregateWidget):

    code = 'tema'
    name = 'Tema'

    EXCLUDED_COMPONENT = 'temi'
    API_PATH = 'temi/'
    API_TOPIC = 'tema'

    def get_topic_choices(self):
        if not hasattr(self, '_topic_choices'):
            self._topic_choices = [(t.slug, t.short_label) for t in Tema.objects.principali()]
        return self._topic_choices


class NaturaWidget(AggregateWidget):

    code = 'natura'
    name = 'Natura'

    EXCLUDED_COMPONENT = 'nature'
    API_PATH = 'nature/'
    API_TOPIC = 'natura'

    def get_topic_choices(self):
        if not hasattr(self, '_topic_choices'):
            self._topic_choices = [(t.slug, t.short_label) for t in ClassificazioneAzione.objects.nature()]
        return self._topic_choices


class ProgettoWidget(Widget):

    code = "progetto"
    name = "Progetto"

    def get_context_data(self):
        context = super(ProgettoWidget, self).get_context_data()
        if self.is_valid():
            cleaned_data = self.get_data()
            context['progetto'] = request('progetti/{0}'.format(cleaned_data['progetto']))
        return context

    def get_form(self):
        form = super(ProgettoWidget, self).get_form()
        form.fields['progetto'] = forms.CharField()
        return form

    def get_initial(self):
        initial = super(ProgettoWidget, self).get_initial()
        initial['progetto'] = Progetto.objects.order_by('-fin_totale_pubblico')[1].slug
        return initial


class ProgettiWidget(Widget):

    code = 'progetti'
    name = "Progetti"

    def get_context_data(self):
        context = super(ProgettiWidget, self).get_context_data()
        if self.is_valid():
            cleaned_data = self.get_data()
            order_by = cleaned_data['order_by']
            if cleaned_data['desc']:
                order_by = '-{0}'.format(order_by)
            context['progetti'] = request('progetti', order_by=order_by)
        return context

    def get_form(self):
        form = super(ProgettiWidget, self).get_form()
        form.fields['order_by'] = forms.ChoiceField(label='Ordinamento', choices=(
            ('costo', 'Costo totale'),
            ('pagamento', 'Pagamenti totali'),
            ('perc_pagamento', 'Percentuale pagamenti'),
            ('data_inizio_effettiva', 'Data di inizio'),
            ('data_fine_effettiva', 'Data di fine'),
        ))
        form.fields['desc'] = forms.BooleanField(label='Decrescente', required=False)
        return form

    def get_initial(self):
        initial = super(ProgettiWidget, self).get_initial()
        initial['desc'] = True
        initial['order_by'] = 'costo'
        return initial