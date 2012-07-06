import csv
from django.conf import settings
import os
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.core.urlresolvers import reverse
from django.views.generic.detail import DetailView
from django.utils import simplejson

from oc_search.forms import RangeFacetedSearchForm
from oc_search.views import ExtendedFacetedSearchView

from models import Progetto, ClassificazioneAzione, ClassificazioneQSN
from open_coesione.settings import REPO_ROOT
from open_coesione.views import AggregatoView, AccessControlView
from progetti.models import Tema, ClassificazioneAzione
from soggetti.models import Soggetto
from territori.models import Territorio
from django.db.models import Sum, Count


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

        context['stesso_tema'] = Progetto.objects.exclude(codice_locale=self.object.codice_locale).con_tema(self.object.tema).nei_territori( self.object.territori )[:1]
        context['stesso_tipologia'] = Progetto.objects.exclude(codice_locale=self.object.codice_locale).del_tipo(self.object.tipo_operazione).nei_territori( self.object.territori )[:1]
        context['stessi_destinatari'] = Progetto.objects.exclude(codice_locale=self.object.codice_locale).con_tema(self.object.tema).nei_territori( self.object.territori )[:1]
        context['stessi_realizzatori'] = Progetto.objects.exclude(codice_locale=self.object.codice_locale).con_tema(self.object.tema).nei_territori( self.object.territori )[:1]

        context['total_cost'] = float(self.object.fin_totale_pubblico) if self.object.fin_totale_pubblico else 0.0
        context['total_cost_paid'] = float(self.object.pagamento) if self.object.pagamento else 0.0
        # calcolo della percentuale del finanziamento erogato
        context['cost_payments_ratio'] = "{0:.0%}".format(context['total_cost_paid'] / context['total_cost'] if context['total_cost'] > 0.0 else 0.0)

        primo_territorio = self.object.territori[0] or None

        context['map'] = {
            'extent': "[{{lon: {0}, lat: {1}}},{{lon: {2}, lat: {3}}}]".format( *Territorio.objects.filter(territorio='R').extent() ),
            'poi': simplejson.dumps( primo_territorio.geom.centroid.coords if primo_territorio else False ),
            'pois' : simplejson.dumps( [t.geom.centroid.coords for t in self.object.territori] ),
        }

        return context

#    def get_object(self, queryset=None):
#       return Progetto.objects.get(slug=self.kwargs.get('slug'))

class TipologiaView(AggregatoView, DetailView):
    context_object_name = 'tipologia'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TipologiaView, self).get_context_data(**kwargs)

        context['total_cost'] = Progetto.objects.totale_costi(classificazione=self.object)
        context['total_cost_paid'] = Progetto.objects.totale_costi_pagati(classificazione=self.object)
        context['total_projects'] = Progetto.objects.totale_progetti(classificazione=self.object)
        context['cost_payments_ratio'] = "{0:.0%}".format(context['total_cost_paid'] / context['total_cost'] if context['total_cost'] > 0.0 else 0.0)

        context['temi_principali'] = [
            {
            'object': tema,
            'data': Tema.objects.\
                filter(tema_superiore=tema).\
                filter(progetto_set__classificazione_azione__classificazione_superiore=self.object).\
                aggregate(numero=Count('progetto_set'),
                          costo=Sum('progetto_set__fin_totale_pubblico'),
                          pagamento=Sum('progetto_set__pagamento'))
            } for tema in Tema.objects.principali()
        ]

        context['numero_soggetti'] = Soggetto.objects.count()

#        context['map'] = self.get_map_context()
        context['tematizzazione'] = self.request.GET.get('tematizzazione', 'totale_costi')
        context['map_legend_colors'] = settings.MAP_COLORS

#        context['map']['data'] = {
#            'regioni': {
#                'numero': {},
#                'costo': {},
#                'pagamento' : {},
#                }
#        }
#
#        for regione in Territorio.objects.regioni():
#
#            stats = Progetto.objects.con_natura(self.object).aggregate(
#                numero=Count('codice_locale'),
#                costo=Sum('fin_totale_pubblico'),
#                pagamento=Sum('pagamento'),
#            )
#
#            for key in stats:
#                context['map']['data']['regioni'][key][regione.cod_reg] = float(stats[key]) if key != 'numero' else int(stats[key])

        return context

    def get_object(self, queryset=None):
        return ClassificazioneAzione.objects.get(slug=self.kwargs.get('slug'))

class TemaView(AggregatoView, DetailView):
    context_object_name = 'tema'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TemaView, self).get_context_data(**kwargs)

        context['total_cost'] = Progetto.objects.totale_costi(tema=self.object)
        context['total_cost_paid'] = Progetto.objects.totale_costi_pagati(tema=self.object)
        context['total_projects'] = Progetto.objects.totale_progetti(tema=self.object)
        context['cost_payments_ratio'] = "{0:.0%}".format(context['total_cost_paid'] / context['total_cost'] if context['total_cost'] > 0.0 else 0.0)

        # estrae l'aggregato di numero, costi e pagamenti progetti per
        # tutte le nature (tipologie principali)
        # a tema fissato
        context['tipologie_principali'] = [
            {
                'object': natura,
                'data': ClassificazioneAzione.objects.\
                          filter(classificazione_superiore=natura).\
                          filter(progetto_set__tema__tema_superiore=self.object).\
                          aggregate(numero=Count('progetto_set'),
                                    costo=Sum('progetto_set__fin_totale_pubblico'),
                                    pagamento=Sum('progetto_set__pagamento'))
            } for natura in ClassificazioneAzione.objects.tematiche()
        ]

        context['numero_soggetti'] = Soggetto.objects.count()

        context['tematizzazione'] = self.request.GET.get('tematizzazione', 'totale_costi')
        context['map_legend_colors'] = settings.MAP_COLORS

#        context['map'] = self.get_map_context()
#
#        context['map']['data'] = {
#            'regioni': {
#                'numero': {},
#                'costo': {},
#                'pagamento' : {},
#            }
#        }
#
#        for regione in Territorio.objects.regioni():
#
#            stats = Progetto.objects.nel_territorio(regione).aggregate(
#                numero=Count('codice_locale'),
#                costo=Sum('fin_totale_pubblico'),
#                pagamento=Sum('pagamento'),
#            )
#
#            for key in stats:
#                context['map']['data']['regioni'][key][regione.cod_reg] = float(stats[key]) if key != 'numero' else int(stats[key])

        context['lista_indici_tema'] = csv.DictReader(open(os.path.join(REPO_ROOT, 'open_coesione/static/csv/indicatori/{0}.csv'.format(self.object.codice))))

        return context

    def get_object(self, queryset=None):
        return Tema.objects.get(slug=self.kwargs.get('slug'))


class ProgettoSearchView(AccessControlView, ExtendedFacetedSearchView):
    """

    This view allows faceted search and navigation of a progetto.

    It extends an extended version of the basic FacetedSearchView,

    """
    __name__ = 'ProgettoSearchView'

    def __init__(self, *args, **kwargs):
        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = RangeFacetedSearchForm

        super(ProgettoSearchView, self).__init__(*args, **kwargs)

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        return super(ProgettoSearchView, self).build_form(form_kwargs)

    def extra_context(self):
        """
        Add extra content here, when needed
        """
        extra = super(ProgettoSearchView, self).extra_context()

        territorio_id = self.request.GET.get('territorio_id', 0)
        if territorio_id:
            extra['territorio'] = Territorio.objects.get(pk=territorio_id).nome_con_provincia

        # definizione struttura dati per  visualizzazione faccette natura
        extra['natura'] = {
            'descrizione': dict(
                (c.codice, c.descrizione)
                for c in ClassificazioneAzione.objects.filter(tipo_classificazione='natura')
            ),
            'short_label': dict(
                (c.codice, c.short_label)
                for c in ClassificazioneAzione.objects.filter(tipo_classificazione='natura')
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

        extra['paginator'] = paginator
        extra['page_obj'] = page_obj

        return extra
