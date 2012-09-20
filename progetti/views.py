import csv
from django.conf import settings
from django.http import HttpResponse
import os
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.db import models
from django.views.generic.edit import FormView

from oc_search.forms import RangeFacetedSearchForm
from oc_search.mixins import FacetRangeCostoMixin, TerritorioMixin
from oc_search.views import ExtendedFacetedSearchView

from models import Progetto, ClassificazioneAzione, Ruolo
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



class ProgettoSearchView(AccessControlView, ExtendedFacetedSearchView, FacetRangeCostoMixin, TerritorioMixin):
    """

    This view allows faceted search and navigation of a progetto.

    It extends an extended version of the basic FacetedSearchView,

    """
    __name__ = 'ProgettoSearchView'

    COST_RANGES = {
        '0-0TO1K':      {'qrange': '[* TO 1000]', 'r_label': 'da 0 a 1.000&euro;'},
        '1-1KTO10K':    {'qrange': '[1001 TO 10000]', 'r_label': 'da 1.000 a 10.000&euro;'},
        '2-10KTO100K':  {'qrange': '[10001 TO 100000]', 'r_label': 'da 10.000 a 100.000&euro;'},
        '3-100KTOINF':  {'qrange': '[100001 TO *]', 'r_label': 'oltre 100.000&euro;'},
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
            extra['soggetto'] = Soggetto.objects.get(slug=soggetto_slug)

        # get data about custom costo and n_progetti range facets
        extra['facet_queries_costo'] = self.get_custom_facet_queries_costo()

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

        return extra


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

