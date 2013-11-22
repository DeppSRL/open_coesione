# coding=utf-8
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.cache import cache
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.db.models import Count, Sum
from django.core.urlresolvers import reverse
from oc_search.forms import RangeFacetedSearchForm
from oc_search.mixins import FacetRangeCostoMixin, FacetRangeNProgettiMixin, TerritorioMixin
from oc_search.views import ExtendedFacetedSearchView
from open_coesione.views import AggregatoView, AccessControlView, cached_context
from progetti.models import Progetto, Tema, ClassificazioneAzione, Ruolo
from soggetti.models import Soggetto
from territori.models import Territorio

import logging

class SoggettoSearchView(AccessControlView, ExtendedFacetedSearchView, FacetRangeCostoMixin, FacetRangeNProgettiMixin, TerritorioMixin):
    """
    This view allows faceted search and navigation of a progetto.

    It extends an extended version of the basic FacetedSearchView,

    It also extends FacetRangeCostoMixin and FacetRangeNProgettiMixin, to handle
    custom facets on range fields `costo` and `n_progetti`.
    """
    __name__ = 'SoggettoSearchView'

    COST_RANGES = {
        '0-0TO100K':   {'qrange': '[* TO 100000]',             'r_label': 'fino a 100.000 &euro;'},
        '1-100KTO1M':  {'qrange': '[100000.1 TO 1000000]',     'r_label': 'da 100.000 a 1 mil. di &euro;'},
        '2-1MTO10M':   {'qrange': '[1000001 TO 10000000]',     'r_label': 'da 1 mil. a 10 mil. di &euro;'},
        '3-10MTO100M': {'qrange': '[10000001 TO 100000000]',   'r_label': 'da 10 mil. a 100 mil. di &euro;'},
        '4-100MTO1G':  {'qrange': '[100000010 TO 1000000000]', 'r_label': 'da 100 mil. a 1 mld. di &euro;'},
        '5-1GTOINF':   {'qrange': '[1000000001 TO *]',         'r_label': 'oltre 1 mld. di &euro;'},
    }
    N_PROGETTI_RANGES = {
        '0-0TO10':     {'qrange': '[* TO 10]',       'r_label': 'fino a 10' },
        '1-10TO100':   {'qrange': '[11 TO 100]',     'r_label': 'da 10 a 100' },
        '2-100TO1K':   {'qrange': '[101 TO 1000]',   'r_label': 'da 100 a 1.000' },
        '3-1KTO10K':   {'qrange': '[1001 TO 10000]', 'r_label': 'da 1.000 a 10.000' },
        '4-10KTOINF':  {'qrange': '[10001 TO *]',    'r_label': 'oltre 10.000' },
    }


    def __init__(self, *args, **kwargs):
        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = RangeFacetedSearchForm

        super(SoggettoSearchView, self).__init__(*args, **kwargs)

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        return super(SoggettoSearchView, self).build_form(form_kwargs)


    def _get_extended_selected_facets(self):
        """
        modifies the extended_selected_facets, adding correct labels for this view
        works directly on the extended_selected_facets dictionary
        """
        extended_selected_facets = super(SoggettoSearchView, self)._get_extended_selected_facets()

        # these comes from the Mixins
        extended_selected_facets = self.add_costo_extended_selected_facets(extended_selected_facets)
        extended_selected_facets = self.add_n_progetti_extended_selected_facets(extended_selected_facets)
        extended_selected_facets = self.add_territorio_extended_selected_facets(extended_selected_facets)

        return extended_selected_facets

    def extra_context(self):
        """
        Add extra content here, when needed
        """
        extra = super(SoggettoSearchView, self).extra_context()

        territorio_com = self.request.GET.get('territorio_com', 0)
        territorio_prov = self.request.GET.get('territorio_prov', 0)
        territorio_reg = self.request.GET.get('territorio_reg', 0)
        if territorio_com and territorio_com != '0':
            extra['territorio'] = Territorio.objects.get(
                territorio=Territorio.TERRITORIO.C,
                cod_com=territorio_com
            ).nome
        elif territorio_prov and territorio_prov != '0':
            extra['territorio'] = Territorio.objects.get(
                territorio=Territorio.TERRITORIO.P,
                cod_prov=territorio_prov
            ).nome_con_provincia
        elif territorio_reg and territorio_reg != '0':
            extra['territorio'] = Territorio.objects.get(
                territorio=Territorio.TERRITORIO.R,
                cod_reg=territorio_reg
            ).nome

        # get data about custom costo and n_progetti range facets
        extra['facet_queries_costo'] = self.get_custom_facet_queries_costo()
        extra['facet_queries_n_progetti'] = self.get_custom_facet_queries_n_progetti()

        # definizione struttura dati per  visualizzazione faccette ruoli
        extra['ruolo'] = {
            'denominazione':dict(Ruolo.RUOLO)
        }

        # definizione struttura dati per  visualizzazione faccette tema
        extra['tema'] = {
            'descrizione': dict(
                (c.codice, c.descrizione)
                    for c in Tema.objects.filter(tipo_tema=Tema.TIPO.sintetico)
            ),
            'short_label': dict(
                (c.codice, c.short_label)
                    for c in Tema.objects.filter(tipo_tema=Tema.TIPO.sintetico)
            )
        }
        extra['base_url'] = reverse('soggetti_search') + '?' + extra['params'].urlencode()
        extra['soggetto'] = True

        paginator = Paginator(self.results, 25)
        page = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page_obj = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page_obj = paginator.page(paginator.num_pages)

        extra['paginator'] = paginator
        extra['page_obj'] = page_obj

        return extra


class SoggettiView(AggregatoView, TemplateView):
    #raise Exception("Class SoggettiView needs to be implemented")
    pass

class SoggettoView(AggregatoView, DetailView):
    model = Soggetto
    context_object_name = 'soggetto'

    @cached_context
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SoggettoView, self).get_context_data(**kwargs)

        logger = logging.getLogger('console')
        logger.debug("get_aggregate_data start")
        context = self.get_aggregate_data(context, soggetto=self.object)

        # calcolo dei collaboratori con cui si spartiscono piu' soldi
        logger.debug("top_collaboratori start")
        collaboratori = {}
        soggetti_ids = Soggetto.objects.exclude(pk=self.object.pk).filter(progetto__ruolo__soggetto=self.object).values('pk')
        for s in soggetti_ids:
            s_id = s['pk']
            if not s_id in collaboratori:
                collaboratori[s_id] = 0
            collaboratori[s_id] += 1

        top_collaboratori = sorted(
            # create a list of dict with partners
            [{'soggetto_id':s_id, 'numero':collaboratori[s_id]} for s_id in collaboratori],
            # sorted by totale
            key = lambda c: c['numero'],
            reverse = True )[:5]

        # hydrate just the 5 extracted soggetti
        for c in top_collaboratori:
            c['soggetto'] = Soggetto.objects.get(pk=c['soggetto_id'])

        context['top_collaboratori'] = top_collaboratori


        # calcolo dei progetti con piu' fondi
        logger.debug("top_progetti start")
        context['top_progetti'] = self.object.progetti.distinct().order_by('-fin_totale_pubblico')[:5]
        """
        context['top_progetti'] = [
            Progetto.objects.get(pk=p['codice_locale'])
            for p in self.object.progetti.values('codice_locale', 'fin_totale_pubblico').distinct().order_by('-fin_totale_pubblico')[:5]]
        """
        logger.debug("top_progetti end")

        # calcolo dei comuni un cui questo soggetto ha operato di piu'
        logger.debug("territori_piu_finanziati_pro_capite start")
        context['territori_piu_finanziati_pro_capite'] = Territorio.objects.comuni()\
            .filter(progetto__soggetto_set__pk=self.object.pk).defer('geom')\
            .annotate(totale=Sum('progetto__fin_totale_pubblico'))\
            .order_by('-totale')[:5]



        ## calcolo dei totali di finanziamenti per regione (e nazioni)
        context['lista_finanziamenti_per_regione'] = []
        logger.debug("lista_finanziamenti_per_regione start")

        ## insieme dei progetti del soggetto che hanno multilocalizzazioni
        ps_multiloc = Progetto.objects.del_soggetto(self.object).annotate(
            tot=Count('territorio_set')
        ).filter(tot__gt=1)


        ## definizioni funzioni usate internamente
        def tot(qs):
            """
            Calcolo totale a partire da queryset qs, il metodo è indicato in context['tematizzazione']
            """
            return getattr(qs, context['tematizzazione'])()

        def multi_localizzato_in_regione(p,r):
            """
            Torna True se il progetto p
             ha *tutte* le territorializzazioni in un unica regione
            Torna False in caso contrario
            """
            return all( map(lambda t: t.cod_reg == r.cod_reg, p.territori) )

        def multi_localizzato_in_nazione(p):
            """
            Torna True se il progetto p
             ha almeno una territorializzazione nazionale e nessuna estera
            Torna False in caso contrario
            """
            return any(map(lambda t: t.territorio == 'N', p.territori)) and \
                   all(map(lambda t: t.territorio != 'E', p.territori))


        ## costruzione lista per le regioni
        logger.debug("::fetch dati_regioni start")
        for regione in Territorio.objects.regioni().defer('geom'):

            logger.debug("::::regione {0}".format(regione))

            # progetti del soggetto localizzati in territori della regione
            psr = Progetto.objects.nel_territorio(regione).del_soggetto(self.object)

            logger.debug("::::::filter start")
            # elimina dai progetti multiloc del soggetto quelli localizzati esclusivamente nella regione
            ps_multiloc = filter(lambda p: not multi_localizzato_in_regione(p, regione), ps_multiloc)


            logger.debug("::::::queryset start")
            # predispone la query per estrarre tutti i progetti del soggetto, localizzati nella regione,
            # tranne quelli multilocalizzati anche in altre regioni oltre questa in considerazione
            # questo serve a evitare di contare 2 volte progetti multilocalizzati in regioni differenti,
            # nelle somme dei progetti regionali di un determinato soggetto
            queryset = psr.exclude(
                # tutti i progetti in regione del soggetto, NON multi localizzati in altre regioni
                pk__in=ps_multiloc
            ).distinct()

            logger.debug("::::::append tot start")
            # calcola il totale richiesto dalla vista (totale_costi, totale_procapite, totale_progetti)
            # e lo appende alla lista fei finanziamenti per regione
            context['lista_finanziamenti_per_regione'].append( ( regione, tot( queryset ) ) )

        # rimuovo tutti i progetti multilocalizzati nazionali
        ps_multiloc = filter(lambda p: not multi_localizzato_in_nazione(p), ps_multiloc)

        logger.debug("::fetch dati_nazioni start")
        for nazione in Territorio.objects.filter(territorio__in=['N','E']).defer('geom').order_by('-territorio'):

            queryset = Progetto.objects.nel_territorio( nazione ).del_soggetto( self.object ).exclude(
                # tutti i progetti in una nazione realizzati dal soggetto NON multi localizzati nella nazione
                # (e neanche nelle regioni, che sono già stati eliminati prima)
                pk__in=ps_multiloc
            )

            context['lista_finanziamenti_per_regione'].append( ( nazione, tot( queryset ) ) )
        logger.debug("::fetch dati_nazioni end")

        if len(ps_multiloc):
            # aggrego in un territorio fittizio i progetti multilocalizzati non inclusi fino ad ora
            context['lista_finanziamenti_per_regione'].append(
                (
                    Territorio(denominazione='In più territori', territorio='X'),
                    tot( Progetto.objects.del_soggetto( self.object).filter(pk__in=ps_multiloc) )
                )
            )
        logger.debug("lista_finanziamenti_per_regione stop")


        # calcolo i finanziamenti per ruolo del soggetto
        # preparo il filtro di aggregazione in base alla tematizzazione richiesta
        logger.debug("lista_finanziamenti_per_ruolo start")
        aggregazione_ruolo = {
            'totale_costi': Sum('progetto__fin_totale_pubblico'),
            'totale_pagamenti': Sum('progetto__pagamento'),
            'totale_progetti': Count('progetto')
        }[ self.request.GET.get('tematizzazione', 'totale_costi') ]

        context['lista_finanziamenti_per_ruolo'] = []

        progetto_to_ruoli = {}

        # TODO quando avremo realizzatori e destinatari posso prendere tutti i ruoli
        for tipo_ruolo, nome_ruolo in Ruolo.RUOLO[:2]:

            for progetto_id, tot in Ruolo.objects.filter(soggetto=self.object, ruolo=tipo_ruolo).annotate(tot=aggregazione_ruolo).values_list('progetto_id', 'tot'):

                if progetto_id not in progetto_to_ruoli:
                    progetto_to_ruoli[progetto_id] = {}
                progetto_to_ruoli[progetto_id][nome_ruolo] = float(tot if tot else 0)

        dict_finanziamenti_per_ruolo = {}

        for progetto_id in progetto_to_ruoli:

            is_multiple = len(progetto_to_ruoli[progetto_id]) > 1

            if is_multiple:
                # il soggetto partecipa con piu' ruoli
                # concateno i nomi dei ruoli per creare un nuovo nome
                name = "/".join(sorted(progetto_to_ruoli[progetto_id].keys()))
                tot = 0
                for key in progetto_to_ruoli[progetto_id]:
                    # prendo il massimo totale, tanto DEVONO essere tutti uguali
                    tot = max(tot, progetto_to_ruoli[progetto_id][key])
                    # aggiungo il ruolo anche se vuoto
                    if key not in dict_finanziamenti_per_ruolo: dict_finanziamenti_per_ruolo[key] = 0.0
                if name not in dict_finanziamenti_per_ruolo: dict_finanziamenti_per_ruolo[name] = 0.0
                dict_finanziamenti_per_ruolo[name]+=tot
            else:
                # il soggetto ha un solo ruolo in questo progetto
                name = progetto_to_ruoli[progetto_id].keys()[0]
                tot = progetto_to_ruoli[progetto_id][name]
                if name not in dict_finanziamenti_per_ruolo: dict_finanziamenti_per_ruolo[name] = 0.0
                dict_finanziamenti_per_ruolo[name] += tot

        del progetto_to_ruoli

        # ordino il dict_finanziamenti_per_ruolo per i suoi valore (il totale)
        context['lista_finanziamenti_per_ruolo'] = sorted(dict_finanziamenti_per_ruolo.items(), key=lambda x: x[1], reverse=True)
        logger.debug("lista_finanziamenti_per_ruolo stop")

        del dict_finanziamenti_per_ruolo

        return context
