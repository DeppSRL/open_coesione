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
from oc_search.mixins import FacetRangeCostoMixin, FacetRangeDateIntervalsMixin, TerritorioMixin
from oc_search.views import ExtendedFacetedSearchView

from models import Progetto, ClassificazioneAzione
from open_coesione import utils
from open_coesione.views import AggregatoView, AccessControlView
from progetti.forms import DescrizioneProgettoForm
from progetti.models import Tema, Fonte, SegnalazioneProgetto
from soggetti.models import Soggetto
from territori.models import Territorio


class ProgettoView(AccessControlView, DetailView):
    model = Progetto
    context_object_name = 'progetto'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProgettoView, self).get_context_data(**kwargs)

        context['durata_progetto_effettiva'] = ''
        context['durata_progetto_prevista'] = ''
        if self.object.data_fine_effettiva and self.object.data_inizio_effettiva:
            context['durata_progetto_effettiva'] = (self.object.data_fine_effettiva - self.object.data_inizio_effettiva).days
        if self.object.data_fine_prevista and self.object.data_inizio_prevista:
            context['durata_progetto_prevista'] = (self.object.data_fine_prevista - self.object.data_inizio_prevista).days

#        context['giorni_alla_fine'] = (
#            (date.today() - self.object.data_fine_prevista).days
#            if self.object.data_fine_prevista else ''
#            )
#        if context['giorni_alla_fine'] and context['giorni_alla_fine'] < 0:
#            context['giorni_alla_fine'] = ''
        numero_collaboratori = 5
        if self.object.territori:
            altri_progetti_nei_territori = Progetto.objects.exclude(codice_locale=self.object.codice_locale).nei_territori( self.object.territori ).distinct().order_by('-fin_totale_pubblico')
            context['stesso_tema'] = altri_progetti_nei_territori.con_tema(self.object.tema)[:numero_collaboratori]
            context['stessa_natura'] = altri_progetti_nei_territori.con_natura(self.object.classificazione_azione)[:numero_collaboratori]
            context['stessi_attuatori'] = altri_progetti_nei_territori.filter(soggetto_set__in=self.object.attuatori)[:numero_collaboratori]
            context['stessi_programmatori'] = altri_progetti_nei_territori.filter(soggetto_set__in=self.object.programmatori)[:numero_collaboratori]

        context['total_cost'] = float(self.object.fin_totale_pubblico) if self.object.fin_totale_pubblico else 0.0
        context['total_cost_paid'] = float(self.object.pagamento) if self.object.pagamento else 0.0
        # calcolo della percentuale del finanziamento erogato
        context['cost_payments_ratio'] = "{0:.0%}".format(context['total_cost_paid'] / context['total_cost'] if context['total_cost'] > 0.0 else 0.0)

        context['segnalazioni_pubblicate'] = self.object.segnalazioni

#        primo_territorio = self.object.territori[0] or None
#
#        context['map'] = {
#            'extent': "[{{lon: {0}, lat: {1}}},{{lon: {2}, lat: {3}}}]".format( *Territorio.objects.filter(territorio='R').extent() ),
#            'poi': simplejson.dumps( primo_territorio.geom.centroid.coords if primo_territorio else False ),
#            'pois' : simplejson.dumps( [t.geom.centroid.coords for t in self.object.territori] ),
#        }

        return context

class TipologiaView(AggregatoView, DetailView):
    context_object_name = 'tipologia'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TipologiaView, self).get_context_data(**kwargs)

        context = self.get_aggregate_data(context, classificazione=self.object)

        context['numero_soggetti'] = Soggetto.objects.count()

#        context['tematizzazione'] = self.request.GET.get('tematizzazione', 'totale_costi')
#        context['map_legend_colors'] = settings.MAP_COLORS
        context['map_selector'] = 'nature/{0}/'.format(self.kwargs['slug'])

        context['top_progetti_per_costo'] = Progetto.objects.con_natura(self.object).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]
        context['ultimi_progetti_conclusi'] = Progetto.objects.conclusi().con_natura(self.object)[:5]

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

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TemaView, self).get_context_data(**kwargs)

        context = self.get_aggregate_data(context, tema=self.object)

        context['numero_soggetti'] = Soggetto.objects.count()

#        context['tematizzazione'] = self.request.GET.get('tematizzazione', 'totale_costi')
#        context['map_legend_colors'] = settings.MAP_COLORS
        context['map_selector'] = 'temi/{0}/'.format(self.kwargs['slug'])

        context['lista_indici_tema'] = csv.DictReader(open(os.path.join(settings.STATIC_ROOT, 'csv/indicatori/{0}.csv'.format(self.object.codice))))

        context['top_progetti_per_costo'] = Progetto.objects.con_tema(self.object).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]
        context['ultimi_progetti_conclusi'] = Progetto.objects.conclusi().con_tema(self.object)[:5]

        context['territori_piu_finanziati_pro_capite'] = self.top_comuni_pro_capite(
            filters={
                'progetto__tema__tema_superiore': self.object
            }
        )
#        def pro_capite_order(territorio):
#            territorio.totale_pro_capite = territorio.totale / territorio.popolazione_totale
#            return territorio.totale_pro_capite
#
#        context['territori_piu_finanziati_pro_capite'] = sorted( Territorio.objects
#                                                         .filter( territorio=Territorio.TERRITORIO.C, progetto__tema__tema_superiore=self.object )
#                                                         .annotate( totale=models.Sum('progetto__fin_totale_pubblico') )
#                                                         .filter( totale__isnull=False ), key= pro_capite_order, reverse=True )[:5]
#                                                         #.order_by('-totale')[:5]

        return context

    def get_object(self, queryset=None):
        return Tema.objects.get(slug=self.kwargs.get('slug'))

class CSVView(AggregatoView, DetailView):

    filter_field = ''

    def get_first_row(self):
        return ['Comune', 'Provincia', 'Finanziamento pro capite']

    def get_csv_filename(self):
        return '{0}_pro_capite'.format(self.kwargs.get('slug','all'))

    def write_csv(self, response):
        writer = utils.UnicodeWriter(response, dialect= utils.excel_semicolon)
        writer.writerow( self.get_first_row() )
        comuni = list(Territorio.objects.comuni())
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


class ProgettoSearchView(AccessControlView, ExtendedFacetedSearchView, FacetRangeCostoMixin, FacetRangeDateIntervalsMixin, TerritorioMixin):
    """
    This view allows faceted search and navigation of a progetto.

    It extends an extended version of the basic FacetedSearchView,
    """
    __name__ = 'ProgettoSearchView'

    COST_RANGES = {
        '0-0TO1K':      {'qrange': '[* TO 1000]', 'r_label': 'da 0 a 1.000&euro;'},
        '1-1KTO10K':    {'qrange': '[1000.001 TO 10000]', 'r_label': 'da 1.000 a 10.000&euro;'},
        '2-10KTO100K':  {'qrange': '[10000.001 TO 100000]', 'r_label': 'da 10.000 a 100.000&euro;'},
        '3-100KTOINF':  {'qrange': '[100000.001 TO *]', 'r_label': 'oltre 100.000&euro;'},
    }


#    DATE_INTERVALS_RANGES = {
#        'SIXMONTHS':  {'qrange': '[NOW/DAY-180DAYS TO NOW/DAY]', 'r_label': 'ultimi sei mesi'},
#        'ONEYEAR': {'qrange': '[NOW/DAY-365DAYS TO NOW/DAY]', 'r_label': 'ultimo anno'},
#        'TWOYEARS': {'qrange': '[NOW/DAY-730DAYS TO NOW/DAY]', 'r_label': 'ultimi due anno'}
#    }

    DATE_INTERVALS_RANGES = {
        '2013':  {'qrange': '[2013-01-01T00:00:00Z TO 2014-01-01T00:00:00Z]', 'r_label': '2013'},
        '2012':  {'qrange': '[2012-01-01T00:00:00Z TO 2013-01-01T00:00:00Z]', 'r_label': '2012'},
        '2011':  {'qrange': '[2011-01-01T00:00:00Z TO 2012-01-01T00:00:00Z]', 'r_label': '2011'},
        '2010':  {'qrange': '[2010-01-01T00:00:00Z TO 2011-01-01T00:00:00Z]', 'r_label': '2010'},
        '2009':  {'qrange': '[2009-01-01T00:00:00Z TO 2010-01-01T00:00:00Z]', 'r_label': '2009'},
        '2008':  {'qrange': '[2008-01-01T00:00:00Z TO 2009-01-01T00:00:00Z]', 'r_label': '2008'},
        '2007':  {'qrange': '[2007-01-01T00:00:00Z TO 2008-01-01T00:00:00Z]', 'r_label': '2007'},
        'early': {'qrange': '[1970-01-02T00:00:00Z TO 2007-01-01T00:00:00Z]', 'r_label': 'prima del 2007'},
        'nd'  :  {'qrange': '[* TO 1970-01-01T00:00:00Z]', 'r_label': 'non disponibile'}
    }

    def __init__(self, *args, **kwargs):
        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = RangeFacetedSearchForm

        super(ProgettoSearchView, self).__init__(*args, **kwargs)

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        return super(ProgettoSearchView, self).build_form(form_kwargs)


    def _get_extended_selected_facets(self):
        """
        modifies the extended_selected_facets, adding correct labels for this view
        works directly on the extended_selected_facets dictionary
        """
        extended_selected_facets = super(ProgettoSearchView, self)._get_extended_selected_facets()

        # this comes from the Mixins
        extended_selected_facets = self.add_costo_extended_selected_facets(extended_selected_facets)
        extended_selected_facets = self.add_territorio_extended_selected_facets(extended_selected_facets)
        extended_selected_facets = self.add_date_interval_extended_selected_facets(extended_selected_facets)

        return extended_selected_facets

    def extra_context(self):
        """
        Add extra content here, when needed
        """
        extra = super(ProgettoSearchView, self).extra_context()

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
        elif territorio_reg and territorio_reg == '0':
            extra['territorio'] = Territorio.objects.get(
                territorio=Territorio.TERRITORIO.N,
                cod_reg=territorio_reg
            ).nome

        soggetto_slug = self.request.GET.get('soggetto', None)
        if soggetto_slug:
            try:
                extra['soggetto'] = Soggetto.objects.get(slug=soggetto_slug)
            except ObjectDoesNotExist:
                pass

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

            print r.territorio_com
            if r.territorio_com is not None:
                territori_codici = zip(
                    r.territorio_tipo,
                    r.territorio_com,
                    r.territorio_prov,
                    r.territorio_reg
                )
                for t in territori_codici:
                    writer.writerow([
                        r.clp,
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
        locale.setlocale(locale.LC_ALL, 'it_IT.utf8')

        writer.writerow([
            'COD_LOCALE_PROGETTO', 'CUP',
            'DPS_TITOLO_PROGETTO', 'DESCRIZIONE',
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
                soggetti_programmatori = separator.join(list(r.soggetti_programmatori)).encode('latin1')

            soggetti_attuatori = ""
            if r.soggetti_attuatori:
                soggetti_attuatori = separator.join(list(r.soggetti_attuatori)).encode('latin1')

            ambiti = ""
            if r.ambiti_territoriali:
                ambiti = separator.join(list(r.ambiti_territoriali)).encode('latin1')

            territori = ""
            if r.territori:
                territori = separator.join(list(r.territori)).encode('latin1')

            writer.writerow([
                r.clp, r.cup,
                unicode(r.titolo).encode('latin1'),
                unicode(r.descrizione).encode('latin1') if r.descrizione is not None else "",
                unicode(r.tema_descr).encode('latin1'),
                unicode(r.natura_descr).encode('latin1'),
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
                unicode(r.fondo).encode('latin1'),
                r.data_inizio_prevista.strftime("%Y%m%d") if r.data_inizio_prevista is not None else "",
                r.data_inizio_effettiva.strftime("%Y%m%d") if r.data_inizio_effettiva is not None else "",
                r.data_fine_prevista.strftime("%Y%m%d") if r.data_fine_prevista is not None else "",
                r.data_fine_effettiva.strftime("%Y%m%d") if r.data_fine_effettiva is not None else "",
                soggetti_programmatori, soggetti_attuatori,
                ambiti, territori
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
        response['Content-Disposition'] = 'attachment; filename=risultati_progetti.csv'

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
        response['Content-Disposition'] = 'attachment; filename=risultati_localizzazioni.csv'

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
        import jsonpickle
        results = [r.object for r in self.get_results()]

        # send JSON out as plain text
        response = HttpResponse(json.dumps(results, cls=ProgettoJSONEncoder), mimetype='text/plain')

        return response


class SegnalaDescrizioneView(FormView):
    template_name = 'segnalazione/modulo.html'
    form_class = DescrizioneProgettoForm
    success_url = reverse_lazy('progetti_segnalazione_completa')

    def get_context_data(self, **kwargs):
        context = super(SegnalaDescrizioneView,self).get_context_data(**kwargs)
        try:
            context['progetto'] = Progetto.objects.get(cup=self.request.GET.get('cup'))
        except Progetto.DoesNotExist:
            pass
        return context

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initials = self.initial.copy()

        if 'cup' in self.request.GET:

            initials['cup'] = self.request.GET.get('cup')

        return initials

    def form_valid(self, form):

        form.send_mail()

        form.save()

        return super(SegnalaDescrizioneView, self).form_valid(form)


class SegnalazioneDetailView(DetailView):
    model = SegnalazioneProgetto
    template_name = 'segnalazione/singola.html'
    context_object_name = 'segnalazione'

