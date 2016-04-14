# -*- coding: utf-8 -*-
from haystack.indexes import *
from haystack import site
from progetti.models import Progetto
import datetime


class ProgettoIndex(SearchIndex):
    text = CharField(document=True, use_template=True, stored=False)

    soggetto = MultiValueField(stored=False)

    territorio_tipo = MultiValueField(stored=False)
    territorio_com = MultiValueField(stored=False)
    territorio_prov = MultiValueField(stored=False)
    territorio_reg = MultiValueField(stored=False)

    fonte_fin = MultiValueField(stored=False)
    classificazione_cup = CharField(stored=False)

    is_active = FacetBooleanField(model_attr='active_flag', stored=False)
    natura = FacetCharField(stored=False)
    tema = FacetCharField(stored=False)
    fonte = FacetMultiValueField(stored=False)
    stato_progetto = FacetCharField(model_attr='stato_progetto', stored=False)

    data_inizio = FacetDateField(stored=False)
    costo = FacetFloatField(model_attr='fin_totale_pubblico', stored=False)
    perc_pagamento = FacetFloatField(stored=False)

    def prepare_soggetto(self, obj):
        return ['{}|{}'.format(r['soggetto__slug'], r['ruolo']) for r in obj.ruolo_set.values('soggetto__slug', 'ruolo')]

    def prepare_territorio_tipo(self, obj):
        return [t.territorio for t in obj.territori]

    def prepare_territorio_prov(self, obj):
        return [t.cod_prov for t in obj.territori]

    def prepare_territorio_com(self, obj):
        return [t.cod_com for t in obj.territori]

    def prepare_territorio_reg(self, obj):
        return [t.cod_reg for t in obj.territori]

    def prepare_classificazione_cup(self, obj):
        if obj.classificazione_oggetto:
            return obj.classificazione_oggetto.codice
        else:
            return 'ND'

    def prepare_fonte_fin(self, obj):
        return [f.pk for f in obj.fonti_fin]

    def prepare_natura(self, obj):
        if obj.classificazione_azione:
            codice = obj.classificazione_azione.codice.split('.')[0]
            if codice != ' ':
                return codice
            else:
                return 'ND'
        else:
            return 'ND'

    def prepare_tema(self, obj):
        if obj.tema:
            return obj.tema.codice.split('.')[0]
        else:
            return 'ND'

    def prepare_fonte(self, obj):
        return [f.codice for f in obj.fonti]

    def prepare_data_inizio(self, obj):
        if obj.data_inizio_effettiva:
            return obj.data_inizio_effettiva
        else:
            return datetime.datetime.strptime('19700101', '%Y%m%d')

    def prepare_perc_pagamento(self, obj):
        return obj.percentuale_pagamenti

    def index_queryset(self):
        related = ['territorio_set', 'programma_asse_obiettivo__classificazione_superiore__classificazione_superiore', 'programma_linea_azione__classificazione_superiore__classificazione_superiore', 'classificazione_azione', 'classificazione_oggetto', 'tema', 'fonte_set']
        return self.model.fullobjects.select_related(*related).prefetch_related(*related)


site.register(Progetto, ProgettoIndex)
