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


class ProgettoWidget(Widget):

    code = "progetto"
    title = "Progetto"

    def get_context_data(self):
        context = super(ProgettoWidget, self).get_context_data()
        if self.get_form().is_valid():
            cleaned_data = self.get_form().cleaned_data
            context['progetto'] = request('progetti/{0}'.format(cleaned_data['progetto']))
        return context

    def build_form_fields(self, form):
        form.fields['progetto'] = forms.CharField()
        super(ProgettoWidget, self).build_form_fields(form)
        del form.fields['title']

    def get_initial(self):
        initial = super(ProgettoWidget, self).get_initial()
        initial['progetto'] = Progetto.objects.order_by('-fin_totale_pubblico')[1].slug
        return initial


class ProgettiWidget(Widget):

    code = 'progetti'
    title = "Progetti"

    def get_context_data(self):
        context = super(ProgettiWidget, self).get_context_data()
        if self.get_form().is_valid():
            cleaned_data = self.get_form().cleaned_data
            order_by = cleaned_data['order_by']
            if cleaned_data['desc']:
                order_by = '-{0}'.format(order_by)
            context['progetti'] = request('progetti', order_by=order_by)
        return context

    def build_form_fields(self, form):
        form.fields['order_by'] = forms.ChoiceField(label='Ordinamento', choices=(
            ('costo', 'Costo totale'),
            ('pagamento', 'Pagamenti totali'),
            ('perc_pagamento', 'Percentuale pagamenti'),
            ('data_inizio_effettiva', 'Data di inizio'),
            ('data_fine_effettiva', 'Data di fine'),
        ))
        form.fields['desc'] = forms.BooleanField(label='Decrescente', required=False)
        super(ProgettiWidget, self).build_form_fields(form)

    def get_initial(self):
        initial = super(ProgettiWidget, self).get_initial()
        initial['desc'] = True
        initial['order_by'] = 'costo'
        return initial