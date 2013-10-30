import StringIO
import csv
import json
import zipfile
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import os
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView

from oc_search.forms import RangeFacetedSearchForm
from oc_search.mixins import FacetRangeCostoMixin, FacetRangeDateIntervalsMixin, TerritorioMixin, FacetRangePercPayMixin
from oc_search.views import ExtendedFacetedSearchView

from models import Progetto, ClassificazioneAzione, ProgrammaAsseObiettivo
from open_coesione import utils
from open_coesione.views import AggregatoView, AccessControlView, cached_context
from progetti.forms import DescrizioneProgettoForm
from progetti.models import Tema, Fonte, SegnalazioneProgetto
from soggetti.models import Soggetto
from territori.models import Territorio

import logging

class ProgettoView(AccessControlView, DetailView):
    model = Progetto
    context_object_name = 'progetto'
    queryset = Progetto.fullobjects.get_query_set()


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProgettoView, self).get_context_data(**kwargs)

        context['durata_progetto_effettiva'] = ''
        context['durata_progetto_prevista'] = ''
        if self.object.data_fine_effettiva and self.object.data_inizio_effettiva:
            context['durata_progetto_effettiva'] = (self.object.data_fine_effettiva - self.object.data_inizio_effettiva).days
        if self.object.data_fine_prevista and self.object.data_inizio_prevista:
            context['durata_progetto_prevista'] = (self.object.data_fine_prevista - self.object.data_inizio_prevista).days

        numero_collaboratori = 5
        if self.object.territori:
            altri_progetti_nei_territori = Progetto.fullobjects.exclude(codice_locale=self.object.codice_locale).nei_territori( self.object.territori ).distinct().order_by('-fin_totale_pubblico')
            context['stesso_tema'] = altri_progetti_nei_territori.con_tema(self.object.tema)[:numero_collaboratori]
            context['stessa_natura'] = altri_progetti_nei_territori.con_natura(self.object.classificazione_azione)[:numero_collaboratori]
            context['stessi_attuatori'] = altri_progetti_nei_territori.filter(soggetto_set__in=self.object.attuatori)[:numero_collaboratori]
            context['stessi_programmatori'] = altri_progetti_nei_territori.filter(soggetto_set__in=self.object.programmatori)[:numero_collaboratori]

        context['total_cost'] = float(self.object.fin_totale_pubblico) if self.object.fin_totale_pubblico else 0.0
        context['total_cost_paid'] = float(self.object.pagamento) if self.object.pagamento else 0.0
        # calcolo della percentuale del finanziamento erogato
        context['cost_payments_ratio'] = "{0:.0%}".format(context['total_cost_paid'] / context['total_cost'] if context['total_cost'] > 0.0 else 0.0)

        context['segnalazioni_pubblicate'] = self.object.segnalazioni

        return context

class ProgrammaView(AccessControlView, AggregatoView, DetailView):
    context_object_name = 'programma'
    template_name = 'progetti/programma_detail.html'

    @cached_context
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProgrammaView, self).get_context_data(**kwargs)

        logger = logging.getLogger('console')
        logger.debug("get_aggregate_data start")
        context = self.get_aggregate_data(context, programma=self.object)

        context['numero_soggetti'] = Soggetto.objects.count()
        context['map_selector'] = 'programmi/{0}/'.format(self.kwargs['codice'])

        logger.debug("top_progetti_per_costo start")
        context['top_progetti_per_costo'] = Progetto.objects.con_programma(self.object).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]

        logger.debug("ultimi_progetti_conclusi start")
        context['ultimi_progetti_conclusi'] = Progetto.objects.conclusi().con_programma(self.object)[:5]

        logger.debug("territori_piu_finanziati_pro_capite start")
        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(
            filters={
                'progetto__programma_asse_obiettivo__classificazione_superiore__classificazione_superiore': self.object
            }
        )

        return context

    def get_object(self, queryset=None):
        return ProgrammaAsseObiettivo.objects.get(pk=self.kwargs.get('codice'))


class TipologiaView(AccessControlView, AggregatoView, DetailView):
    context_object_name = 'tipologia'

    @cached_context
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TipologiaView, self).get_context_data(**kwargs)

        logger = logging.getLogger('console')
        logger.debug("get_aggregate_data start")
        context = self.get_aggregate_data(context, classificazione=self.object)

        context['numero_soggetti'] = Soggetto.objects.count()
        context['map_selector'] = 'nature/{0}/'.format(self.kwargs['slug'])

        logger.debug("top_progetti_per_costo start")
        context['top_progetti_per_costo'] = Progetto.objects.con_natura(self.object).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]

        logger.debug("ultimi_progetti_conclusi start")
        context['ultimi_progetti_conclusi'] = Progetto.objects.conclusi().con_natura(self.object)[:5]

        logger.debug("territori_piu_finanziati_pro_capite start")
        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(
            filters={
                'progetto__classificazione_azione__classificazione_superiore': self.object
            }
        )

        return context

    def get_object(self, queryset=None):
        return ClassificazioneAzione.objects.get(slug=self.kwargs.get('slug'))

class TemaView(AccessControlView, AggregatoView, DetailView):
    context_object_name = 'tema'

    @cached_context
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TemaView, self).get_context_data(**kwargs)

        logger = logging.getLogger('console')
        logger.debug("get_aggregate_data start")
        context = self.get_aggregate_data(context, tema=self.object)

        context['numero_soggetti'] = Soggetto.objects.count()
        context['map_selector'] = 'temi/{0}/'.format(self.kwargs['slug'])

        logger.debug("build lista_indici_tema from csv file start")
        context['lista_indici_tema'] = []
        with open(os.path.join(settings.STATIC_ROOT, 'csv/indicatori/{0}.csv'.format(self.object.codice))) as csvfile:
            reader = csv.DictReader(csvfile)
            for line in reader:
                context['lista_indici_tema'].append(line)


        logger.debug("top_progetti_per_costo start")
        context['top_progetti_per_costo'] = Progetto.objects.con_tema(self.object).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]

        logger.debug("ultimi_progetti_conclusi start")
        context['ultimi_progetti_conclusi'] = Progetto.objects.conclusi().con_tema(self.object)[:5]

        logger.debug("territori_piu_finanziati_pro_capite start")
        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(
            filters={
                'progetto__tema__tema_superiore': self.object
            }
        )

        return context

    def get_object(self, queryset=None, **kwargs):
        return Tema.objects.get(slug=self.kwargs.get('slug'))

class CSVView(AggregatoView, DetailView):

    filter_field = ''

    def get_first_row(self):
        return ['Comune', 'Provincia', 'Finanziamento pro capite']

    def get_csv_filename(self):
        return '{0}_pro_capite'.format(self.kwargs.get('slug','all'))

    def write_csv(self, response):
        writer = utils.UnicodeWriter(response, dialect=utils.excel_semicolon)
        writer.writerow(self.get_first_row())
        comuni = list(Territorio.objects.comuni().defer('geom'))
        provincie = dict([(t['cod_prov'], t['denominazione']) for t in Territorio.objects.provincie().values('cod_prov','denominazione')])
        comuni_con_pro_capite = self.top_comuni_pro_capite(filters={ self.filter_field: self.object}, qnt=None)

        for city in comuni_con_pro_capite:
            writer.writerow([
                unicode(city.denominazione),
                unicode(provincie[city.cod_prov]),
                '{0:.2f}'.format( city.totale / city.popolazione_totale if city in comuni_con_pro_capite else .0).replace('.', ',')
            ])
            comuni.remove(city)

        for city in comuni:
            writer.writerow([
                unicode(city.denominazione),
                unicode(provincie[city.cod_prov]),
                '{0:.2f}'.format( .0 ).replace('.', ',')
            ])

    def get(self, request, *args, **kwargs):

        self.object = self.get_object()

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename={0}.csv'.format(self.get_csv_filename())

        self.write_csv(response)

        return response

    def get_object(self, queryset=None):
        return self.model.objects.get(slug=self.kwargs.get('slug'))

class TipologiaCSVView(CSVView):
    model = ClassificazioneAzione
    filter_field = 'progetto__classificazione_azione__classificazione_superiore'

class TemaCSVView(CSVView):
    model = Tema
    filter_field = 'progetto__tema__tema_superiore'


class ProgettoSearchView(AccessControlView, ExtendedFacetedSearchView,
                         FacetRangePercPayMixin, FacetRangeCostoMixin,
                         FacetRangeDateIntervalsMixin, TerritorioMixin):
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
        '0-0TO1K':      {'qrange': '[* TO 1000]', 'r_label': 'da 0 a 1.000&euro;'},
        '1-1KTO10K':    {'qrange': '[1000.01 TO 10000]', 'r_label': 'da 1.000 a 10.000&euro;'},
        '2-10KTO100K':  {'qrange': '[10000.01 TO 100000]', 'r_label': 'da 10.000 a 100.000&euro;'},
        '3-100KTOINF':  {'qrange': '[100000.01 TO *]', 'r_label': 'oltre 100.000&euro;'},
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
        'nd'  :  {'qrange': '[* TO 1970-01-01T00:00:00Z]', 'r_label': 'non disponibile'}
    }

    def __init__(self, *args, **kwargs):
        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = RangeFacetedSearchForm

        super(ProgettoSearchView, self).__init__(*args, **kwargs)

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {  }

        # the is_active:1 facet is selected by default
        # and is substituted by is_active:0 when explicitly requested
        # by clicking on the "See archive" link in the progetti page
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
        extra['facet_queries_date'] = self._get_custom_facet_queries_date()

        # definizione struttura dati per  visualizzazione faccette natura
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


        # definizione struttura dati per  visualizzazione faccette tema
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

        extra['paginator'] = paginator
        extra['page_obj'] = page_obj

        extra['n_max_downloadable'] = settings.N_MAX_DOWNLOADABLE_RESULTS

        extra['perc_pay_facets_enabled'] = getattr(settings, 'PERC_PAY_FACETS_ENABLED', False)
        return extra


class CSVSearchResultsWriterMixin(object):
    """
    Mixin used by CSV - related SearchView classes, to add results as csv rows to a CSV writer
    Both the results and the writer objects must have been correctly defined,
    before invoking the write_search_results method.
    """
    def write_projects_localisations_search_results(self, results, writer):
        """
        Writes all results of a search query set into a CSV writer.
        """
        writer.writerow([
            'COD_LOCALE_PROGETTO',
            'DPS_TERRITORIO_PROG', 'COD_COMUNE', 'COD_PROVINCIA', 'COD_REGIONE'
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
                        "%06d" % int(t[1]),
                        "%03d" % int(t[2]),
                        t[3]
                    ])


    def write_projects_search_results(self, results, writer ):
        """
        Writes all results of a search query set into a CSV writer.
        """

        import locale
        from datetime import datetime
        locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

        writer.writerow([
            'COD_LOCALE_PROGETTO', 'CUP',
            'DPS_TITOLO_PROGETTO',
            'DPS_TEMA_SINTETICO', 'CUP_DESCR_NATURA ',
            'FIN_UE',
            'FIN_STATO_FONDO_ROTAZIONE', 'FIN_STATO_FSC', 'FIN_STATO_ALTRI_PROVVEDIMENTI',
            'FIN_REGIONE', 'FIN_PROVINCIA', 'FIN_COMUNE',
            'FIN_ALTRO_PUBBLICO', 'FIN_STATO_ESTERO',
            'FIN_PRIVATO', 'FIN_DA_REPERIRE',
            'FIN_TOTALE_PUBBLICO',
            'TOT_PAGAMENTI',
            'QSN_FONDO_COMUNITARIO',
            'DPS_DATA_INIZIO_PREVISTA', 'DPS_DATA_FINE_PREVISTA',
            'DPS_DATA_INIZIO_EFFETTIVA', 'DPS_DATA_FINE_EFFETTIVA',
            'SOGGETTI_PROGRAMMATORI', 'SOGGETTI_ATTUATORI',
            'AMBITI_TERRITORIALI', 'TERRITORI'
        ])
        for r in results:
            
            separator = u":::"

            soggetti_programmatori = ""
            if r.soggetti_programmatori:
                soggetti_programmatori = separator.join(list(r.soggetti_programmatori)).encode('latin1', 'ignore')

            soggetti_attuatori = ""
            if r.soggetti_attuatori:
                soggetti_attuatori = separator.join(list(r.soggetti_attuatori)).encode('latin1', 'ignore')

            ambiti = ""
            if r.ambiti_territoriali:
                ambiti = separator.join(list(r.ambiti_territoriali)).encode('latin1', 'ignore')

            territori = ""
            if r.territori:
                territori = separator.join(list(r.territori)).encode('latin1', 'ignore')

            writer.writerow([
                unicode(r.clp).encode('latin1', 'ignore'), r.cup,
                unicode(r.titolo).encode('latin1', 'ignore'),
                unicode(r.tema_descr).encode('latin1', 'ignore'),
                unicode(r.natura_descr).encode('latin1', 'ignore'),
                locale.format("%.2f", r.fin_ue) if r.fin_ue is not None else "",
                locale.format("%.2f", r.fin_stato_fondo_rotazione) if r.fin_stato_fondo_rotazione is not None else "",
                locale.format("%.2f", r.fin_stato_fsc) if r.fin_stato_fsc is not None else "", 
                locale.format("%.2f", r.fin_stato_altri_provvedimenti) if r.fin_stato_altri_provvedimenti is not None else "",
                locale.format("%.2f", r.fin_regione) if r.fin_regione is not None else "", 
                locale.format("%.2f", r.fin_provincia) if r.fin_provincia is not None else "", 
                locale.format("%.2f", r.fin_comune) if r.fin_comune is not None else "",
                locale.format("%.2f", r.fin_altro_pubblico) if r.fin_altro_pubblico is not None else "", 
                locale.format("%.2f", r.fin_stato_estero) if r.fin_stato_estero is not None else "",
                locale.format("%.2f", r.fin_privato) if r.fin_privato is not None else "", 
                locale.format("%.2f", r.fin_da_reperire) if r.fin_da_reperire is not None else "",
                locale.format("%.2f", r.fin_totale_pubblico) if r.fin_totale_pubblico is not None else "",
                locale.format("%.2f", r.pagamento) if r.pagamento is not None else "",
                unicode(r.fondo).encode('latin1', 'ignore'),
                r.data_inizio_prevista.strftime("%Y%m%d") if r.data_inizio_prevista is not None else "",
                r.data_inizio_effettiva.strftime("%Y%m%d") if r.data_inizio_effettiva is not None else "",
                r.data_fine_prevista.strftime("%Y%m%d") if r.data_fine_prevista is not None else "",
                r.data_fine_effettiva.strftime("%Y%m%d") if r.data_fine_effettiva is not None else "",
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
        z = zipfile.ZipFile(response,'w')   ## write zip to response

        # add progetti csv to zip stream
        output = StringIO.StringIO()
        writer = csv.writer(output, dialect='opencoesione')
        self.write_projects_search_results(results, writer)
        z.writestr("progetti.csv", output.getvalue())  ## write csv file to zip

        # add localizzazioni csv to zip stream
        output = StringIO.StringIO()
        writer = csv.writer(output, dialect='opencoesione')
        self.write_projects_localisations_search_results(results, writer)
        z.writestr("localizzazioni.csv", output.getvalue())  ## write csv file to zip

        # add metadati content to zip stream
        output = StringIO.StringIO()
        f = open(os.path.join(settings.REPO_ROOT, 'dati', 'metadati_search_results.xls'), 'rb')
        output.write(f.read())
        z.writestr("metadati.xls", output.getvalue())

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
    model = SegnalazioneProgetto
    template_name = 'segnalazione/singola.html'
    context_object_name = 'segnalazione'

