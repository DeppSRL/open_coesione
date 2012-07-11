from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.db.models import Count, Sum
from django.core.urlresolvers import reverse
from oc_search.forms import RangeFacetedSearchForm
from oc_search.mixins import FacetRangeCostoMixin, FacetRangeNProgettiMixin
from oc_search.views import ExtendedFacetedSearchView
from open_coesione.views import AggregatoView, AccessControlView
from progetti.models import Progetto, Tema, ClassificazioneAzione, Ruolo
from soggetti.models import Soggetto
from territori.models import Territorio


class SoggettoSearchView(AccessControlView, ExtendedFacetedSearchView, FacetRangeCostoMixin, FacetRangeNProgettiMixin):
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
            'denominazione': dict(
                (r.ruolo, r.get_ruolo_display())
                    for r in Ruolo.objects.filter()
            )
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

        context['total_cost'] = Progetto.objects.totale_costi(soggetto=self.object)
        context['total_cost_paid'] = Progetto.objects.totale_pagamenti(soggetto=self.object)
        context['total_projects'] = Progetto.objects.totale_progetti(soggetto=self.object)
        context['cost_payments_ratio'] = "{0:.0%}".format(context['total_cost_paid'] / context['total_cost'] if context['total_cost'] > 0.0 else 0.0)

        context['temi_principali'] = [
            {
            'object': tema,
            'data': Tema.objects.\
                        filter(tema_superiore=tema).\
                        filter(progetto_set__soggetto_set__pk=self.object.pk).
                        aggregate(numero=Count('progetto_set'),
                            costo=Sum('progetto_set__fin_totale_pubblico'),
                            pagamento=Sum('progetto_set__pagamento'))
            } for tema in Tema.objects.principali()
        ]

        context['tipologie_principali'] = [
            {
            'object': natura,
            'data': ClassificazioneAzione.objects.\
                        filter(classificazione_superiore=natura).\
                        filter(progetto_set__soggetto_set__pk=self.object.pk).\
                        aggregate(numero=Count('progetto_set'),
                            costo=Sum('progetto_set__fin_totale_pubblico'),
                            pagamento=Sum('progetto_set__pagamento'))
            } for natura in ClassificazioneAzione.objects.tematiche()
        ]


        # calcolo dei collaboratori con cui si spartiscono piu' soldi
        collaboratori = {}
        for soggetti in [x.soggetti for x in self.object.progetti]:
            for s in soggetti:
                if s == self.object:
                    continue
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
        context['top_progetti'] = self.object.progetti.order_by('-fin_totale_pubblico')[:5]

        # calcolo dei comuni un cui questo soggetto ha operato di piu'
        context['territori_piu_finanziati_pro_capite'] = Territorio.objects.comuni()\
            .filter(progetto__soggetto_set__pk=self.object.pk)\
            .annotate(totale=Sum('progetto__fin_totale_pubblico'))\
            .order_by('-totale')[:5]


        #context['map'] = self.get_map_context( )

        context['lista_finanziamenti_per_regione'] = [
            (regione,float(Progetto.objects.nel_territorio( regione ).filter(soggetto_set__pk=self.object.pk).aggregate(totale=Sum('fin_totale_pubblico'))['totale'] or 0))
            for regione in Territorio.objects.regioni()
        ]


        return context