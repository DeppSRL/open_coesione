from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.db.models import Count, Sum
from django.core.urlresolvers import reverse
from oc_search.forms import RangeFacetedSearchForm
from oc_search.mixins import FacetRangeCostoMixin, FacetRangeNProgettiMixin, TerritorioMixin
from oc_search.views import ExtendedFacetedSearchView
from open_coesione.views import AggregatoView, AccessControlView
from progetti.models import Progetto, Tema, ClassificazioneAzione, Ruolo
from soggetti.models import Soggetto
from territori.models import Territorio


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
        '1-100KTO1M':  {'qrange': '[100001 TO 1000000]',       'r_label': 'da 100.000 a 1 mil. di &euro;'},
        '2-1MTO10M':   {'qrange': '[1000001 TO 10000000]',     'r_label': 'da 1 mil. a 10 mil. di &euro;'},
        '3-10MTO100M': {'qrange': '[10000001 TO 100000000]',   'r_label': 'da 10 mil. a 100 mil. di &euro;'},
        '4-100MTO1G':  {'qrange': '[100000001 TO 1000000000]', 'r_label': 'da 100 mil. a 1 mld. di &euro;'},
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

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SoggettoView, self).get_context_data(**kwargs)

        context = self.get_aggregate_data(context, soggetto=self.object)

        # calcolo dei collaboratori con cui si spartiscono piu' soldi
        collaboratori = {}
        soggetti = Soggetto.objects.exclude(pk=self.object.pk).filter(progetto__ruolo__soggetto=self.object)
        for s in soggetti:
            if not s in collaboratori:
                collaboratori[s] = 0
            collaboratori[s] += 1

        context['top_collaboratori'] = sorted(
            # create a list of dict with partners
            [{'soggetto':key, 'numero':collaboratori[key]} for key in collaboratori],
            # sorted by totale
            key = lambda c: c['numero'],
            # desc
            reverse = True )[:5]

        # calcolo dei progetti con piu' fondi
        context['top_progetti'] = self.object.progetti.distinct().order_by('-fin_totale_pubblico')[:5]

        # calcolo dei comuni un cui questo soggetto ha operato di piu'
        context['territori_piu_finanziati_pro_capite'] = Territorio.objects.comuni()\
            .filter(progetto__soggetto_set__pk=self.object.pk)\
            .annotate(totale=Sum('progetto__fin_totale_pubblico'))\
            .order_by('-totale')[:5]

        # calcolo dei finanziamenti regione per regione
        progetti_multi_territorio = Progetto.objects.del_soggetto(self.object).annotate(tot=Count('territorio_set')).filter(tot__gt=1).distinct()

        # e nell'ambito nazionale
        context['lista_finanziamenti_per_regione'] = [
            (regione, getattr(Progetto.objects.exclude(pk__in=[p.pk for p in progetti_multi_territorio]).nel_territorio( regione ).del_soggetto(self.object),
                              self.request.GET.get('tematizzazione', 'totale_costi'))())
            for regione in Territorio.objects.regioni(with_nation=True)
        ]
        if progetti_multi_territorio:
            context['lista_finanziamenti_per_regione'].append(
                (
                    Territorio(denominazione='Multi-localizzazione'),
                    getattr(progetti_multi_territorio, self.request.GET.get('tematizzazione', 'totale_costi'))()
                )
            )

        # calcolo i finanziamenti per ruolo del soggetto
        # preparo il filtro di aggregazione in base alla tematizzazione richiesta
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
                # prendo il massimo totale, tanto DEVONO essere tutti uguali
                tot = max([ progetto_to_ruoli[progetto_id][key] for key in progetto_to_ruoli[progetto_id] ])
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

        del dict_finanziamenti_per_ruolo

        return context