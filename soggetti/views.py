# -*- coding: utf-8 -*-
from collections import defaultdict, OrderedDict
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Sum
from django.views.generic.detail import DetailView
from models import Soggetto
from oc_search.views import OCFacetedSearchView
from open_coesione.views import AggregatoMixin, XRobotsTagTemplateResponseMixin
from progetti.models import Progetto, Tema, Ruolo
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

        # if self.request.GET.get('tematizzazione', 'totale_costi') == 'anagrafica':
        #     context['tematizzazione'] = 'anagrafica'
        #     context.update(
        #         self.get_totals(soggetto=self.object)
        #     )
        #
        #     self.template_name = 'soggetti/soggetto_detail_anagrafica.html'
        #     return context

        context = self.get_aggregate_data(context, soggetto=self.object)

        # PROGETTI CON PIÙ FONDI

        context['top_progetti'] = context.pop('top_progetti_per_costo')

        # COLLABORATORI CON CUI SI SPARTISCONO PIÙ SOLDI

        top_collaboratori = Soggetto.objects.filter(progetto__ruolo__soggetto=self.object).exclude(pk=self.object.pk).values('pk').annotate(totale=Count('pk')).order_by('-totale')[:5]

        soggetto_by_pk = Soggetto.objects.in_bulk(x['pk'] for x in top_collaboratori)

        context['top_collaboratori'] = []
        for c in top_collaboratori:
            soggetto = soggetto_by_pk[c['pk']]
            soggetto.totale = c['totale']
            context['top_collaboratori'].append(soggetto)

        # COMUNI IN CUI QUESTO SOGGETTO HA OPERATO DI PIU'

        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(filters={'progetto__soggetto_set__pk': self.object.pk})

        # TOTALI PER REGIONI (E NAZIONI)

        progetti = Progetto.objects.myfilter(soggetto=self.object)

        # i progetti del soggetto localizzati in più territori (vengono considerati a parte per evitare di contarli più volte nelle aggregazioni)
        progetti_multilocalizzati_pks = [x['pk'] for x in progetti.values('pk').annotate(cnt=Count('territorio_set__cod_reg', distinct=True)).filter(cnt__gt=1)]

        totali_non_multilocalizzati = {x['id']: x[context['tematizzazione']] for x in progetti.exclude(pk__in=progetti_multilocalizzati_pks).totali_group_by('territorio_set__cod_reg')}

        totale_multilocalizzati_nazionali = 0
        totale_multilocalizzati_non_nazionali = 0
        for progetto in Progetto.objects.filter(pk__in=progetti_multilocalizzati_pks).prefetch_related('territorio_set'):
            if context['tematizzazione'] == 'totale_costi':
                val = float(progetto.fin_totale_pubblico)
            elif context['tematizzazione'] == 'totale_pagamenti':
                val = float(progetto.pagamento)
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

        # TOTALI PER RUOLO

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


class SoggettoSearchView(OCFacetedSearchView):
    RANGES = {
        'costo': {
            '0-0TO100K':   {'qrange': '[* TO 100000]',             'label': 'fino a 100.000 €'},
            '1-100KTO1M':  {'qrange': '[100000.1 TO 1000000]',     'label': 'da 100.000 a 1 mil. di €'},
            '2-1MTO10M':   {'qrange': '[1000001 TO 10000000]',     'label': 'da 1 mil. a 10 mil. di €'},
            '3-10MTO100M': {'qrange': '[10000001 TO 100000000]',   'label': 'da 10 mil. a 100 mil. di €'},
            '4-100MTO1G':  {'qrange': '[100000010 TO 1000000000]', 'label': 'da 100 mil. a 1 mld. di €'},
            '5-1GTOINF':   {'qrange': '[1000000001 TO *]',         'label': 'oltre 1 mld. di €'},
        },
        'n_progetti': {
            '0-0TO10':    {'qrange': '[* TO 10]',       'label': 'fino a 10'},
            '1-10TO100':  {'qrange': '[11 TO 100]',     'label': 'da 10 a 100'},
            '2-100TO1K':  {'qrange': '[101 TO 1000]',   'label': 'da 100 a 1.000'},
            '3-1KTO10K':  {'qrange': '[1001 TO 10000]', 'label': 'da 1.000 a 10.000'},
            '4-10KTOINF': {'qrange': '[10001 TO *]',    'label': 'oltre 10.000'},
        },
    }

    @staticmethod
    def _get_objects_by_pk(pks):
        return {str(key): value for key, value in Soggetto.objects.in_bulk(pks).items()}

    def build_page(self):
        (paginator, page) = super(SoggettoSearchView, self).build_page()

        ruolo_cod2descr = dict(Ruolo.RUOLO)

        for object in page.object_list:
            object.ruolo = [ruolo_cod2descr[r] for r in object.ruolo]

        return paginator, page

    def extra_context(self):
        extra = super(SoggettoSearchView, self).extra_context()

        extra['soggetto'] = True

        # definizione struttura dati per visualizzazione faccette

        facets = OrderedDict()

        facets['ruolo'] = self._build_facet_field_info('ruolo', 'Ruolo', {k: (v, v) for k, v in dict(Ruolo.RUOLO).items()})
        facets['tema'] = self._build_facet_field_info('tema', 'Tema', {o.codice: (o.descrizione, o.short_label) for o in Tema.objects.principali()})

        facets['costo'] = self._build_range_facet_queries_info('costo', 'Finanziamenti')
        facets['n_progetti'] = self._build_range_facet_queries_info('n_progetti', 'Numero di progetti')

        extra['my_facets'] = facets

        return extra
