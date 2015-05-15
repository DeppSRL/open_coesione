import StringIO
import csv
from datetime import date
import json
import zipfile
import os
import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from oc_search.mixins import FacetRangeCostoMixin, FacetRangeDateIntervalsMixin, TerritorioMixin, FacetRangePercPayMixin
from oc_search.views import ExtendedFacetedSearchView
from models import Progetto, ClassificazioneAzione, ProgrammaAsseObiettivo, ProgrammaLineaAzione, PagamentoProgetto
from open_coesione import utils
from open_coesione.views import AccessControlView, AggregatoMixin, XRobotsTagTemplateResponseMixin, cached_context
from progetti.forms import DescrizioneProgettoForm
from progetti.gruppo_programmi import GruppoProgrammi, split_by_type
from progetti.models import Tema, Fonte, SegnalazioneProgetto
from soggetti.models import Soggetto
from territori.models import Territorio


class ProgettoView(XRobotsTagTemplateResponseMixin, AccessControlView, DetailView):
    model = Progetto
    queryset = Progetto.fullobjects.get_query_set()

    def get_x_robots_tag(self):
        return 'noindex' if (self.object.privacy_flag or (not self.object.active_flag)) else False

    def get_context_data(self, **kwargs):
        context = super(ProgettoView, self).get_context_data(**kwargs)

        if self.object.territori:
            numero_collaboratori = 5
            altri_progetti_nei_territori = Progetto.fullobjects.exclude(codice_locale=self.object.codice_locale).nei_territori(self.object.territori).distinct().order_by('-fin_totale_pubblico')
            context['progetti_stesso_tema'] = altri_progetti_nei_territori.con_tema(self.object.tema)[:numero_collaboratori]
            context['progetti_stessa_natura'] = altri_progetti_nei_territori.con_natura(self.object.classificazione_azione)[:numero_collaboratori]
            context['progetti_stessi_attuatori'] = altri_progetti_nei_territori.filter(soggetto_set__in=self.object.attuatori)[:numero_collaboratori]
            context['progetti_stessi_programmatori'] = altri_progetti_nei_territori.filter(soggetto_set__in=self.object.programmatori)[:numero_collaboratori]

        context['total_cost'] = float(self.object.fin_totale_pubblico or 0)
        context['total_cost_paid'] = float(self.object.pagamento or 0)
        context['total_economie'] = float(self.object.economie_totali_pubbliche or 0)

        # calcolo della percentuale del finanziamento erogato
        fin_totale_pubblico_netto = float(self.object.fin_totale_pubblico_netto or self.object.fin_totale_pubblico or 0)
        context['cost_payments_ratio'] = '{0:.0%}'.format(context['total_cost_paid'] / fin_totale_pubblico_netto if fin_totale_pubblico_netto > 0.0 else 0.0)

        context['segnalazioni_pubblicate'] = self.object.segnalazioni

        context['overlapping_projects'] = Progetto.fullobjects.filter(overlapping_projects=self.object)

        return context


class ProgettoSearchView(AccessControlView, ExtendedFacetedSearchView, FacetRangePercPayMixin, FacetRangeCostoMixin, FacetRangeDateIntervalsMixin, TerritorioMixin):
    """
    This view allows faceted search and navigation of a progetto.
    It extends an extended version of the basic FacetedSearchView,
    """
    __name__ = 'ProgettoSearchView'

    PERC_PAY_RANGES = {
        '0-0TO25':   {'qrange': '[* TO 25.0]', 'r_label': 'da 0 al 25%'},
        '1-25TO50':  {'qrange': '[25.001 TO 50.0]', 'r_label': 'dal 25% al 50%'},
        '2-50TO75':  {'qrange': '[50.001 TO 75.0]', 'r_label': 'dal 50% al 75%'},
        '3-75TO100': {'qrange': '[75.00 TO *]', 'r_label': 'oltre il 75%'},
    }

    COST_RANGES = {
        '0-0TO1K':     {'qrange': '[* TO 1000]', 'r_label': 'da 0 a 1.000&euro;'},
        '1-1KTO10K':   {'qrange': '[1000.01 TO 10000]', 'r_label': 'da 1.000 a 10.000&euro;'},
        '2-10KTO100K': {'qrange': '[10000.01 TO 100000]', 'r_label': 'da 10.000 a 100.000&euro;'},
        '3-100KTOINF': {'qrange': '[100000.01 TO *]', 'r_label': 'oltre 100.000&euro;'},
    }

    DATE_INTERVALS_RANGES = {
        '2013':  {'qrange': '[2013-01-01T00:00:00Z TO *]', 'r_label': '2013'},
        '2012':  {'qrange': '[2012-01-01T00:00:00Z TO 2012-12-31T23:59:59Z]', 'r_label': '2012'},
        '2011':  {'qrange': '[2011-01-01T00:00:00Z TO 2011-12-31T23:59:59Z]', 'r_label': '2011'},
        '2010':  {'qrange': '[2010-01-01T00:00:00Z TO 2010-12-31T23:59:59Z]', 'r_label': '2010'},
        '2009':  {'qrange': '[2009-01-01T00:00:00Z TO 2009-12-31T23:59:59Z]', 'r_label': '2009'},
        '2008':  {'qrange': '[2008-01-01T00:00:00Z TO 2008-12-31T23:59:59Z]', 'r_label': '2008'},
        '2007':  {'qrange': '[2007-01-01T00:00:00Z TO 2007-12-31T23:59:59Z]', 'r_label': '2007'},
        'early': {'qrange': '[1970-01-02T00:00:00Z TO 2006-12-31T23:59:59Z]', 'r_label': 'prima del 2007'},
        'nd':    {'qrange': '[* TO 1970-01-01T00:00:00Z]', 'r_label': 'non disponibile'}
    }

    # def __init__(self, *args, **kwargs):
    #     # Needed to switch out the default form class.
    #     if kwargs.get('form_class') is None:
    #         kwargs['form_class'] = RangeFacetedSearchForm
    #
    #     super(ProgettoSearchView, self).__init__(*args, **kwargs)

    @staticmethod
    def _get_objects_by_pk(pks):
        related = ['territorio_set', 'tema__tema_superiore', 'classificazione_azione__classificazione_superiore']
        return Progetto.fullobjects.select_related(*related).prefetch_related(*related).in_bulk(pks)

    def build_form(self, form_kwargs=None):
        # the is_active:1 facet is selected by default
        # and is substituted by is_active:0 when explicitly requested
        # by clicking on the 'See archive' link in the progetti page
        if 'is_active:0' in self.request.GET.getlist('selected_facets'):
            form_kwargs = {'selected_facets': ['is_active:0']}
        else:
            form_kwargs = {'selected_facets': ['is_active:1']}

        return super(ProgettoSearchView, self).build_form(form_kwargs)

    def _get_extended_selected_facets(self):
        """
        modifies the extended_selected_facets, adding correct labels for this view
        works directly on the extended_selected_facets dictionary
        """
        extended_selected_facets = super(ProgettoSearchView, self)._get_extended_selected_facets()

        # this comes from the Mixins
        extended_selected_facets = self.add_perc_pay_extended_selected_facets(extended_selected_facets)
        extended_selected_facets = self.add_costo_extended_selected_facets(extended_selected_facets)
        extended_selected_facets = self.add_territorio_extended_selected_facets(extended_selected_facets)
        extended_selected_facets = self.add_date_interval_extended_selected_facets(extended_selected_facets)

        return extended_selected_facets

    def extra_context(self):
        """
        Add extra content here, when needed
        """
        extra = super(ProgettoSearchView, self).extra_context()

        territorio_com = self.request.GET.get('territorio_com', '')
        territorio_prov = self.request.GET.get('territorio_prov', '')
        territorio_reg = self.request.GET.get('territorio_reg', '')
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
        elif territorio_reg and territorio_reg == '0':
            extra['territorio'] = Territorio.objects.get(
                territorio=Territorio.TERRITORIO.N,
                cod_reg=territorio_reg
            ).nome

        fonte_fin = self.request.GET.get('fonte_fin', None)
        if fonte_fin:
            try:
                extra['fonte_fin'] = ProgrammaAsseObiettivo.objects.get(pk=fonte_fin)
            except ObjectDoesNotExist:
                try:
                    extra['fonte_fin'] = ProgrammaLineaAzione.objects.get(pk=fonte_fin)
                except ObjectDoesNotExist:
                    pass

        programmi_slug = self.request.GET.get('gruppo_programmi', None)
        if programmi_slug:
            try:
                extra['gruppo_programmi'] = GruppoProgrammi(codice=programmi_slug)
            except:
                pass

        soggetto_slug = self.request.GET.get('soggetto', None)
        if soggetto_slug:
            try:
                extra['soggetto'] = Soggetto.objects.get(slug=soggetto_slug)
            except ObjectDoesNotExist:
                pass

        # get data about perc pay and n_progetti range facets
        extra['facet_queries_perc_pay'] = self.get_custom_facet_queries_perc_pay()

        # get data about custom costo and n_progetti range facets
        extra['facet_queries_costo'] = self.get_custom_facet_queries_costo()

        # get data about custom date range facets
        extra['facet_queries_date'] = self.get_custom_facet_queries_date()

        # definizione struttura dati per visualizzazione faccette natura
        extra['natura'] = {
            'descrizione': {},
            'short_label': {}
        }
        for c in ClassificazioneAzione.objects.filter(tipo_classificazione='natura'):
            if c.codice != ' ':
                codice = c.codice
            else:
                codice = 'ND'
            extra['natura']['descrizione'][codice] = c.descrizione
            extra['natura']['short_label'][codice] = c.short_label

        # definizione struttura dati per visualizzazione faccette tema
        extra['tema'] = {
            'descrizione': {},
            'short_label': {}
        }
        for c in Tema.objects.principali():
            if c.codice != ' ':
                codice = c.codice
            else:
                codice = 'ND'

            extra['tema']['descrizione'][codice] = c.descrizione
            extra['tema']['short_label'][codice] = c.short_label

        # definizione struttura dati per visualizzazione faccette tipo progetto
        extra['tipo_progetto'] = {
            'descrizione': {},
            'short_label': {}
        }
        for c in Progetto.TIPI_PROGETTO:
            codice, descrizione = c

            extra['tipo_progetto']['descrizione'][codice] = descrizione
            extra['tipo_progetto']['short_label'][codice] = descrizione

        extra['base_url'] = reverse('progetti_search') + '?' + extra['params'].urlencode()

        # definizione struttura dati per visualizzazione faccette fonte
        extra['fonte'] = {
            'descrizione': {},
            'short_label': {}
        }
        for c in Fonte.objects.all():
            extra['fonte']['descrizione'][c.codice] = c.descrizione
            extra['fonte']['short_label'][c.codice] = c.short_label

        paginator = Paginator(self.results, 10)
        page = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page_obj = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page_obj = paginator.page(paginator.num_pages)

        selected_facets = self.request.GET.getlist('selected_facets')
        extra['search_within_non_active'] = 'is_active:0' in selected_facets

        extra['paginator'] = paginator
        extra['page_obj'] = page_obj

        extra['n_max_downloadable'] = settings.N_MAX_DOWNLOADABLE_RESULTS

        extra['perc_pay_facets_enabled'] = getattr(settings, 'PERC_PAY_FACETS_ENABLED', False)
        return extra


class BaseProgrammaView(AccessControlView, AggregatoMixin, TemplateView):
    @cached_context
    def get_cached_context_data(self, programmi):
        logger = logging.getLogger('console')

        context = {}

        logger.debug('get_aggregate_data start')
        context = self.get_aggregate_data(context, programmi=programmi)

        context['numero_soggetti'] = Soggetto.objects.count()

        logger.debug('top_progetti_per_costo start')
        context['top_progetti_per_costo'] = Progetto.objects.con_programmi(programmi).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]

        logger.debug('territori_piu_finanziati_pro_capite start')

        #discriminate between ProgrammaAsseObiettivo and ProgrammaLineaAzione
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

        context['ultimi_progetti_conclusi'] = Progetto.objects.filter(privacy_flag=False).conclusi().con_programmi(programmi)[:5]

        return context


class ProgrammiView(BaseProgrammaView):
    template_name = 'progetti/programmi_detail.html'

    def get_object(self):
        return GruppoProgrammi(codice=self.kwargs.get('slug'))

    @cached_context
    def get_cached_context_data(self, programmi):
        context = super(ProgrammiView, self).get_cached_context_data(programmi=programmi)

        if self.kwargs.get('slug') in ('ue-fesr', 'ue-fse'):
            from csvkit import convert
            from open_coesione.views import OpendataView

            data_pagamenti_per_programma = date(2014, 12, 31)

            logger = logging.getLogger('console')

            # dotazioni_totali = csv.DictReader(open(OpendataView.get_latest_localfile('Dotazioni_Certificazioni.csv')), delimiter=';')
            # dotazioni_totali.fieldnames = [field.strip() for field in dotazioni_totali.fieldnames]
            # dotazioni_totali = list(dotazioni_totali)
            dotazioni_totali = list(csv.DictReader(convert.xls2csv(open(OpendataView.get_latest_localfile('Dotazioni_Certificazioni.xls'), 'rb')).splitlines()))

            for trend in ('conv', 'cro'):
                programmi_codici = [programma.codice for programma in programmi if ' {0} '.format(trend) in programma.descrizione.lower()]

                logger.debug('pagamenti_per_anno_{0} start'.format(trend))

                pagamenti_per_anno = PagamentoProgetto.objects.filter(data__day=31, data__month=12, progetto__active_flag=True, progetto__programma_asse_obiettivo__classificazione_superiore__classificazione_superiore__codice__in=programmi_codici).values('data').annotate(ammontare=Sum('ammontare_rendicontabile_ue')).order_by('data')

                dotazioni_totali_per_anno = {pagamento['data'].year: 0 for pagamento in pagamenti_per_anno}
                for row in dotazioni_totali:
                    if row['DPS_CODICE_PROGRAMMA'].strip() in programmi_codici:
                        for anno in dotazioni_totali_per_anno:
                            data = '{0}1231'.format(max(anno, 2009))  # i dati delle dotazioni totali partono dal 2009; per gli anni precedenti valgono i dati del 2009
                            try:
                                valore = row['DOTAZIONE TOTALE PROGRAMMA POST PAC {0}'.format(data)]
                            except KeyError:
                                valore = row['DOTAZIONE TOTALE PROGRAMMA {0}'.format(data)]

                            # dotazioni_totali_per_anno[anno] += float(valore.strip().replace('.', '').replace(',', '.'))
                            dotazioni_totali_per_anno[anno] += float(valore)

                context['pagamenti_per_anno_{0}'.format(trend)] = [{'year': pagamento['data'].year, 'total_amount': dotazioni_totali_per_anno[pagamento['data'].year], 'paid_amount': pagamento['ammontare'] or 0} for pagamento in pagamenti_per_anno]

                logger.debug('pagamenti_per_programma_{0} start'.format(trend))

                programmi_con_pagamenti = ProgrammaAsseObiettivo.objects.filter(classificazione_set__classificazione_set__progetto_set__pagamentoprogetto_set__data=data_pagamenti_per_programma, classificazione_set__classificazione_set__progetto_set__active_flag=True, codice__in=programmi_codici).values('descrizione', 'codice').annotate(ammontare=Sum('classificazione_set__classificazione_set__progetto_set__pagamentoprogetto_set__ammontare_rendicontabile_ue')).order_by('descrizione')

                dotazioni_totali_per_programma = {}
                for row in dotazioni_totali:
                    programma = row['DPS_CODICE_PROGRAMMA'].strip()
                    if programma in programmi_codici:
                        data = data_pagamenti_per_programma.strftime('%Y%m%d')
                        try:
                            valore = row['DOTAZIONE TOTALE PROGRAMMA POST PAC {0}'.format(data)]
                        except KeyError:
                            valore = row['DOTAZIONE TOTALE PROGRAMMA {0}'.format(data)]

                        dotazioni_totali_per_programma[programma] = float(valore)

                context['pagamenti_per_programma_{0}'.format(trend)] = [{'program': programma['descrizione'], 'total_amount': dotazioni_totali_per_programma[programma['codice']], 'paid_amount': programma['ammontare']} for programma in programmi_con_pagamenti]

            pagamenti_per_anno_tutti = {}
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

        context['map_selector'] = 'gruppo-programmi/{0}/'.format(self.kwargs['slug'])

        context['gruppo_programmi'] = gruppo_programmi

        return context


class ProgrammaView(BaseProgrammaView):
    template_name = 'progetti/programma_detail.html'

    def get_object(self):
        try:
            return ProgrammaAsseObiettivo.objects.get(pk=self.kwargs.get('codice'))
        except ObjectDoesNotExist:
            return ProgrammaLineaAzione.objects.get(pk=self.kwargs.get('codice'))

    def get_context_data(self, **kwargs):
        try:
            programma = self.get_object()
        except:
            raise Http404

        context = super(ProgrammaView, self).get_context_data(programmi=[programma], **kwargs)

        context['map_selector'] = 'programmi/{0}/'.format(self.kwargs['codice'])

        context['programma'] = programma

        return context


class ClassificazioneAzioneView(AccessControlView, AggregatoMixin, DetailView):
    context_object_name = 'tipologia'
    model = ClassificazioneAzione

    @cached_context
    def get_cached_context_data(self):
        logger = logging.getLogger('console')

        context = {}

        logger.debug('get_aggregate_data start')
        context = self.get_aggregate_data(context, classificazione=self.object)

        context['numero_soggetti'] = Soggetto.objects.count()
        context['map_selector'] = 'nature/{0}/'.format(self.kwargs['slug'])

        logger.debug('top_progetti_per_costo start')
        context['top_progetti_per_costo'] = Progetto.objects.con_natura(self.object).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]

        logger.debug('territori_piu_finanziati_pro_capite start')
        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(
            filters={
                'progetto__classificazione_azione__classificazione_superiore': self.object
            }
        )

        return context

    def get_context_data(self, **kwargs):
        context = super(ClassificazioneAzioneView, self).get_context_data(**kwargs)

        context.update(self.get_cached_context_data())

        context['ultimi_progetti_conclusi'] = Progetto.objects.filter(privacy_flag=False).conclusi().con_natura(self.object)[:5]

        return context


class TemaView(AccessControlView, AggregatoMixin, DetailView):
    model = Tema

    @cached_context
    def get_cached_context_data(self):
        logger = logging.getLogger('console')

        context = {}

        logger.debug('get_aggregate_data start')
        context = self.get_aggregate_data(context, tema=self.object)

        context['numero_soggetti'] = Soggetto.objects.count()
        context['map_selector'] = 'temi/{0}/'.format(self.kwargs['slug'])

        logger.debug('top_progetti_per_costo start')
        context['top_progetti_per_costo'] = Progetto.objects.con_tema(self.object).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]

        logger.debug('territori_piu_finanziati_pro_capite start')
        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(
            filters={
                'progetto__tema__tema_superiore': self.object
            }
        )

        return context

    def get_context_data(self, **kwargs):
        context = super(TemaView, self).get_context_data(**kwargs)

        context.update(self.get_cached_context_data())

        context['ultimi_progetti_conclusi'] = Progetto.objects.filter(privacy_flag=False).conclusi().con_tema(self.object)[:5]

        context['lista_indici_tema'] = []
        with open(os.path.join(settings.STATIC_ROOT, 'csv/indicatori/{0}.csv'.format(self.object.codice))) as csvfile:
            reader = csv.DictReader(csvfile)
            for line in reader:
                context['lista_indici_tema'].append(line)

        return context


class BaseCSVView(AggregatoMixin, DetailView):
    filter_field = None

    @staticmethod
    def get_first_row():
        return ['Comune', 'Provincia', 'Finanziamento pro capite']

    def get_csv_filename(self):
        return '{0}_pro_capite'.format(self.kwargs.get('slug', 'all'))

    def write_csv(self, response):
        writer = utils.UnicodeWriter(response, dialect=utils.excel_semicolon)
        writer.writerow(self.get_first_row())
        comuni = list(Territorio.objects.comuni().defer('geom'))
        provincie = dict([(t['cod_prov'], t['denominazione']) for t in Territorio.objects.provincie().values('cod_prov', 'denominazione')])
        comuni_con_pro_capite = self.top_comuni_pro_capite(filters={self.filter_field: self.object}, qnt=None)

        for city in comuni_con_pro_capite:
            writer.writerow([
                unicode(city.denominazione),
                unicode(provincie[city.cod_prov]),
                '{0:.2f}'.format(city.totale / city.popolazione_totale if city.popolazione_totale else .0).replace('.', ',')
            ])
            comuni.remove(city)

        for city in comuni:
            writer.writerow([
                unicode(city.denominazione),
                unicode(provincie[city.cod_prov]),
                '{0:.2f}'.format(.0).replace('.', ',')
            ])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename={0}.csv'.format(self.get_csv_filename())

        self.write_csv(response)

        return response


class ClassificazioneAzioneCSVView(BaseCSVView):
    model = ClassificazioneAzione
    filter_field = 'progetto__classificazione_azione__classificazione_superiore'


class TemaCSVView(BaseCSVView):
    model = Tema
    filter_field = 'progetto__tema__tema_superiore'


class CSVSearchResultsWriterMixin(object):
    """
    Mixin used by CSV - related SearchView classes, to add results as csv rows to a CSV writer
    Both the results and the writer objects must have been correctly defined,
    before invoking the write_search_results method.
    """
    @staticmethod
    def write_projects_localisations_search_results(results, writer):
        """
        Writes all results of a search query set into a CSV writer.
        """
        writer.writerow([
            'COD_LOCALE_PROGETTO',
            'OC_TERRITORIO_PROG', 'COD_COMUNE', 'COD_PROVINCIA', 'COD_REGIONE'
        ])
        for r in results:

            if r.territorio_com is not None:
                territori_codici = zip(
                    r.territorio_tipo,
                    r.territorio_com,
                    r.territorio_prov,
                    r.territorio_reg
                )
                for t in territori_codici:
                    writer.writerow([
                        unicode(r.clp).encode('latin1'),
                        t[0],
                        '%06d' % int(t[1]),
                        '%03d' % int(t[2]),
                        t[3]
                    ])

    @staticmethod
    def write_projects_search_results(results, writer):
        """
        Writes all results of a search query set into a CSV writer.
        """

        import locale
        locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

        writer.writerow([
            'COD_LOCALE_PROGETTO', 'CUP',
            'OC_TITOLO_PROGETTO',
            'OC_TEMA_SINTETICO', 'CUP_DESCR_NATURA',
            'OC_TIPO_PROGETTO',
            'FINANZ_UE',
            'FINANZ_STATO_FONDO_ROTAZIONE', 'FINANZ_STATO_FSC', 'FINANZ_STATO_PAC', 'FINANZ_STATO_ALTRI_PROVVEDIMENTI',
            'FINANZ_REGIONE', 'FINANZ_PROVINCIA', 'FINANZ_COMUNE',
            'FINANZ_ALTRO_PUBBLICO', 'FINANZ_STATO_ESTERO',
            'FINANZ_PRIVATO', 'FINANZ_DA_REPERIRE', 'FINANZ_RISORSE_LIBERATE',
            'FINANZ_TOTALE_PUBBLICO',
            'TOT_PAGAMENTI',
            'QSN_FONDO_COMUNITARIO',
            'OC_DATA_INIZIO_PREVISTA', 'OC_DATA_FINE_PREVISTA',
            'OC_DATA_INIZIO_EFFETTIVA', 'OC_DATA_FINE_EFFETTIVA',
            'SOGGETTI_PROGRAMMATORI', 'SOGGETTI_ATTUATORI',
            'AMBITI_TERRITORIALI', 'TERRITORI'
        ])

        separator = u':::'

        for r in results:
            soggetti_programmatori = ''
            if r.soggetti_programmatori:
                soggetti_programmatori = separator.join(list(r.soggetti_programmatori)).encode('latin1', 'ignore')

            soggetti_attuatori = ''
            if r.soggetti_attuatori:
                soggetti_attuatori = separator.join(list(r.soggetti_attuatori)).encode('latin1', 'ignore')

            ambiti = ''
            if r.ambiti_territoriali:
                ambiti = separator.join(list(r.ambiti_territoriali)).encode('latin1', 'ignore')

            territori = ''
            if r.territori:
                territori = separator.join(list(r.territori)).encode('latin1', 'ignore')

            writer.writerow([
                unicode(r.clp).encode('latin1', 'ignore'), r.cup,
                unicode(r.titolo).encode('latin1', 'ignore'),
                unicode(r.tema_descr).encode('latin1', 'ignore'),
                unicode(r.natura_descr).encode('latin1', 'ignore'),
                unicode(dict(Progetto.TIPI_PROGETTO)[r.tipo_progetto]).encode('latin1', 'ignore'),
                locale.format('%.2f', r.fin_ue) if r.fin_ue is not None else '',
                locale.format('%.2f', r.fin_stato_fondo_rotazione) if r.fin_stato_fondo_rotazione is not None else '',
                locale.format('%.2f', r.fin_stato_fsc) if r.fin_stato_fsc is not None else '',
                locale.format('%.2f', r.fin_stato_pac) if r.fin_stato_pac is not None else '',
                locale.format('%.2f', r.fin_stato_altri_provvedimenti) if r.fin_stato_altri_provvedimenti is not None else '',
                locale.format('%.2f', r.fin_regione) if r.fin_regione is not None else '',
                locale.format('%.2f', r.fin_provincia) if r.fin_provincia is not None else '',
                locale.format('%.2f', r.fin_comune) if r.fin_comune is not None else '',
                locale.format('%.2f', r.fin_altro_pubblico) if r.fin_altro_pubblico is not None else '',
                locale.format('%.2f', r.fin_stato_estero) if r.fin_stato_estero is not None else '',
                locale.format('%.2f', r.fin_privato) if r.fin_privato is not None else '',
                locale.format('%.2f', r.fin_da_reperire) if r.fin_da_reperire is not None else '',
                locale.format('%.2f', r.fin_risorse_liberate) if r.fin_risorse_liberate is not None else '',
                locale.format('%.2f', r.fin_totale_pubblico) if r.fin_totale_pubblico is not None else '',
                locale.format('%.2f', r.pagamento) if r.pagamento is not None else '',
                unicode(r.fondo).encode('latin1', 'ignore'),
                r.data_inizio_prevista.strftime('%Y%m%d') if r.data_inizio_prevista is not None else '',
                r.data_inizio_effettiva.strftime('%Y%m%d') if r.data_inizio_effettiva is not None else '',
                r.data_fine_prevista.strftime('%Y%m%d') if r.data_fine_prevista is not None else '',
                r.data_fine_effettiva.strftime('%Y%m%d') if r.data_fine_effettiva is not None else '',
                soggetti_programmatori,
                soggetti_attuatori,
                ambiti,
                territori
            ])


class ProgettoLocCSVPreviewSearchView(ProgettoSearchView, CSVSearchResultsWriterMixin):
    def create_response(self):
        """
        Generates a CSV text preview (limited to 50000 items) for search results
        """
        results = self.get_results()[0:5000]

        # send CSV output as plain text, to view it in the browser
        response = HttpResponse(mimetype='text/plain')

        csv.register_dialect('opencoesione', delimiter=';', quoting=csv.QUOTE_ALL)
        writer = csv.writer(response, dialect='opencoesione')
        self.write_projects_localisations_search_results(results, writer)
        return response


class ProgettoCSVPreviewSearchView(ProgettoSearchView, CSVSearchResultsWriterMixin):
    def create_response(self):
        """
        Generates a CSV text preview (limited to 50000 items) for search results
        """
        results = self.get_results()[0:5000]

        # send CSV output as plain text, to view it in the browser
        response = HttpResponse(mimetype='text/plain')

        csv.register_dialect('opencoesione', delimiter=';', quoting=csv.QUOTE_ALL)
        writer = csv.writer(response, dialect='opencoesione')
        self.write_projects_search_results(results, writer)
        return response


class ProgettoCSVSearchView(ProgettoSearchView, CSVSearchResultsWriterMixin):
    def create_response(self):
        """
        Generates a zipped, downloadale CSV file, from search results
        """
        results = self.get_results()

        csv.register_dialect('opencoesione', delimiter=';', quoting=csv.QUOTE_ALL)

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=progetti.csv'

        # add progetti csv to zip stream
        writer = csv.writer(response, dialect='opencoesione')
        self.write_projects_search_results(results, writer)

        # send response
        return response


class ProgettoLocCSVSearchView(ProgettoSearchView, CSVSearchResultsWriterMixin):
    def create_response(self):
        """
        Generates a zipped, downloadale CSV file, from search results
        """
        results = self.get_results()

        csv.register_dialect('opencoesione', delimiter=';', quoting=csv.QUOTE_ALL)

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=codici_localita.csv'

        # add progetti csv to zip stream
        writer = csv.writer(response, dialect='opencoesione')
        self.write_projects_localisations_search_results(results, writer)

        # send response
        return response


class ProgettoFullCSVSearchView(ProgettoSearchView, CSVSearchResultsWriterMixin):
    def create_response(self):
        """
        Generates a zipped, downloadale CSV file, from search results
        """
        results = self.get_results()

        csv.register_dialect('opencoesione', delimiter=';', quoting=csv.QUOTE_ALL)

        response = HttpResponse(mimetype='application/zip')
        response['Content-Disposition'] = 'attachment; filename=opencoesione_risultati.csv.zip'

        # define zipped stream as response
        z = zipfile.ZipFile(response, 'w')   # write zip to response

        # add progetti csv to zip stream
        output = StringIO.StringIO()
        writer = csv.writer(output, dialect='opencoesione')
        self.write_projects_search_results(results, writer)
        z.writestr('progetti.csv', output.getvalue())  # write csv file to zip

        # add localizzazioni csv to zip stream
        output = StringIO.StringIO()
        writer = csv.writer(output, dialect='opencoesione')
        self.write_projects_localisations_search_results(results, writer)
        z.writestr('localizzazioni.csv', output.getvalue())  # write csv file to zip

        # add metadati content to zip stream
        output = StringIO.StringIO()
        f = open(os.path.join(settings.REPO_ROOT, 'dati', 'metadati_search_results.xls'), 'rb')
        output.write(f.read())
        z.writestr('metadati.xls', output.getvalue())

        # send response
        return response


# TODO: serialization of complex JSON objects need to be tackled with proper tools
class ProgettoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__


class ProgettoJSONSearchView(ProgettoSearchView):
    def create_response(self):
        """
        Generates a CSV text preview (limited to 500 items) for search results
        """
        results = [r.object for r in self.get_results()]

        # send JSON out as plain text
        response = HttpResponse(json.dumps(results, cls=ProgettoJSONEncoder), mimetype='text/plain')

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
            try:
                context['progetto'] = Progetto.objects.get(**params)
            except Progetto.DoesNotExist:
                pass
            except Progetto.MultipleObjectsReturned:
                pass
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
