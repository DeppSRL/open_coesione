# coding=utf-8
from __future__ import absolute_import
from widgets.models import Widget
from api.query import request
from open_coesione.widgets import AggregateWidget
from soggetti.models import Soggetto


__author__ = 'daniele'


class SoggettoWidget(AggregateWidget):

    code = "soggetto"
    name = "Soggetto"
    title = "Soggetto"
    API_TOPIC = 'soggetto'

    _COMPONENTS = (
        ('temi', 'Classificazione per tema'),
        ('nature', 'Visualizza le nature'),
        ('top_progetti', 'Visualizza i 5 progetti più finanziati'),
        ('territori_piu_finanziati_pro_capite', 'Visualizza i 5 comuni con più finanziamenti procapite'),
        ('top_collaboratori', 'Visualizza i 5 soggetti con cui collabora di più'),
    )

    INITIAL_TOPIC = 'miur-97429780584', 'MIUR'

    def get_context_data(self):
        context = Widget.get_context_data(self)
        if self.is_valid():
            cleaned_data = self.get_data()
            context['soggetto'] = request('soggetti/{0}'.format(cleaned_data['soggetto']))
            context['aggregati'] = context['soggetto'].pop('aggregati')
            context['top_progetti'] = {'results': context['soggetto'].pop('top_progetti')}
            context['top_collaboratori'] = {'results': context['soggetto'].pop('top_collaboratori')}
            context['territori_piu_finanziati_pro_capite'] = {
                'results': context['soggetto'].pop('territori_piu_finanziati_pro_capite')
            }
        return context

    def get_title(self):
        return '{0}: {1}'.format(self.title, Soggetto.objects.get(slug=self.get_topic()).denominazione)
