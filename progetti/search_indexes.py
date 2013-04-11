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

    soggetti_programmatori = MultiValueField(stored=True)
    soggetti_attuatori = MultiValueField(stored=True)

    territori = MultiValueField(stored=True)
    ambiti_territoriali = MultiValueField(stored=True)

    text = CharField(document=True, use_template=True)
    territorio_tipo = MultiValueField(indexed=True, stored=True)
    territorio_com = MultiValueField(indexed=True, stored=True)
    territorio_prov = MultiValueField(indexed=True, stored=True)
    territorio_reg = MultiValueField(indexed=True, stored=True)

    soggetto = MultiValueField(indexed=True, stored=True)
    fonte_fin = CharField(indexed=True, stored=False)

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

    def prepare_territorio_tipo(self, obj):
        return [t.territorio for t in obj.territori]

    def prepare_territorio_reg(self, obj):
        return [t.cod_reg for t in obj.territori]

    def prepare_territorio_prov(self, obj):
        return [t.cod_prov for t in obj.territori]

    def prepare_territorio_com(self, obj):
        return [t.cod_com for t in obj.territori]

    def prepare_soggetto(self, obj):
        return [s['slug'] for s in obj.soggetto_set.values('slug').distinct()]

    def prepare_fonte_fin(self, obj):
        return obj.fonte_fin.pk

    def prepare_soggetti_programmatori(self, obj):
        return [s['soggetto__denominazione'] for s in obj.ruolo_set.filter(ruolo=Ruolo.RUOLO.programmatore).values('soggetto__denominazione')]

    def prepare_soggetti_attuatori(self, obj):
        return [s['soggetto__denominazione'] for s in obj.ruolo_set.filter(ruolo=Ruolo.RUOLO.attuatore).values('soggetto__denominazione')]

    def prepare_territori(self, obj):
        return set([t.nome_con_provincia for t in obj.territori])

    def prepare_ambiti_territoriali(self, obj):
        return set([t.ambito_territoriale for t in obj.territori])

    def prepare_data_inizio(self, obj):
        if obj.data_inizio_effettiva:
            return obj.data_inizio_effettiva
        elif obj.data_inizio_prevista:
            return obj.data_inizio_prevista
        else:
            return datetime.datetime.strptime('19700101', '%Y%m%d')


site.register(Progetto, ProgettoIndex)