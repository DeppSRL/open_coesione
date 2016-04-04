# -*- coding: utf-8 -*-
from collections import defaultdict
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.cache import cache
from django.db.models import Count, Sum
from django.core.urlresolvers import reverse
from django.views.generic.detail import DetailView
from oc_search.mixins import FacetRangeCostoMixin, FacetRangeNProgettiMixin, TerritorioMixin
from oc_search.views import ExtendedFacetedSearchView
from open_coesione.views import AggregatoMixin, XRobotsTagTemplateResponseMixin
from progetti.models import Progetto, Tema, Ruolo
from models import Soggetto
from territori.models import Territorio


class SoggettoView(XRobotsTagTemplateResponseMixin, AggregatoMixin, DetailView):
    model = Soggetto
    context_object_name = 'soggetto'

    def get_x_robots_tag(self):
        return 'noindex' if self.object.privacy_flag else False

    def get_context_data(self, **kwargs):
        # look for context in cache (only for soggetti with a high number of progetti).
        cache_key = None
        if self.object.n_progetti > settings.BIG_SOGGETTI_THRESHOLD:
            cache_key = 'context' + self.request.get_full_path()
            context = cache.get(cache_key)
            if context is not None:
                return context

        context = super(SoggettoView, self).get_context_data(**kwargs)

        context = self.get_aggregate_data(context, soggetto=self.object)

        # CALCOLO DEI COLLABORATORI CON CUI SI SPARTISCONO PIÙ SOLDI

        top_collaboratori = Soggetto.objects.filter(progetto__ruolo__soggetto=self.object).exclude(pk=self.object.pk).values('pk').annotate(totale=Count('pk')).order_by('-totale')[:5]

        soggetto_by_pk = Soggetto.objects.in_bulk(x['pk'] for x in top_collaboratori)

        context['top_collaboratori'] = []
        for c in top_collaboratori:
            soggetto = soggetto_by_pk[c['pk']]
            soggetto.totale = c['totale']
            context['top_collaboratori'].append(soggetto)

        # CALCOLO DEI PROGETTI CON PIÙ FONDI

        # top_progetti = self.object.progetti.values('pk', 'fin_totale_pubblico').distinct().order_by('-fin_totale_pubblico')[:5]
        # progetto_by_pk = Progetto.objects.in_bulk(x['pk'] for x in top_progetti)
        # context['top_progetti'] = [progetto_by_pk[x['pk']] for x in top_progetti]
        context['top_progetti'] = self.object.progetti.distinct().order_by('-fin_totale_pubblico')[:5]
        # context['top_progetti'] = [Progetto.objects.get(pk=p['codice_locale']) for p in self.object.progetti.values('codice_locale', 'fin_totale_pubblico').distinct().order_by('-fin_totale_pubblico')[:5]]

        # CALCOLO DEI COMUNI UN CUI QUESTO SOGGETTO HA OPERATO DI PIU'

        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(filters={'progetto__soggetto_set__pk': self.object.pk})

        # CALCOLO DEI TOTALI PER REGIONI (E NAZIONI)

        # i progetti del soggetto localizzati in più territori (vengono considerati a parte per evitare di contarli più volte nelle aggregazioni)
        progetti_multilocalizzati_pk = [x['pk'] for x in self.object.progetti.values('pk').annotate(num_reg=Count('territorio_set__cod_reg', distinct=True)).filter(num_reg__gt=1)]

        queryset = self.object.progetti.exclude(pk__in=progetti_multilocalizzati_pk).values('codice_locale', 'fin_totale_pubblico', 'pagamento', 'territorio_set__cod_reg').distinct()

        sql, params = queryset.query.sql_with_params()

        from django.db import connection

        def dictfetchall(cursor):
            col_names = [x.name for x in cursor.description]
            for row in cursor.fetchall():
                yield dict(zip(col_names, row))

        cursor = connection.cursor()
        cursor.execute('SELECT t.cod_reg, SUM(t.fin_totale_pubblico) AS "totale_costi", SUM(t.pagamento) AS "totale_pagamenti", COUNT(*) AS "totale_progetti" from ({}) AS t GROUP BY t.cod_reg'.format(sql), params)

        totali_non_multilocalizzati = {x['cod_reg']: x[context['tematizzazione']] for x in dictfetchall(cursor)}

        # from itertools import groupby

        # aggregate_functions = {
        #     'totale_costi': lambda g: sum(x['fin_totale_pubblico'] for x in g),
        #     'totale_pagamenti': lambda g: sum(x['pagamento'] for x in g),
        #     'totale_progetti': lambda g: sum(1 for x in g),
        # }

        # totali_non_multilocalizzati = {k: aggregate_functions[context['tematizzazione']](g) for k, g in groupby(queryset.order_by('territorio_set__cod_reg').iterator(), key=lambda x: x['territorio_set__cod_reg'])}

        totale_multilocalizzati_nazionali = 0
        totale_multilocalizzati_non_nazionali = 0
        for progetto in Progetto.objects.filter(pk__in=progetti_multilocalizzati_pk).prefetch_related('territorio_set'):
            if context['tematizzazione'] == 'totale_costi':
                val = progetto.fin_totale_pubblico
            elif context['tematizzazione'] == 'totale_pagamenti':
                val = progetto.pagamento
            elif context['tematizzazione'] == 'totale_progetti':
                val = 1

            if any([t.is_nazionale for t in progetto.territori]) and not any([t.is_estero for t in progetto.territori]):  # con almeno una localizzazione nazionale e nessuna estera
                totale_multilocalizzati_nazionali += val
            else:
                totale_multilocalizzati_non_nazionali += val

        if totale_multilocalizzati_nazionali:
            totali_non_multilocalizzati[0] = totali_non_multilocalizzati.get(0, 0) + totale_multilocalizzati_nazionali

        totali_non_multilocalizzati = {k: v for k, v in totali_non_multilocalizzati.items() if v > 0}

        context['territori'] = []

        for territorio in Territorio.objects.regioni(with_nation=True).filter(cod_reg__in=totali_non_multilocalizzati.keys()).order_by('-territorio', 'denominazione').defer('geom'):
            territorio.totale = totali_non_multilocalizzati[territorio.cod_reg]
            context['territori'].append(territorio)

        # assegno a un territorio fittizio i progetti multilocalizzati senza localizzazione nazionale
        if totale_multilocalizzati_non_nazionali:
            territorio = Territorio(denominazione=u'In più territori', territorio='X')
            territorio.totale = totale_multilocalizzati_non_nazionali
            context['territori'].append(territorio)

        # CALCOLO DEI TOTALI PER RUOLO DEL SOGGETTO

        aggregazione_ruolo = {
            'totale_costi': Sum('progetto__fin_totale_pubblico'),
            'totale_pagamenti': Sum('progetto__pagamento'),
            'totale_progetti': Count('progetto')
        }[context['tematizzazione']]

        progetto_to_ruoli = defaultdict(dict)

        for ruolo in dict(Ruolo.RUOLO).keys():
            for progetto_id, totale in Ruolo.objects.filter(soggetto=self.object, ruolo=ruolo).annotate(totale=aggregazione_ruolo).values_list('progetto_id', 'totale'):
                progetto_to_ruoli[progetto_id][ruolo] = float(totale or 0)

        dict_finanziamenti_per_ruolo = defaultdict(float)

        for ruoli in progetto_to_ruoli.values():
            codice = ''.join(ruoli.keys())  # in caso di più ruoli per uno stesso progetto si crea un nuovo codice
            totale = max(ruoli.values())    # prendo il massimo dei totali per ruolo, tanto DEVONO essere tutti uguali

            dict_finanziamenti_per_ruolo[codice] += totale

        context['ruoli'] = sorted([{'nome': '/'.join(sorted([dict(Ruolo.RUOLO)[r] for r in x[0]])), 'codice': x[0], 'totale': x[1]} for x in dict_finanziamenti_per_ruolo.items()], key=lambda x: x['totale'], reverse=True)

        # store context in cache (only for soggetti with a high number of progetti).
        if self.object.n_progetti > settings.BIG_SOGGETTI_THRESHOLD:
            serializable_context = context.copy()
            serializable_context.pop('view', None)
            cache.set(cache_key, serializable_context)

        return context


class SoggettoSearchView(ExtendedFacetedSearchView, FacetRangeCostoMixin, FacetRangeNProgettiMixin, TerritorioMixin):
    """
    This view allows faceted search and navigation of a soggetto.
    It extends an extended version of the basic FacetedSearchView,
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
        '0-0TO10':     {'qrange': '[* TO 10]',       'r_label': 'fino a 10'},
        '1-10TO100':   {'qrange': '[11 TO 100]',     'r_label': 'da 10 a 100'},
        '2-100TO1K':   {'qrange': '[101 TO 1000]',   'r_label': 'da 100 a 1.000'},
        '3-1KTO10K':   {'qrange': '[1001 TO 10000]', 'r_label': 'da 1.000 a 10.000'},
        '4-10KTOINF':  {'qrange': '[10001 TO *]',    'r_label': 'oltre 10.000'},
    }

    # def __init__(self, *args, **kwargs):
    #     # Needed to switch out the default form class.
    #     if kwargs.get('form_class') is None:
    #         kwargs['form_class'] = RangeFacetedSearchForm
    #
    #     super(SoggettoSearchView, self).__init__(*args, **kwargs)

    # def build_form(self, form_kwargs=None):
    #     if form_kwargs is None:
    #         form_kwargs = {}
    #
    #     return super(SoggettoSearchView, self).build_form(form_kwargs)

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

        # definizione struttura dati per visualizzazione faccette ruoli
        extra['ruolo'] = {
            'denominazione': dict(Ruolo.RUOLO)
        }

        # definizione struttura dati per visualizzazione faccette tema
        extra['tema'] = {
            'descrizione': dict((c.codice, c.descrizione) for c in Tema.objects.filter(tipo_tema=Tema.TIPO.sintetico)),
            'short_label': dict((c.codice, c.short_label) for c in Tema.objects.filter(tipo_tema=Tema.TIPO.sintetico)),
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
