# -*- coding: utf-8 -*-
import csv
import StringIO
import zipfile
from collections import OrderedDict
from datetime import date, timedelta
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, Http404
from django.views.generic import DetailView, ListView, TemplateView, FormView
from forms import DescrizioneProgettoForm
from gruppo_programmi import GruppoProgrammi, split_by_type
from models import Progetto, ClassificazioneAzione, ProgrammaAsseObiettivo, ProgrammaLineaAzione,\
    Ruolo, Tema, Fonte, SegnalazioneProgetto, MonitoraggioASOC
from oc_search.views import OCFacetedSearchView
from open_coesione import utils
from open_coesione.views import AggregatoMixin, XRobotsTagTemplateResponseMixin, cached_context, OpendataView
from soggetti.models import Soggetto
from territori.models import Territorio


class ProgettoView(XRobotsTagTemplateResponseMixin, DetailView):
    model = Progetto
    queryset = Progetto.fullobjects.get_query_set().select_related('programma_asse_obiettivo__classificazione_superiore__classificazione_superiore', 'programma_linea_azione__classificazione_superiore__classificazione_superiore', 'classificazione_qsn__classificazione_superiore__classificazione_superiore', 'classificazione_azione__classificazione_superiore', 'tema__tema_superiore').prefetch_related('monitoraggi_asoc__istituto_comune')

    def get_x_robots_tag(self):
        return 'noindex' if (self.object.privacy_flag or (not self.object.active_flag)) else False

    def get_context_data(self, **kwargs):
        context = super(ProgettoView, self).get_context_data(**kwargs)

        context['MIUR_EXT_API_URL'] = settings.MIUR_EXT_API_URL

        self.object.progetti_attuatori_tutti = Progetto.fullobjects.filter(progetti_attuati=self.object)
        self.object.progetti_attuati_tutti = False  # Progetto.fullobjects.filter(progetti_attuatori=self.object).order_by('-cipe_flag')

        if self.object.territori:
            numero_collaboratori = 5
            altri_progetti_nei_territori_qs = Progetto.objects.exclude(codice_locale=self.object.codice_locale).nei_territori(self.object.territori).distinct().order_by('-fin_totale_pubblico')
            altri_progetti_nei_territori = [
                {
                    'titolo': 'Stesso tema',
                    'lista': altri_progetti_nei_territori_qs.con_tema(self.object.tema)[:numero_collaboratori],
                },
                {
                    'titolo': 'Stessi attuatori',
                    'lista': altri_progetti_nei_territori_qs.filter(soggetto_set__in=self.object.attuatori)[:numero_collaboratori],
                },
                {
                    'titolo': "Stessa natura dell'investimento",
                    'lista': altri_progetti_nei_territori_qs.con_natura(self.object.classificazione_azione)[:numero_collaboratori],
                },
                {
                    'titolo': 'Stessi programmatori',
                    'lista': altri_progetti_nei_territori_qs.filter(soggetto_set__in=self.object.programmatori)[:numero_collaboratori],
                },
            ]

            self.object.altri_progetti_nei_territori = [x for x in altri_progetti_nei_territori if x['lista']]

        self.object.pagamenti_bimestrali = self._get_pagamenti_bimestrali(self.object.pagamenti)

        return context

    @staticmethod
    def _get_pagamenti_bimestrali(pagamenti):
        pagamenti = list(pagamenti)

        pagamenti_bimestrali = []

        if pagamenti:
            data_iniziale = pagamenti[0].data

            pagamenti.reverse()

            data = date(2017, 02, 28)

            while data >= data_iniziale:
                month = data.month
                year = data.year

                month = month - 2 + month % 2
                if month < 1:
                    month += 12
                    year -= 1

                data = (data.replace(year=year, month=month, day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

                ammontare = 0
                percentuale = 0
                for pagamento in pagamenti:
                    if pagamento.data <= data:
                        ammontare = pagamento.ammontare
                        percentuale = pagamento.percentuale
                        break

                pagamenti_bimestrali.insert(0, {'data': data, 'ammontare': ammontare, 'percentuale': percentuale})

        return pagamenti_bimestrali


class ProgettoSearchView(OCFacetedSearchView):
    RANGES = {
        'costo': {
            '0-0TO1K': {
                'qrange': '[* TO 1000]',
                'label': 'fino a 1.000 €',
            },
            '1-1KTO10K': {
                'qrange': '[1000.01 TO 10000]',
                'label': 'da 1.000 a 10.000 €',
            },
            '2-10KTO100K': {
                'qrange': '[10000.01 TO 100000]',
                'label': 'da 10.000 a 100.000 €',
            },
            '3-100KTO1M': {
                'qrange': '[100000.01 TO 1000000]',
                'label': 'da 100.000 a 1.000.000 €',
            },
            '4-1MTO10M': {
                'qrange': '[1000001 TO 10000000]',
                'label': 'da 1.000.000 a 10.000.000 €',
            },
            '5-10MTOINF': {
                'qrange': '[10000001 TO *]',
                'label': 'oltre 10.000.000 €',
            },
        },
        'data_inizio': {
            '00-2017': {
                'qrange': '[2017-01-01T00:00:00Z TO *]',
                'label': '2017',
            },
            '01-2016': {
                'qrange': '[2016-01-01T00:00:00Z TO 2016-12-31T23:59:59Z]',
                'label': '2016',
            },
            '02-2015': {
                'qrange': '[2015-01-01T00:00:00Z TO 2015-12-31T23:59:59Z]',
                'label': '2015',
            },
            '03-2014': {
                'qrange': '[2014-01-01T00:00:00Z TO 2014-12-31T23:59:59Z]',
                'label': '2014',
            },
            '04-2013': {
                'qrange': '[2013-01-01T00:00:00Z TO 2013-12-31T23:59:59Z]',
                'label': '2013',
            },
            '05-2012': {
                'qrange': '[2012-01-01T00:00:00Z TO 2012-12-31T23:59:59Z]',
                'label': '2012',
            },
            '06-2011': {
                'qrange': '[2011-01-01T00:00:00Z TO 2011-12-31T23:59:59Z]',
                'label': '2011',
            },
            '07-2010': {
                'qrange': '[2010-01-01T00:00:00Z TO 2010-12-31T23:59:59Z]',
                'label': '2010',
            },
            '08-2009': {
                'qrange': '[2009-01-01T00:00:00Z TO 2009-12-31T23:59:59Z]',
                'label': '2009',
            },
            '09-2008': {
                'qrange': '[2008-01-01T00:00:00Z TO 2008-12-31T23:59:59Z]',
                'label': '2008',
            },
            '10-2007': {
                'qrange': '[2007-01-01T00:00:00Z TO 2007-12-31T23:59:59Z]',
                'label': '2007',
            },
            '11-early': {
                'qrange': '[1970-01-02T00:00:00Z TO 2006-12-31T23:59:59Z]',
                'label': 'prima del 2007',
            },
            '12-nd': {
                'qrange': '[* TO 1970-01-01T00:00:00Z]',
                'label': 'non disponibile',
            }
        },
        'perc_pagamento': {
            '0-0TO25': {
                'qrange': '[* TO 25.0]',
                'label': 'da 0 al 25%',
            },
            '1-25TO50': {
                'qrange': '[25.001 TO 50.0]',
                'label': 'dal 25% al 50%',
            },
            '2-50TO75': {
                'qrange': '[50.001 TO 75.0]',
                'label': 'dal 50% al 75%',
            },
            '3-75TO100': {
                'qrange': '[75.00 TO *]',
                'label': 'oltre il 75%',
            },
        },
    }

    def __call__(self, request):
        if not any(x.startswith('is_pubblicato') for x in request.GET.getlist('selected_facets')) and not request.GET.get('r'):
            from django import http
            uri = request.build_absolute_uri()
            return http.HttpResponseRedirect('{}{}selected_facets=is_pubblicato:true'.format(uri, '&' if '?' in uri else '?'))

        return super(ProgettoSearchView, self).__call__(request)

    @staticmethod
    def _get_objects_by_pk(pks):
        related = ['territorio_set', 'tema__tema_superiore', 'classificazione_azione__classificazione_superiore']
        return {str(key): value for key, value in Progetto.fullobjects.select_related(*related).prefetch_related(*related).in_bulk(pks).items()}

    def build_form(self, form_kwargs=None):
        # The is_active:1 facet is selected by default and is substituted by is_active:0 when explicitly requested
        # by clicking on the 'See archive' link in the progetti page
        if 'is_active:0' in self.request.GET.getlist('selected_facets'):
            form_kwargs = {'selected_facets': ['is_active:0']}
        else:
            form_kwargs = {'selected_facets': ['is_active:1']}

        return super(ProgettoSearchView, self).build_form(form_kwargs)

    def extra_context(self):
        extra = super(ProgettoSearchView, self).extra_context()

        fonte_fin = self.request.GET.get('fonte_fin')
        if fonte_fin:
            try:
                extra['fonte_fin'] = ProgrammaLineaAzione.objects.get(pk=fonte_fin)
            except ProgrammaLineaAzione.DoesNotExist:
                try:
                    extra['fonte_fin'] = ProgrammaAsseObiettivo.objects.get(pk=fonte_fin)
                except ProgrammaAsseObiettivo.DoesNotExist:
                    pass

        programmi_slug = self.request.GET.get('gruppo_programmi')
        if programmi_slug:
            try:
                extra['gruppo_programmi'] = GruppoProgrammi(codice=programmi_slug)
            except:
                pass

        soggetto_slug = self.request.GET.get('soggetto')
        if soggetto_slug:
            try:
                extra['soggetto'] = Soggetto.objects.get(slug=soggetto_slug)
            except Soggetto.DoesNotExist:
                pass
            else:
                soggetto_ruolo = self.request.GET.get('ruolo')
                if soggetto_ruolo:
                    extra['ruolo'] = '/'.join(sorted(set(dict(Ruolo.RUOLO).get(r, '') for r in soggetto_ruolo))).strip('/')

        extra['params'] = self.params.urlencode(safe=':')

        extra['n_max_downloadable'] = settings.N_MAX_DOWNLOADABLE_RESULTS

        extra['search_within_non_active'] = 'is_active:0' in self.request.GET.getlist('selected_facets')

        # definizione struttura dati per visualizzazione faccette

        facets = OrderedDict()

        facets['natura'] = self._build_facet_field_info('natura', "Natura dell'investimento", {o.codice.strip() or 'ND': (o.descrizione, o.short_label) for o in ClassificazioneAzione.objects.nature()})
        facets['tema'] = self._build_facet_field_info('tema', 'Tema', {o.codice: (o.descrizione, o.short_label) for o in Tema.objects.principali()})
        facets['fonte'] = self._build_facet_field_info('fonte', 'Fonte', {o.codice: (o.descrizione, o.short_label) for o in Fonte.objects.all()})
        facets['stato_progetto'] = self._build_facet_field_info('stato_progetto', 'Stato progetto', {k: (v, v) for k, v in dict(Progetto.STATO).items()})

        facets['data_inizio'] = self._build_range_facet_queries_info('data_inizio', 'Anno di inizio')
        facets['costo'] = self._build_range_facet_queries_info('costo', 'Finanziamenti')

        if getattr(settings, 'PERC_PAY_FACETS_ENABLED', False):
            facets['perc_pagamento'] = self._build_range_facet_queries_info('perc_pagamento', 'Percentuali pagamento')

        facets['is_pubblicato'] = self._build_facet_field_info('is_pubblicato', 'Visualizzazione', {'true': ('Progetti pubblicati', 'Progetti pubblicati'), 'false': ('Progetti esclusi', 'Progetti esclusi')})

        facets['stato_progetto']['values'] = sorted(facets['stato_progetto']['values'], key=lambda x: x['key'], reverse=True)

        if not extra['search_within_non_active']:
            facets['fonte']['values'] = [v for v in facets['fonte']['values'] if v['key'] != 'FSC0006']

        extra['my_facets'] = facets

        return extra


class BaseProgrammaView(AggregatoMixin, TemplateView):
    @cached_context
    def get_cached_context_data(self, programmi):
        context = self.get_aggregate_data()

        # discriminate between ProgrammaAsseObiettivo and ProgrammaLineaAzione
        programmi_splitted = split_by_type(programmi)

        from django.db.models import Q

        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(
            (
                Q(progetto__programma_asse_obiettivo__classificazione_superiore__classificazione_superiore__in=programmi_splitted['programmi_asse_obiettivo']) |
                Q(progetto__programma_linea_azione__classificazione_superiore__classificazione_superiore__in=programmi_splitted['programmi_linea_azione']),
            )
        )

        return context

    def get_context_data(self, **kwargs):
        programmi = kwargs.pop('programmi', [])

        context = super(BaseProgrammaView, self).get_context_data(**kwargs)

        context.update(self.get_cached_context_data(programmi=programmi))

        self.tematizza_context_data(context)

        context['ultimi_progetti_conclusi'] = self.get_progetti_queryset().no_privacy().conclusi()[:5]

        return context


class ProgrammiView(BaseProgrammaView):
    template_name = 'progetti/programmi_detail.html'

    def get_object(self):
        return GruppoProgrammi(codice=self.kwargs.get('slug'))

    def get_progetti_queryset(self):
        return Progetto.objects.con_programmi(self.get_object().programmi)

    @cached_context
    def get_cached_context_data(self, programmi):
        context = super(ProgrammiView, self).get_cached_context_data(programmi=programmi)

        if self.kwargs.get('slug') in ('ue-fesr', 'ue-fse'):
            import re
            from csvkit import convert
            from open_coesione.views import OpendataView

            data_pagamenti_per_programma = date(2015, 12, 31)

            dotazioni_totali = csv.DictReader(convert.xls2csv(open(OpendataView.get_latest_localfile('Target_Certificato_Pagamenti.xls'), 'rb'), sheet='Target spesa cert ammessi va').splitlines())

            pattern = re.compile('pagamenti ammessi (\d{4})1231')
            anni = [m.group(1) for m in map(pattern.match, dotazioni_totali.fieldnames) if m is not None]

            dotazioni_totali = list(dotazioni_totali)

            for trend in ('conv', 'cro'):
                programmi_per_trend_codici = [programma.codice for programma in programmi if ' {} '.format(trend) in programma.descrizione.lower()]

                valori_per_anno = OrderedDict([(x, {'dotazioni_totali': 0.0, 'pagamenti': 0.0}) for x in anni])

                for row in dotazioni_totali:
                    programma_codice = row['OC_CODICE_PROGRAMMA']
                    if programma_codice in programmi_per_trend_codici:
                        for anno in valori_per_anno:
                            data = '{}1231'.format(anno)

                            valori_per_anno[anno]['pagamenti'] += float(row['pagamenti ammessi {}'.format(data)] or 0)

                            try:
                                valore = row['DOTAZIONE TOTALE PROGRAMMA POST PAC {}'.format(data)]
                            except KeyError:
                                valore = row['DOTAZIONE TOTALE PROGRAMMA {}'.format(data)]

                            valori_per_anno[anno]['dotazioni_totali'] += float(valore)

                context['pagamenti_per_anno_{}'.format(trend)] = [{'year': anno, 'total_amount': valori['dotazioni_totali'], 'paid_amount': valori['pagamenti']} for anno, valori in valori_per_anno.items()]

                programmi_per_trend = ProgrammaAsseObiettivo.objects.filter(classificazione_set__classificazione_set__progetto_set__active_flag=True, classificazione_set__classificazione_set__progetto_set__visualizzazione_flag='0', codice__in=programmi_per_trend_codici).distinct().values('descrizione', 'codice').order_by('descrizione')

                dotazioni_totali_per_programma = {}
                pagamenti_per_programma = {}
                for row in dotazioni_totali:
                    programma_codice = row['OC_CODICE_PROGRAMMA']
                    if programma_codice in programmi_per_trend_codici:
                        data = data_pagamenti_per_programma.strftime('%Y%m%d')
                        try:
                            valore = row['DOTAZIONE TOTALE PROGRAMMA POST PAC {}'.format(data)]
                        except KeyError:
                            valore = row['DOTAZIONE TOTALE PROGRAMMA {}'.format(data)]

                        dotazioni_totali_per_programma[programma_codice] = float(valore)

                        pagamenti_per_programma[programma_codice] = float(row['pagamenti ammessi {}'.format(data)])

                context['pagamenti_per_programma_{}'.format(trend)] = [{'program': programma['descrizione'], 'total_amount': dotazioni_totali_per_programma[programma['codice']], 'paid_amount': pagamenti_per_programma[programma['codice']]} for programma in programmi_per_trend]

            pagamenti_per_anno_tutti = OrderedDict()
            for item in context['pagamenti_per_anno_conv'] + context['pagamenti_per_anno_cro']:
                if not item['year'] in pagamenti_per_anno_tutti:
                    pagamenti_per_anno_tutti[item['year']] = item.copy()
                else:
                    pagamenti_per_anno_tutti[item['year']]['total_amount'] += item['total_amount']
                    pagamenti_per_anno_tutti[item['year']]['paid_amount'] += item['paid_amount']

            context['pagamenti_per_anno_tutti'] = pagamenti_per_anno_tutti.values()

            context['data_pagamenti_per_programma'] = data_pagamenti_per_programma

        return context

    def get_context_data(self, **kwargs):
        try:
            gruppo_programmi = self.get_object()
        except:
            raise Http404

        context = super(ProgrammiView, self).get_context_data(programmi=gruppo_programmi.programmi, **kwargs)

        context['map_selector'] = 'gruppo-programmi/{}/'.format(self.kwargs['slug'])

        context['gruppo_programmi'] = gruppo_programmi

        return context


class ProgrammaView(BaseProgrammaView):
    template_name = 'progetti/programma_detail.html'

    def get_object(self):
        try:
            return ProgrammaLineaAzione.objects.programmi().get(pk=self.kwargs.get('codice'))
        except ProgrammaLineaAzione.DoesNotExist:
            return ProgrammaAsseObiettivo.objects.programmi().get(pk=self.kwargs.get('codice'))

    def get_progetti_queryset(self):
        return Progetto.objects.con_programmi([self.get_object()])

    def get_context_data(self, **kwargs):
        try:
            programma = self.get_object()
        except:
            raise Http404

        context = super(ProgrammaView, self).get_context_data(programmi=[programma], **kwargs)

        context['map_selector'] = 'programmi/{}/'.format(self.kwargs['codice'])

        context['programma'] = programma

        return context


# class ProgrammaView(BaseProgrammaView):
#     template_name = 'progetti/programma_detail.html'
#
#     def get_objects(self):
#         objects = []
#         for model in (ProgrammaAsseObiettivo, ProgrammaLineaAzione):
#             objects += list(model.objects.filter(pk=self.kwargs.get('codice')))
#         return objects
#
#     def get_progetti_queryset(self):
#         return Progetto.objects.con_programmi(self.get_objects())
#
#     def get_context_data(self, **kwargs):
#         programmi = self.get_objects()
#         try:
#             programma = programmi[0]
#         except:
#             raise Http404
#
#         context = super(ProgrammaView, self).get_context_data(programmi=programmi, **kwargs)
#
#         context['map_selector'] = 'programmi/{}/'.format(self.kwargs['codice'])
#
#         context['programma'] = programma
#
#         return context


class ClassificazioneAzioneView(AggregatoMixin, DetailView):
    context_object_name = 'natura'
    model = ClassificazioneAzione

    def get_queryset(self):
        return super(ClassificazioneAzioneView, self).get_queryset().nature()

    def get_progetti_queryset(self):
        return Progetto.objects.con_natura(self.object)

    @cached_context
    def get_cached_context_data(self):
        context = self.get_aggregate_data()

        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(filters={'progetto__classificazione_azione__classificazione_superiore': self.object})

        return context

    def get_context_data(self, **kwargs):
        context = super(ClassificazioneAzioneView, self).get_context_data(**kwargs)

        context.update(self.get_cached_context_data())

        self.tematizza_context_data(context)

        context['ultimi_progetti_conclusi'] = self.get_progetti_queryset().no_privacy().conclusi()[:5]

        context['map_selector'] = 'nature/{}/'.format(self.kwargs['slug'])

        return context


class TemaView(AggregatoMixin, DetailView):
    model = Tema

    def get_queryset(self):
        return super(TemaView, self).get_queryset().principali()

    def get_progetti_queryset(self):
        return Progetto.objects.con_tema(self.object)

    @cached_context
    def get_cached_context_data(self):
        context = self.get_aggregate_data()

        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(filters={'progetto__tema__tema_superiore': self.object})

        return context

    def get_context_data(self, **kwargs):
        context = super(TemaView, self).get_context_data(**kwargs)

        context.update(self.get_cached_context_data())

        self.tematizza_context_data(context)

        context['ultimi_progetti_conclusi'] = self.get_progetti_queryset().no_privacy().conclusi()[:5]

        context['map_selector'] = 'temi/{}/'.format(self.kwargs['slug'])

        return context


class ProgettoPagamentiCSVView(DetailView):
    model = Progetto
    queryset = Progetto.fullobjects.get_query_set()

    def get(self, request, *args, **kwargs):
        import locale

        locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

        self.object = self.get_object()

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=pagamenti_{}.csv'.format(self.kwargs.get('slug'))

        writer = utils.UnicodeWriter(response, dialect=utils.excel_semicolon)

        writer.writerow(['COD_LOCALE_PROGETTO', 'OC_DATA_PAGAMENTI', 'TOT_PAGAMENTI'])

        ammontare_cumulato = 0

        for pagamento in self.object.pagamenti:
            writer.writerow([
                self.object.codice_locale,
                pagamento.data.strftime('%x'),
                locale.format('%.2f', pagamento.ammontare - ammontare_cumulato, grouping=True),
            ])

            ammontare_cumulato = pagamento.ammontare

        return response


class BaseCSVView(AggregatoMixin, DetailView):
    def comuni_filter(self):
        return {}

    def comuni_con_pro_capite_filter(self):
        return {}

    def get(self, request, *args, **kwargs):
        import locale

        locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

        self.object = self.get_object()

        comuni_con_pro_capite = self.top_comuni_pro_capite(filters=self.comuni_con_pro_capite_filter(), qnt=None)
        altri_comuni = list(Territorio.objects.comuni().filter(**self.comuni_filter()).exclude(pk__in=(x.pk for x in comuni_con_pro_capite)).defer('geom'))

        comuni = comuni_con_pro_capite + altri_comuni

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}_pro_capite.csv'.format(self.kwargs.get('slug', 'all'))

        writer = utils.UnicodeWriter(response, dialect=utils.excel_semicolon)

        writer.writerow(['Comune', 'Provincia', 'Finanziamento pro capite'])

        for comune in comuni:
            writer.writerow([
                comune.denominazione,
                comune.provincia.denominazione,
                locale.format('%.2f', getattr(comune, 'totale_pro_capite', 0)),
            ])

        return response


class ClassificazioneAzioneCSVView(BaseCSVView):
    model = ClassificazioneAzione

    def comuni_con_pro_capite_filter(self):
        return {'progetto__classificazione_azione__classificazione_superiore': self.object}


class TemaCSVView(BaseCSVView):
    model = Tema

    def comuni_con_pro_capite_filter(self):
        return {'progetto__tema__tema_superiore': self.object}


class ProgettoCSVSearchView(ProgettoSearchView):
    def __init__(self, *args, **kwargs):
        super(ProgettoCSVSearchView, self).__init__(*args, **kwargs)
        self.searchqueryset = self.searchqueryset.values_list('pk', flat=True)

    @staticmethod
    def _get_objects_by_pk(pks):
        # related = ['tema__tema_superiore', 'classificazione_azione__classificazione_superiore', 'ruolo_set__soggetto', 'territorio_set']
        related = ['ruolo_set__soggetto', 'territorio_set']
        return {str(key): value for key, value in Progetto.fullobjects.select_related(*related).prefetch_related(*related).in_bulk(pks).items()}

    def create_response1(self):
        """
        Generates a zipped, downloadale CSV file, from search results
        """
        import datetime
        import logging
        import pandas as pd
        from open_coesione.views import OpendataView

        logger = logging.getLogger('csvimport')

        results = self.get_results()

        logger.info(u'Lettura csv...')

        start_time = datetime.datetime.now()

        csvfile = OpendataView.get_latest_localfile('progetti_OC.zip')

        try:
            with zipfile.ZipFile(csvfile) as z:
                with z.open(z.filelist[0]) as f:
                    df = pd.read_csv(
                        f,
                        sep=';',
                        header=0,
                        low_memory=True,
                        dtype=object,
                        encoding='utf-8-sig',
                        keep_default_na=False,
                    )
        except IOError:
            raise IOError(u'It was impossible to open file {}'.format(csvfile))

        df.rename(columns=lambda x: x.strip('"'), inplace=True)

        duration = datetime.datetime.now() - start_time
        seconds = round(duration.total_seconds())
        logger.info(u'{:02d}:{:02d}:{:02d}.'.format(int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)))

        logger.info(u'Composizione dataframe...')

        start_time = datetime.datetime.now()

        df = df[df['COD_LOCALE_PROGETTO'].isin(results)].sort('FINANZ_TOTALE_PUBBLICO', ascending=False)

        duration = datetime.datetime.now() - start_time
        seconds = round(duration.total_seconds())
        logger.info(u'{:02d}:{:02d}:{:02d}.'.format(int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)))

        logger.info(u'Scrittura csv...')

        start_time = datetime.datetime.now()

        output = StringIO.StringIO()
        df.to_csv(output, sep=';', encoding='utf-8', index=False)

        duration = datetime.datetime.now() - start_time
        seconds = round(duration.total_seconds())
        logger.info(u'{:02d}:{:02d}:{:02d}.'.format(int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)))

        logger.info(u'Scrittura zip...')

        start_time = datetime.datetime.now()

        response = HttpResponse(content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename=progetti.csv.zip'

        z = zipfile.ZipFile(response, 'w', zipfile.ZIP_DEFLATED)
        z.writestr('progetti.csv', output.getvalue())
        z.close()

        duration = datetime.datetime.now() - start_time
        seconds = round(duration.total_seconds())
        logger.info(u'{:02d}:{:02d}:{:02d}.'.format(int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)))

        return response

    def create_response(self):
        """
        Generates a zipped, downloadale CSV file, from search results
        """

        import json
        # import os
        # from csvkit import convert
        # from open_coesione.views import OpendataView
        import decimal
        import locale

        locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

        def myformat(val):
            if isinstance(val, (float, decimal.Decimal)):
                val = locale.format('%.2f', val)
            elif isinstance(val, (list, set)):
                val = u':::'.join(val)
            return val

        # reader = csv.DictReader(convert.xls2csv(open(OpendataView.get_latest_localfile('metadati_OC_2007_2013.xls'), 'rb'), sheet='Progetti').splitlines())
        # csv_columns = [row['Variabile'].strip() for row in reader if row['Presenza nei dataset da query su www.opencoesione.gov.it'].strip()]

        # reader = csv.DictReader(convert.xls2csv(open(os.path.join(settings.STATIC_ROOT, 'metadati_risultati_ricerca.xls'), 'rb'), sheet='Progetti').splitlines())
        # columns = [row['Variabile'].strip() for row in reader]
        # columns = [{'FINANZ_STATO_FONDO_ROTAZIONE': u'FINANZ_STATO_FONDO_DI_ROTAZIONE', 'FINANZ_STATO_PRIVATO': u'FINANZ_PRIVATO'}.get(c, c) for c in columns]

        # columns = ['COD_LOCALE_PROGETTO', 'CUP', 'OC_TITOLO_PROGETTO', 'QSN_FONDO_COMUNITARIO', 'OC_TEMA_SINTETICO', 'OC_DESCR_FONTE', 'OC_CODICE_PROGRAMMA', 'OC_DESCRIZIONE_PROGRAMMA', 'DESCR_STRUMENTO', 'DESCR_TIPO_STRUMENTO', 'DATA_APPROV_STRUMENTO', 'CUP_DESCR_NATURA', 'CUP_DESCR_SETTORE', 'CUP_DESCR_SOTTOSETTORE', 'CUP_DESCR_CATEGORIA', 'COD_ATECO', 'DESCRIZIONE_ATECO', 'OC_TIPO_PROGETTO', 'FINANZ_UE', 'FINANZ_STATO_FONDO_DI_ROTAZIONE', 'FINANZ_STATO_FSC', 'FINANZ_STATO_PAC', 'FINANZ_STATO_ALTRI_PROVVEDIMENTI', 'FINANZ_REGIONE', 'FINANZ_PROVINCIA', 'FINANZ_COMUNE', 'FINANZ_RISORSE_LIBERATE', 'FINANZ_ALTRO_PUBBLICO', 'FINANZ_STATO_ESTERO', 'FINANZ_PRIVATO', 'FINANZ_DA_REPERIRE', 'FINANZ_TOTALE_PUBBLICO', 'COSTO_RENDICONTABILE_UE', 'IMPEGNI', 'TOT_PAGAMENTI', 'OC_TOT_PAGAMENTI_RENDICONTAB_UE', 'OC_DATA_INIZIO_PREVISTA', 'OC_DATA_FINE_PREVISTA', 'OC_DATA_INIZIO_EFFETTIVA', 'OC_DATA_FINE_EFFETTIVA', 'OC_STATO_PROGETTO', 'DESCR_PROCED_ATTIVAZIONE', 'DESCR_TIPO_PROCED_ATTIVAZIONE', 'DATA_PREVISTA_BANDO_PROC_ATTIV', 'DATA_EFFETTIVA_BANDO_PROC_ATTIV', 'DATA_PREVISTA_FINE_PROC_ATTIV', 'DATA_EFFETTIVA_FINE_PROC_ATTIV', 'DATA_AGGIORNAMENTO', 'SOGGETTI_PROGRAMMATORI', 'SOGGETTI_ATTUATORI', 'AMBITI_TERRITORIALI', 'TERRITORI']
        columns = ['COD_LOCALE_PROGETTO', 'CUP', 'OC_TITOLO_PROGETTO', 'QSN_FONDO_COMUNITARIO', 'OC_TEMA_SINTETICO', 'OC_DESCR_FONTE', 'OC_CODICE_PROGRAMMA', 'OC_DESCRIZIONE_PROGRAMMA', 'DESCR_STRUMENTO', 'DESCR_TIPO_STRUMENTO', 'DATA_APPROV_STRUMENTO', 'CUP_DESCR_NATURA', 'CUP_DESCR_SETTORE', 'CUP_DESCR_SOTTOSETTORE', 'CUP_DESCR_CATEGORIA', 'COD_ATECO', 'DESCRIZIONE_ATECO', 'FINANZ_UE', 'FINANZ_STATO_FONDO_DI_ROTAZIONE', 'FINANZ_STATO_FSC', 'FINANZ_STATO_PAC', 'FINANZ_STATO_ALTRI_PROVVEDIMENTI', 'FINANZ_REGIONE', 'FINANZ_PROVINCIA', 'FINANZ_COMUNE', 'FINANZ_RISORSE_LIBERATE', 'FINANZ_ALTRO_PUBBLICO', 'FINANZ_STATO_ESTERO', 'FINANZ_PRIVATO', 'FINANZ_DA_REPERIRE', 'FINANZ_TOTALE_PUBBLICO', 'COSTO_RENDICONTABILE_UE', 'IMPEGNI', 'TOT_PAGAMENTI', 'OC_TOT_PAGAMENTI_RENDICONTAB_UE', 'OC_DATA_INIZIO_PREVISTA', 'OC_DATA_FINE_PREVISTA', 'OC_DATA_INIZIO_EFFETTIVA', 'OC_DATA_FINE_EFFETTIVA', 'OC_STATO_PROGETTO', 'DESCR_PROCED_ATTIVAZIONE', 'DESCR_TIPO_PROCED_ATTIVAZIONE', 'DATA_PREVISTA_BANDO_PROC_ATTIV', 'DATA_EFFETTIVA_BANDO_PROC_ATTIV', 'DATA_PREVISTA_FINE_PROC_ATTIV', 'DATA_EFFETTIVA_FINE_PROC_ATTIV', 'OC_FLAG_VISUALIZZAZIONE', 'DATA_AGGIORNAMENTO', 'SOGGETTI_PROGRAMMATORI', 'SOGGETTI_ATTUATORI', 'AMBITI_TERRITORIALI', 'TERRITORI']

        extra_columns = OrderedDict([
            # ('OC_TIPO_PROGETTO', 'get_tipo_progetto_display'),
            ('SOGGETTI_PROGRAMMATORI', 'nomi_programmatori'),
            ('SOGGETTI_ATTUATORI', 'nomi_attuatori'),
            ('AMBITI_TERRITORIALI', 'ambiti_territoriali'),
            ('TERRITORI', 'nomi_territori'),
        ])

        results = self.get_results()

        response = HttpResponse(content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename=progetti.csv.zip'

        z = zipfile.ZipFile(response, 'w', zipfile.ZIP_DEFLATED)

        output = StringIO.StringIO()

        writer = utils.UnicodeWriter(output, dialect=utils.excel_semicolon)

        # writer.writerow(csv_columns + extra_columns.keys())
        writer.writerow(columns)

        chunk_size = 10000
        for i in xrange(0, len(results), chunk_size):
            chunked_results = results[i:i + chunk_size]

            objects_by_pk = self._get_objects_by_pk(chunked_results)
            for result in chunked_results:
                try:
                    object = objects_by_pk[result]
                except KeyError:
                    pass
                else:
                    csv_data = json.loads(object.csv_data, object_pairs_hook=OrderedDict)
                    csv_data = {{'COD_DIPE': u'COD_LOCALE_PROGETTO', 'ASSEGNAZIONE_CIPE_AGG': u'FINANZ_TOTALE_PUBBLICO'}.get(k, k): v for k, v in csv_data.items()}  # necessario per assegnazioni CIPE

                    # row = [myformat(csv_data.get(x, '')) for x in csv_columns] + [myformat(getattr(object, x) or '') for x in extra_columns.values()]
                    row = [myformat(getattr(object, extra_columns[c]) or '' if c in extra_columns else csv_data.get(c, '')) for c in columns]

                    writer.writerow(row)

        z.writestr('progetti.csv', output.getvalue())

        z.close()

        return response

    def create_response_old(self):
        """
        Generates a zipped, downloadale CSV file, from search results
        """
        import datetime
        import decimal
        import locale

        locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

        def get_repr(value):
            if callable(value):
                return '{}'.format(value())
            return value

        def get_field(instance, field):
            field_path = field.split('.')
            attr = instance
            for elem in field_path:
                try:
                    attr = getattr(attr, elem)
                except AttributeError:
                    return None
            return attr

        columns = OrderedDict([
            ('COD_LOCALE_PROGETTO', 'codice_locale'),
            ('CUP', 'cup'),
            ('OC_TITOLO_PROGETTO', 'titolo_progetto'),
            ('OC_TEMA_SINTETICO', 'tema.tema_superiore.descrizione'),
            ('CUP_DESCR_NATURA', 'classificazione_azione.classificazione_superiore.descrizione'),
            # ('OC_TIPO_PROGETTO', 'get_tipo_progetto_display'),
            ('FINANZ_UE', 'fin_ue'),
            ('FINANZ_STATO_FONDO_ROTAZIONE', 'fin_stato_fondo_rotazione'),
            ('FINANZ_STATO_FSC', 'fin_stato_fsc'),
            ('FINANZ_STATO_PAC', 'fin_stato_pac'),
            ('FINANZ_STATO_ALTRI_PROVVEDIMENTI', 'fin_stato_altri_provvedimenti'),
            ('FINANZ_REGIONE', 'fin_regione'),
            ('FINANZ_PROVINCIA', 'fin_provincia'),
            ('FINANZ_COMUNE', 'fin_comune'),
            ('FINANZ_ALTRO_PUBBLICO', 'fin_altro_pubblico'),
            ('FINANZ_STATO_ESTERO', 'fin_stato_estero'),
            ('FINANZ_PRIVATO', 'fin_privato'),
            ('FINANZ_DA_REPERIRE', 'fin_da_reperire'),
            ('FINANZ_RISORSE_LIBERATE', 'fin_risorse_liberate'),
            ('FINANZ_TOTALE_PUBBLICO', 'fin_totale_pubblico'),
            ('TOT_PAGAMENTI', 'pagamento'),
            ('QSN_FONDO_COMUNITARIO', 'fondo_comunitario'),
            ('OC_DATA_INIZIO_PREVISTA', 'data_inizio_prevista'),
            ('OC_DATA_FINE_PREVISTA', 'data_fine_prevista'),
            ('OC_DATA_INIZIO_EFFETTIVA', 'data_inizio_effettiva'),
            ('OC_DATA_FINE_EFFETTIVA', 'data_fine_effettiva'),
            ('SOGGETTI_PROGRAMMATORI', 'nomi_programmatori'),
            ('SOGGETTI_ATTUATORI', 'nomi_attuatori'),
            ('AMBITI_TERRITORIALI', 'ambiti_territoriali'),
            ('TERRITORI', 'nomi_territori'),
        ])

        results = self.get_results()

        response = HttpResponse(content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename=progetti.csv.zip'

        z = zipfile.ZipFile(response, 'w', zipfile.ZIP_DEFLATED)

        output = StringIO.StringIO()

        writer = utils.UnicodeWriter(output, dialect=utils.excel_semicolon)

        writer.writerow(columns.keys())

        chunk_size = 10000
        for i in xrange(0, len(results), chunk_size):
            chunked_results = results[i:i + chunk_size]

            # objects_by_pk = self._get_objects_by_pk([result.pk for result in chunked_results])
            objects_by_pk = self._get_objects_by_pk(chunked_results)
            for result in chunked_results:
                # try:
                #     result.object = objects_by_pk[result.pk]
                # except KeyError:
                #     pass
                #
                # object = result.object
                try:
                    object = objects_by_pk[result]
                except KeyError:
                    pass
                else:
                    row = []
                    for fld in columns.values():
                        val = get_repr(get_field(object, fld))

                        try:
                            if val is None:
                                val = ''
                            elif isinstance(val, bool):
                                val = {True: u'Sì', False: u'No'}[val]
                            elif isinstance(val, datetime.date):
                                val = val.strftime('%Y%m%d')
                            elif isinstance(val, decimal.Decimal):
                                val = locale.format('%.2f', val)
                            elif isinstance(val, (list, set)):
                                val = u':::'.join(val)
                            else:
                                val = unicode(val)
                        except ValueError:
                            val = ''

                        row.append(val)

                    writer.writerow(row)

        z.writestr('progetti.csv', output.getvalue())

        z.close()

        return response


class ProgettoLocCSVSearchView(ProgettoSearchView):
    def __init__(self, *args, **kwargs):
        super(ProgettoLocCSVSearchView, self).__init__(*args, **kwargs)
        self.searchqueryset = self.searchqueryset.values_list('pk', flat=True)

    @staticmethod
    def _get_objects_by_pk(pks):
        related = ['territorio_set']
        return {str(key): value for key, value in Progetto.fullobjects.select_related(*related).prefetch_related(*related).in_bulk(pks).items()}

    def create_response(self):
        """
        Generates a zipped, downloadale CSV file, from search results
        """
        results = self.get_results()

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=codici_localita.csv'

        writer = utils.UnicodeWriter(response, dialect=utils.excel_semicolon)

        writer.writerow(['COD_LOCALE_PROGETTO', 'OC_TERRITORIO_PROG', 'COD_COMUNE', 'COD_PROVINCIA', 'COD_REGIONE'])

        chunk_size = 10000
        for i in xrange(0, len(results), chunk_size):
            chunked_results = results[i:i + chunk_size]

            objects_by_pk = self._get_objects_by_pk(chunked_results)
            for result in chunked_results:
                try:
                    object = objects_by_pk[result]
                except KeyError:
                    pass
                else:
                    for territorio in object.territori:
                        writer.writerow([
                            object.codice_locale,
                            territorio.territorio,
                            '{:06d}'.format(int(territorio.cod_com)),
                            '{:03d}'.format(int(territorio.cod_prov)),
                            '{:03d}'.format(int(territorio.cod_reg)),
                        ])

        return response


class SegnalaDescrizioneView(FormView):
    template_name = 'segnalazione/modulo.html'
    form_class = DescrizioneProgettoForm
    success_url = reverse_lazy('progetti_segnalazione_completa')

    def get_context_data(self, **kwargs):
        context = super(SegnalaDescrizioneView, self).get_context_data(**kwargs)

        params = {}
        if 'cup' in self.request.GET:
            params['cup'] = self.request.GET.get('cup')
        elif 'clp' in self.request.GET:
            params['cup'] = self.request.GET.get('clp')

        if params:
            context['progetto'] = Progetto.objects.filter(**params).exists()
        else:
            context['progetto'] = False

        return context

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initials = self.initial.copy()

        initials['is_cipe'] = False

        if 'cup' in self.request.GET:
            initials['cup'] = self.request.GET.get('cup')
        elif 'clp' in self.request.GET:
            initials['cup'] = self.request.GET.get('clp')
            initials['is_cipe'] = True

        return initials

    def form_valid(self, form):
        form.save()
        form.send_mail()

        return super(SegnalaDescrizioneView, self).form_valid(form)


class SegnalazioneDetailView(DetailView):
    context_object_name = 'segnalazione'
    model = SegnalazioneProgetto
    template_name = 'segnalazione/singola.html'


class MonitoraggioASOCListView(ListView):
    model = MonitoraggioASOC

    def get_context_data(self, **kwargs):
        context = super(MonitoraggioASOCListView, self).get_context_data(**kwargs)

        context['data_file'] = OpendataView.get_complete_localfile('progetti_ASOC.csv')
        context['metadata_file'] = OpendataView.get_complete_localfile('metadati_progetti_ASOC.xls')

        context['object_list'] = sorted(context['object_list'].select_related('progetto', 'istituto_comune').order_by('-edizione_asoc'), key=lambda x: (x.istituto_regione.denominazione, x.istituto_provincia.denominazione, x.istituto_comune.denominazione, x.istituto_nome))

        return context
