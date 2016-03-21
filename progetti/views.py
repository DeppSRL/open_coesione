# -*- coding: utf-8 -*-
import StringIO
from collections import OrderedDict
import csv
from datetime import date
import zipfile
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
from models import Progetto, ClassificazioneAzione, ProgrammaAsseObiettivo, ProgrammaLineaAzione, PagamentoProgetto, Ruolo
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
        '3-100KTO10M': {'qrange': '[100000.01 TO 10000000]', 'r_label': 'da 100.000 a 10.000.000&euro;'},
        '4-10MTOINF':  {'qrange': '[10000001 TO *]', 'r_label': 'oltre 10.000.000&euro;'},
    }

    DATE_INTERVALS_RANGES = {
        '2015':  {'qrange': '[2015-01-01T00:00:00Z TO *]', 'r_label': '2015'},
        '2014':  {'qrange': '[2014-01-01T00:00:00Z TO 2014-12-31T23:59:59Z]', 'r_label': '2014'},
        '2013':  {'qrange': '[2013-01-01T00:00:00Z TO 2013-12-31T23:59:59Z]', 'r_label': '2013'},
        '2012':  {'qrange': '[2012-01-01T00:00:00Z TO 2012-12-31T23:59:59Z]', 'r_label': '2012'},
        '2011':  {'qrange': '[2011-01-01T00:00:00Z TO 2011-12-31T23:59:59Z]', 'r_label': '2011'},
        '2010':  {'qrange': '[2010-01-01T00:00:00Z TO 2010-12-31T23:59:59Z]', 'r_label': '2010'},
        '2009':  {'qrange': '[2009-01-01T00:00:00Z TO 2009-12-31T23:59:59Z]', 'r_label': '2009'},
        '2008':  {'qrange': '[2008-01-01T00:00:00Z TO 2008-12-31T23:59:59Z]', 'r_label': '2008'},
        '2007':  {'qrange': '[2007-01-01T00:00:00Z TO 2007-12-31T23:59:59Z]', 'r_label': '2007'},
        'early': {'qrange': '[1970-01-02T00:00:00Z TO 2006-12-31T23:59:59Z]', 'r_label': 'prima del 2007'},
        'nd':    {'qrange': '[* TO 1970-01-01T00:00:00Z]', 'r_label': 'non disponibile'}
    }

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

        # territorio_com = self.request.GET.get('territorio_com')
        # territorio_prov = self.request.GET.get('territorio_prov')
        # territorio_reg = self.request.GET.get('territorio_reg')
        # if territorio_com and territorio_com != '0':
        #     extra['territorio'] = Territorio.objects.get(
        #         territorio=Territorio.TERRITORIO.C,
        #         cod_com=territorio_com
        #     ).nome
        # elif territorio_prov and territorio_prov != '0':
        #     extra['territorio'] = Territorio.objects.get(
        #         territorio=Territorio.TERRITORIO.P,
        #         cod_prov=territorio_prov
        #     ).nome_con_provincia
        # elif territorio_reg:
        #     extra['territorio'] = Territorio.objects.get(
        #         territorio__in=(Territorio.TERRITORIO.E, Territorio.TERRITORIO.N, Territorio.TERRITORIO.R),
        #         cod_reg=territorio_reg
        #     ).nome

        fonte_fin = self.request.GET.get('fonte_fin')
        if fonte_fin:
            try:
                extra['fonte_fin'] = ProgrammaAsseObiettivo.objects.get(pk=fonte_fin)
            except ObjectDoesNotExist:
                try:
                    extra['fonte_fin'] = ProgrammaLineaAzione.objects.get(pk=fonte_fin)
                except ObjectDoesNotExist:
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
            except ObjectDoesNotExist:
                pass
            else:
                soggetto_ruolo = self.request.GET.get('ruolo')
                if soggetto_ruolo:
                    extra['ruolo'] = '/'.join(sorted(set(dict(Ruolo.RUOLO).get(r, '') for r in soggetto_ruolo))).strip('/')

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

        # definizione struttura dati per visualizzazione faccette fonte
        extra['fonte'] = {
            'descrizione': {},
            'short_label': {}
        }
        for c in Fonte.objects.all():
            extra['fonte']['descrizione'][c.codice] = c.descrizione
            extra['fonte']['short_label'][c.codice] = c.short_label

        # definizione struttura dati per visualizzazione faccette stato progetto
        extra['stato_progetto'] = {
            'descrizione': {},
            'short_label': {}
        }
        for c in Progetto.STATO:
            codice, descrizione = c

            extra['stato_progetto']['descrizione'][codice] = descrizione
            extra['stato_progetto']['short_label'][codice] = descrizione

        extra['base_url'] = reverse('progetti_search') + '?' + extra['params'].urlencode()

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

        extra['facets']['fields']['stato_progetto']['counts'] = sorted(extra['facets']['fields']['stato_progetto']['counts'], key=lambda x: x[0], reverse=True)

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
        context['top_progetti_per_costo'] = Progetto.objects.no_privacy().con_programmi(programmi).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]

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

        context['ultimi_progetti_conclusi'] = Progetto.objects.no_privacy().con_programmi(programmi).conclusi()[:5]

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

            data_pagamenti_per_programma = date(2015, 12, 31)

            logger = logging.getLogger('console')

            # dotazioni_totali = list(csv.DictReader(convert.xls2csv(open(OpendataView.get_latest_localfile('Dotazioni_Certificazioni.xls'), 'rb')).splitlines()))
            dotazioni_totali = list(csv.DictReader(convert.xls2csv(open(OpendataView.get_latest_localfile('Target_Certificato_Pagamenti.xls'), 'rb'), sheet='Target spesa cert ammessi va').splitlines()))  ##########

            for trend in ('conv', 'cro'):
                programmi_codici = [programma.codice for programma in programmi if ' {} '.format(trend) in programma.descrizione.lower()]

                logger.debug('pagamenti_per_anno_{} start'.format(trend))

                progetti = Progetto.objects.filter(programma_asse_obiettivo__classificazione_superiore__classificazione_superiore__codice__in=programmi_codici)
                pagamenti_per_anno = PagamentoProgetto.objects.filter(data__day=31, data__month=12, progetto__in=progetti).values('data').annotate(ammontare=Sum('ammontare_rendicontabile_ue')).order_by('data')
                # pagamenti_per_anno = PagamentoProgetto.objects.filter(data__day=31, data__month=12, progetto__active_flag=True, progetto__programma_asse_obiettivo__classificazione_superiore__classificazione_superiore__codice__in=programmi_codici).values('data').annotate(ammontare=Sum('ammontare_rendicontabile_ue')).order_by('data')

                pagamenti_2015 = 0  ##########
                dotazioni_totali_2015 = 0  #######

                dotazioni_totali_per_anno = {pagamento['data'].year: 0 for pagamento in pagamenti_per_anno}
                for row in dotazioni_totali:
                    # programma_codice = row['OC_CODICE_PROGRAMMA']
                    programma_codice = row['DPS_CODICE_PROGRAMMA']  ###########
                    if programma_codice in programmi_codici:
                        pagamenti_2015 += float(row['pagamenti ammessi 20151231'])  ########
                        dotazioni_totali_2015 += float(row['DOTAZIONE TOTALE PROGRAMMA POST PAC 20151231'])  ########

                        for anno in dotazioni_totali_per_anno:
                            # data = '{}1231'.format(max(anno, 2009))  # i dati delle dotazioni totali partono dal 2009; per gli anni precedenti valgono i dati del 2009
                            data = '{}1231'.format(max(anno, 2010))  ##############
                            try:
                                valore = row['DOTAZIONE TOTALE PROGRAMMA POST PAC {}'.format(data)]
                            except KeyError:
                                valore = row['DOTAZIONE TOTALE PROGRAMMA {}'.format(data)]

                            dotazioni_totali_per_anno[anno] += float(valore)

                context['pagamenti_per_anno_{}'.format(trend)] = [{'year': pagamento['data'].year, 'total_amount': dotazioni_totali_per_anno[pagamento['data'].year], 'paid_amount': pagamento['ammontare'] or 0} for pagamento in pagamenti_per_anno]
                context['pagamenti_per_anno_{}'.format(trend)] = [x for x in context['pagamenti_per_anno_{}'.format(trend)] if x['year'] != 2006]  ###########
                context['pagamenti_per_anno_{}'.format(trend)].append({'year': 2015, 'total_amount': dotazioni_totali_2015, 'paid_amount': pagamenti_2015})  ##########

                logger.debug('pagamenti_per_programma_{} start'.format(trend))

                # programmi_con_pagamenti = ProgrammaAsseObiettivo.objects.filter(classificazione_set__classificazione_set__progetto_set__pagamentoprogetto_set__data=data_pagamenti_per_programma, classificazione_set__classificazione_set__progetto_set__active_flag=True, codice__in=programmi_codici).values('descrizione', 'codice').annotate(ammontare=Sum('classificazione_set__classificazione_set__progetto_set__pagamentoprogetto_set__ammontare_rendicontabile_ue')).order_by('descrizione')
                programmi_senza_pagamenti = ProgrammaAsseObiettivo.objects.filter(classificazione_set__classificazione_set__progetto_set__active_flag=True, codice__in=programmi_codici).distinct().values('descrizione', 'codice').order_by('descrizione')  ##############

                dotazioni_totali_per_programma = {}
                pagamenti_per_programma = {}  ##########
                for row in dotazioni_totali:
                    # programma_codice = row['OC_CODICE_PROGRAMMA']
                    programma_codice = row['DPS_CODICE_PROGRAMMA']  ###########
                    if programma_codice in programmi_codici:
                        data = data_pagamenti_per_programma.strftime('%Y%m%d')
                        try:
                            valore = row['DOTAZIONE TOTALE PROGRAMMA POST PAC {}'.format(data)]
                        except KeyError:
                            valore = row['DOTAZIONE TOTALE PROGRAMMA {}'.format(data)]

                        dotazioni_totali_per_programma[programma_codice] = float(valore)

                        pagamenti_per_programma[programma_codice] = float(row['pagamenti ammessi {}'.format(data)])  ##############

                # context['pagamenti_per_programma_{}'.format(trend)] = [{'program': programma['descrizione'], 'total_amount': dotazioni_totali_per_programma[programma['codice']], 'paid_amount': programma['ammontare']} for programma in programmi_con_pagamenti]
                context['pagamenti_per_programma_{}'.format(trend)] = [{'program': programma['descrizione'], 'total_amount': dotazioni_totali_per_programma[programma['codice']], 'paid_amount': pagamenti_per_programma[programma['codice']]} for programma in programmi_senza_pagamenti]  ###############

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

        context['map_selector'] = 'gruppo-programmi/{}/'.format(self.kwargs['slug'])

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

        context['map_selector'] = 'programmi/{}/'.format(self.kwargs['codice'])

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
        context['map_selector'] = 'nature/{}/'.format(self.kwargs['slug'])

        logger.debug('top_progetti_per_costo start')
        context['top_progetti_per_costo'] = Progetto.objects.no_privacy().con_natura(self.object).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]

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

        context['ultimi_progetti_conclusi'] = Progetto.objects.no_privacy().con_natura(self.object).conclusi()[:5]

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
        context['map_selector'] = 'temi/{}/'.format(self.kwargs['slug'])

        logger.debug('top_progetti_per_costo start')
        context['top_progetti_per_costo'] = Progetto.objects.no_privacy().con_tema(self.object).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]

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

        context['ultimi_progetti_conclusi'] = Progetto.objects.no_privacy().con_tema(self.object).conclusi()[:5]

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

        writer.writerow(['COD_LOCALE_PROGETTO', 'DATA_AGGIORNAMENTO', 'TOT_PAGAMENTI', 'OC_TOT_PAGAMENTI_RENDICONTAB_UE', 'OC_TOT_PAGAMENTI_FSC', 'OC_TOT_PAGAMENTI_PAC'])

        for pagamento in self.object.pagamenti:
            writer.writerow([
                self.object.codice_locale,
                pagamento.data.strftime('%x'),
                locale.format('%.2f', pagamento.ammontare or 0, grouping=True),
                locale.format('%.2f', pagamento.ammontare_rendicontabile_ue or 0, grouping=True),
                locale.format('%.2f', pagamento.ammontare_fsc or 0, grouping=True),
                locale.format('%.2f', pagamento.ammontare_pac or 0, grouping=True),
            ])

        return response


class BaseCSVView(AggregatoMixin, DetailView):
    filter_field = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        comuni = list(Territorio.objects.comuni().defer('geom'))
        comuni_con_pro_capite = self.top_comuni_pro_capite(filters={self.filter_field: self.object}, qnt=None)
        provincie = dict([(t['cod_prov'], t['denominazione']) for t in Territorio.objects.provincie().values('cod_prov', 'denominazione')])

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}_pro_capite.csv'.format(self.kwargs.get('slug', 'all'))

        writer = utils.UnicodeWriter(response, dialect=utils.excel_semicolon)

        writer.writerow(['Comune', 'Provincia', 'Finanziamento pro capite'])

        for city in comuni_con_pro_capite:
            writer.writerow([
                city.denominazione,
                provincie[city.cod_prov],
                '{:.2f}'.format(city.totale / city.popolazione_totale if city.popolazione_totale else .0).replace('.', ',')
            ])
            comuni.remove(city)

        for city in comuni:
            writer.writerow([
                city.denominazione,
                provincie[city.cod_prov],
                '{0:.2f}'.format(.0).replace('.', ',')
            ])

        return response


class ClassificazioneAzioneCSVView(BaseCSVView):
    model = ClassificazioneAzione
    filter_field = 'progetto__classificazione_azione__classificazione_superiore'


class TemaCSVView(BaseCSVView):
    model = Tema
    filter_field = 'progetto__tema__tema_superiore'


class ProgettoCSVSearchView(ProgettoSearchView):
    def __init__(self, *args, **kwargs):
        super(ProgettoCSVSearchView, self).__init__(*args, **kwargs)
        self.searchqueryset = self.searchqueryset.values_list('pk', flat=True)

    @staticmethod
    def _get_objects_by_pk(pks):
        related = ['territorio_set', 'tema__tema_superiore', 'classificazione_azione__classificazione_superiore', 'ruolo_set__soggetto']
        return Progetto.fullobjects.select_related(*related).prefetch_related(*related).in_bulk(pks)

    def create_response1(self):
        """
        Generates a zipped, downloadale CSV file, from search results
        """
        import datetime
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

        results = self.get_results()

        columns = OrderedDict([
            ('COD_LOCALE_PROGETTO', 'codice_locale'),
            ('CUP', 'cup'),
            ('OC_TITOLO_PROGETTO', 'titolo_progetto'),
            ('OC_TEMA_SINTETICO', 'tema.tema_superiore.descrizione'),
            ('CUP_DESCR_NATURA', 'classificazione_azione.classificazione_superiore.descrizione'),
            ('OC_TIPO_PROGETTO', 'get_tipo_progetto_display'),
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
            ('OC_DATA_FINE_PREVISTA', 'data_inizio_effettiva'),
            ('OC_DATA_INIZIO_EFFETTIVA', 'data_fine_prevista'),
            ('OC_DATA_FINE_EFFETTIVA', 'data_fine_effettiva'),
            ('SOGGETTI_PROGRAMMATORI', 'nomi_programmatori'),
            ('SOGGETTI_ATTUATORI', 'nomi_attuatori'),
            ('AMBITI_TERRITORIALI', 'ambiti_territoriali'),
            ('TERRITORI', 'nomi_territori'),
        ])

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

        # raise Exception
        return response


class ProgettoLocCSVSearchView(ProgettoSearchView):
    def __init__(self, *args, **kwargs):
        super(ProgettoLocCSVSearchView, self).__init__(*args, **kwargs)
        self.searchqueryset = self.searchqueryset.values_list('pk', flat=True)

    @staticmethod
    def _get_objects_by_pk(pks):
        related = ['territorio_set']
        return Progetto.fullobjects.select_related(*related).prefetch_related(*related).in_bulk(pks)

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
