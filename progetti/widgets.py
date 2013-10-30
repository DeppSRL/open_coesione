# coding=utf-8
from __future__ import absolute_import
from django import forms
from open_coesione.widgets import AggregateWidget
from progetti.models import Tema, ClassificazioneAzione
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

    def get_context_data(self):
        context = super(ProgettoWidget, self).get_context_data()
        context['progetto'] = 1
        return context