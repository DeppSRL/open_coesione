# coding=utf-8
from __future__ import absolute_import
from datetime import date
from decimal import Decimal
from django import forms
from open_coesione.widgets import AggregateWidget
from progetti.models import Tema, ClassificazioneAzione, Progetto, Ruolo
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

            # retrieve classificazione_azione.classificazione_superiore
            nature = request('nature')
            for natura in nature['results']:
                if natura['codice'] == context['progetto']['classificazione_azione']['classificazione_superiore']:
                    context['progetto']['classificazione_azione']['classificazione_superiore'] = natura
                    break

            # retrieve tema.tema_superiore
            temi = request('temi')
            for tema in temi['results']:
                if tema['codice'] == context['progetto']['tema']['tema_superiore']:
                    context['progetto']['tema']['tema_superiore'] = tema
                    break

            # collect roles
            context['progetto'].update({'attuatori': [], 'programmatori': []})
            for ruolo in context['progetto']['ruolo_set']:
                if ruolo['codice'] == Ruolo.RUOLO.programmatore:
                    context['progetto']['programmatori'].append(ruolo)
                elif ruolo['codice'] == Ruolo.RUOLO.attuatore:
                    context['progetto']['attuatori'].append(ruolo)
                #TODO: add other roles

            # re-create classificazione_qns tree
            qsn = context['progetto']['classificazione_qsn']
            qsn_parent = qsn_parent_parent = None
            qsn_root_code = qsn['codice'].split('.')[0]
            classificazioni = request('classificazioni')
            for classificazione in classificazioni['results']:
                if classificazione['codice'] == qsn['classificazione_superiore']:
                    qsn_parent = classificazione
                elif classificazione['codice'] == qsn_root_code:
                    qsn_parent_parent = classificazione
            qsn['classificazione_superiore'] = qsn_parent
            qsn_parent['classificazione_superiore'] = qsn_parent_parent

            # re-create programma_asse_obiettivo tree
            prog = context['progetto']['programma_asse_obiettivo']
            prog_parent = prog_parent_parent = None
            prog_root_code = prog['classificazione_superiore'].split('/')[0]
            programmi = request('programmi?codice={0},{1}'.format(
                prog['classificazione_superiore'],
                prog_root_code
            ))
            for programma in programmi['results']:
                if programma['codice'] == prog['classificazione_superiore']:
                    prog_parent = programma
                elif programma['codice'] == prog_root_code:
                    prog_parent_parent = programma
            prog['classificazione_superiore'] = prog_parent
            prog_parent['classificazione_superiore'] = prog_parent_parent

            # cast data and ammontare of pagamenti
            for pagamento in context['progetto']['pagamenti']:
                pagamento['ammontare'] = Decimal(pagamento['ammontare'])
                pagamento['data'] = date(*map(int, pagamento['data'].split('-')))

            # update ultimo_aggiornamento
            if context['progetto']['data_aggiornamento']:
                context['progetto']['ultimo_aggiornamento'] = date(*map(int, context['progetto']['data_aggiornamento'].split('-')))
            elif context['progetto']['pagamenti']:
                context['progetto']['ultimo_aggiornamento'] = max(*[p['data'] for p in context['progetto']['pagamenti']])

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