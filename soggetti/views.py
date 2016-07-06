# -*- coding: utf-8 -*-
from collections import defaultdict, OrderedDict
from django.conf import settings
from django.db.models import Count, Sum
from django.views.generic.detail import DetailView
from models import Soggetto
from oc_search.views import OCFacetedSearchView
from open_coesione.views import AggregatoMixin, XRobotsTagTemplateResponseMixin, cached_context
from progetti.models import Progetto, Tema, Ruolo
from territori.models import Territorio


class SoggettoView(XRobotsTagTemplateResponseMixin, AggregatoMixin, DetailView):
    model = Soggetto
    context_object_name = 'soggetto'

    def get_x_robots_tag(self):
        return 'noindex' if self.object.privacy_flag else False

    def get_progetti_queryset(self):
        return Progetto.objects.del_soggetto(self.object)

    @property
    def cache_enabled(self):
        return self.object.n_progetti > settings.BIG_SOGGETTI_THRESHOLD

    @cached_context
    def get_cached_context_data(self):
        sum_dict = lambda *ds: {k: sum(d.get(k, 0) or 0 for d in ds) for k in ds[0]}

        context = self.get_aggregate_data()

        context['top_progetti'] = context.pop('top_progetti_per_costo')

        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(filters={'progetto__soggetto_set__pk': self.object.pk})

        # == COLLABORATORI CON CUI SI SPARTISCONO PIÙ SOLDI =======================================

        top_collaboratori = Soggetto.objects.filter(progetto__ruolo__soggetto=self.object).exclude(pk=self.object.pk).values('pk').annotate(totale=Count('pk')).order_by('-totale')[:5]

        soggetto_by_pk = Soggetto.objects.in_bulk(x['pk'] for x in top_collaboratori)

        context['top_collaboratori'] = []
        for c in top_collaboratori:
            soggetto = soggetto_by_pk[c['pk']]
            soggetto.totale = c['totale']
            context['top_collaboratori'].append(soggetto)

        # == TOTALI PER REGIONI (E NAZIONI) =======================================================

        progetti = self.get_progetti_queryset()

        # i progetti del soggetto localizzati in più territori (vengono considerati a parte per evitare di contarli più volte nelle aggregazioni)
        progetti_multilocalizzati_pks = [x['pk'] for x in progetti.values('pk').annotate(cnt=Count('territorio_set__cod_reg', distinct=True)).filter(cnt__gt=1)]

        totali_non_multilocalizzati = {x.pop('id'): x for x in progetti.exclude(pk__in=progetti_multilocalizzati_pks).totali_group_by('territorio_set__cod_reg')}

        totali_multilocalizzati_nazionali = {}
        totali_multilocalizzati_non_nazionali = {}
        for progetto in Progetto.objects.filter(pk__in=progetti_multilocalizzati_pks).prefetch_related('territorio_set'):
            totali_progetto = {'totale_costi': float(progetto.fin_totale_pubblico or 0), 'totale_pagamenti': float(progetto.pagamento or 0), 'totale_progetti': 1}

            if any(t.is_nazionale for t in progetto.territori) and not any(t.is_estero for t in progetto.territori):  # con almeno una localizzazione nazionale e nessuna estera
                totali_multilocalizzati_nazionali = sum_dict(totali_progetto, totali_multilocalizzati_nazionali)
            else:
                totali_multilocalizzati_non_nazionali = sum_dict(totali_progetto, totali_multilocalizzati_non_nazionali)

        if any(totali_multilocalizzati_nazionali.viewvalues()):
            totali_non_multilocalizzati[0] = sum_dict(totali_multilocalizzati_nazionali, totali_non_multilocalizzati.get(0, {}))

        # totali_non_multilocalizzati = {key: tots for key, tots in totali_non_multilocalizzati.items() if any(tots.viewvalues())}

        context['territori'] = []

        for territorio in Territorio.objects.regioni(with_nation=True).filter(cod_reg__in=totali_non_multilocalizzati.keys()).order_by('-territorio', 'denominazione').defer('geom'):
            territorio.totali = totali_non_multilocalizzati[territorio.cod_reg]
            context['territori'].append(territorio)

        # assegno a un territorio fittizio i progetti multilocalizzati senza localizzazione nazionale
        if any(totali_multilocalizzati_non_nazionali.viewvalues()):
            territorio = Territorio(denominazione=u'In più territori', territorio='X')
            territorio.totali = totali_multilocalizzati_non_nazionali
            context['territori'].append(territorio)

        # == TOTALI PER RUOLO =====================================================================

        totali_by_ruolo_by_progetto = defaultdict(dict)

        for ruolo in dict(Ruolo.RUOLO).keys():
            for totali in Ruolo.objects.filter(soggetto=self.object, ruolo=ruolo).values('progetto_id').annotate(totale_costi=Sum('progetto__fin_totale_pubblico'), totale_pagamenti=Sum('progetto__pagamento'), totale_progetti=Count('progetto')):
                totali_by_ruolo_by_progetto[totali.pop('progetto_id')][ruolo] = totali

        totali_by_ruolo = defaultdict(dict)

        for totaliprogetto_by_ruolo in totali_by_ruolo_by_progetto.values():
            codice = ''.join(totaliprogetto_by_ruolo.keys())  # in caso di più ruoli per uno stesso progetto si crea un nuovo codice
            totali = totaliprogetto_by_ruolo.values()[0]  # prendo il primo dei totali per ruolo, tanto DEVONO essere tutti uguali

            totali_by_ruolo[codice] = sum_dict(totali, totali_by_ruolo[codice])

        context['ruoli'] = [{'nome': '/'.join(sorted([dict(Ruolo.RUOLO)[r] for r in codice])), 'codice': codice, 'totali': totali} for codice, totali in totali_by_ruolo.items()]

        return context

    def get_context_data(self, **kwargs):
        context = super(SoggettoView, self).get_context_data(**kwargs)

        # if self.request.GET.get('tematizzazione', 'totale_costi') == 'anagrafica':
        #     context['tematizzazione'] = 'anagrafica'
        #     context.update(self.get_progetti_queryset().totali())
        #
        #     self.template_name = 'soggetti/soggetto_detail_anagrafica.html'
        #
        #     return context

        context.update(self.get_cached_context_data())

        self.tematizza_context_data(context)

        for r in context['ruoli']:
            r['totale'] = r.pop('totali').get(context['tematizzazione'], 0)

        context['ruoli'] = sorted(context['ruoli'], key=lambda x: x['totale'], reverse=True)

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
