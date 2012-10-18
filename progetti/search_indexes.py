import datetime
from haystack.indexes import *
from haystack import site
from oc_search.fields import L10NCharField

from progetti.models import Progetto, Ruolo

from django.utils.translation import activate
from django.conf import settings

# user RealTimeSearchIndex once online

class ProgettoIndex(SearchIndex):
    clp = CharField(model_attr='codice_locale')
    cup = CharField(model_attr='cup', null=True)
    titolo = CharField(model_attr='titolo_progetto')
    descrizione = CharField(model_attr='descrizione', null=True)
    fonte_descr = CharField(model_attr='fonte__descrizione', null=True)
    tema_descr = CharField(model_attr='tema__tema_superiore__descrizione', null=True)
    natura_descr = CharField(model_attr='classificazione_azione__classificazione_superiore__descrizione', null=True)
    fin_totale_pubblico = FloatField(model_attr='fin_totale_pubblico', null=True)
    fin_ue = FloatField(model_attr='fin_ue', null=True)
    fin_stato_fondo_rotazione = FloatField(model_attr='fin_stato_fondo_rotazione', null=True)
    fin_stato_fsc = FloatField(model_attr='fin_stato_fsc', null=True)
    fin_stato_altri_provvedimenti = FloatField(model_attr='fin_stato_altri_provvedimenti', null=True)
    fin_regione = FloatField(model_attr='fin_regione', null=True)
    fin_provincia = FloatField(model_attr='fin_provincia', null=True)
    fin_comune = FloatField(model_attr='fin_comune', null=True)
    fin_altro_pubblico = FloatField(model_attr='fin_altro_pubblico', null=True)
    fin_stato_estero = FloatField(model_attr='fin_stato_estero', null=True)
    fin_privato = FloatField(model_attr='fin_privato', null=True)
    fin_da_reperire = FloatField(model_attr='fin_da_reperire', null=True)
    pagamento = FloatField(model_attr='pagamento', null=True)
    fondo = CharField(model_attr='fondo_comunitario', null=True)

    data_inizio_prevista = DateField(model_attr='data_inizio_prevista', null=True)
    data_fine_prevista = DateField(model_attr='data_fine_prevista', null=True)
    data_inizio_effettiva = DateField(model_attr='data_inizio_effettiva', null=True)
    data_fine_effettiva = DateField(model_attr='data_fine_effettiva', null=True)
    data_aggiornamento = DateField(model_attr='data_aggiornamento', null=True)

    sogg_programmatori = MultiValueField(stored=True)

    text = CharField(document=True, use_template=True)
    territorio_com = MultiValueField(indexed=True, stored=True)
    territorio_prov = MultiValueField(indexed=True, stored=True)
    territorio_reg = MultiValueField(indexed=True, stored=True)
    soggetto = MultiValueField(indexed=True, stored=True)

    # faceting fields
    natura = FacetCharField( )
    tema = FacetCharField( )
    fonte = FacetCharField( model_attr='fonte__codice' )
    data_inizio = FacetDateField()
    costo = FacetFloatField(model_attr='fin_totale_pubblico')

    # search result format is pre-rendered during index phase
    rendered = L10NCharField(use_template=True, indexed=False)

    def prepare_natura(self, obj):
        codice = obj.classificazione_azione.codice.split('.')[0]
        if codice != ' ':
            return codice
        else:
            return 'ND'

    def prepare_tema(self, obj):
        return obj.tema.codice.split('.')[0]

    def prepare_territorio_reg(self, obj):
        return [c['cod_reg'] for c in obj.territori.values('cod_reg').distinct()]

    def prepare_territorio_prov(self, obj):
        return [c['cod_prov'] for c in obj.territori.values('cod_prov').distinct()]

    def prepare_territorio_com(self, obj):
        return [c['cod_com'] for c in obj.territori.values('cod_com').distinct()]

    def prepare_soggetto(self, obj):
        return [s['slug'] for s in obj.soggetto_set.values('slug').distinct()]

    def prepare_sogg_programmatori(self, obj):
        return [s['soggetto__denominazione'] for s in obj.ruolo_set.filter(ruolo=Ruolo.RUOLO.programmatore).values('soggetto__denominazione')]

    def prepare_data_inizio(self, obj):
        if obj.data_inizio_effettiva:
            return obj.data_inizio_effettiva
        else:
            return obj.data_inizio_prevista

site.register(Progetto, ProgettoIndex)