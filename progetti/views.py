from django.core import paginator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.views.generic.detail import DetailView

from oc_search.forms import RangeFacetedSearchForm
from oc_search.views import ExtendedFacetedSearchView

from models import Progetto, ClassificazioneAzione, ClassificazioneQSN
from open_coesione.views import AggregatoView
from progetti.models import Tema, ClassificazioneAzione
from territori.models import Territorio
from django.db.models import Sum, Count


class ProgettoView(DetailView):
    model = Progetto
    context_object_name = 'progetto'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProgettoView, self).get_context_data(**kwargs)
        context['durata_progetto'] = (
            self.object.data_fine_prevista - self.object.data_inizio_prevista
            if self.object.data_fine_prevista and self.object.data_inizio_prevista
            else ''
        )

        context['stesso_tema'] = Progetto.objects.con_tema(self.object.tema).nei_territori( self.object.territori )[:1]
        context['stesso_tipologia'] = Progetto.objects.del_tipo(self.object.tipo_operazione).nei_territori( self.object.territori )[:1]
        context['stessi_destinatari'] = Progetto.objects.con_tema(self.object.tema).nei_territori( self.object.territori )[:1]
        context['stessi_realizzatori'] = Progetto.objects.con_tema(self.object.tema).nei_territori( self.object.territori )[:1]

        context['total_cost'] = float(self.object.fin_totale_pubblico) if self.object.fin_totale_pubblico else 0.0
        context['total_cost_paid'] = float(self.object.pagamento) if self.object.pagamento else 0.0
        # calcolo della percentuale del finanziamento erogato
        context['cost_payments_ratio'] = "{0:.0%}".format(context['total_cost_paid'] / context['total_cost'] if context['total_cost'] > 0.0 else 0.0)

        return context

#    def get_object(self, queryset=None):
#       return Progetto.objects.get(slug=self.kwargs.get('slug'))

class TipologiaView(AggregatoView, DetailView):
    # raise Exception("Class TipologiaView needs to be implemented")
    pass

class TemaView(AggregatoView, DetailView):

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TemaView, self).get_context_data(**kwargs)

        context['total_cost'] = Progetto.objects.totale_costi(tema=self.object)
        context['total_cost_paid'] = Progetto.objects.totale_costi_pagati(tema=self.object)
        context['total_projects'] = Progetto.objects.totale_progetti(tema=self.object)
        context['cost_payments_ratio'] = "{0:.0%}".format(context['total_cost_paid'] / context['total_cost'] if context['total_cost'] > 0.0 else 0.0)

        context['temi_principali'] = Tema.objects.principali()

        context['tipologie_principali'] = ClassificazioneAzione.objects.tematiche()

        context['map'] = self.get_map_context()

        context['map']['data'] = {
            'regioni': {
                'numero': {},
                'costo': {},
                'pagamento' : {},
            }
        }

        for regione in Territorio.objects.regioni():

            stats = Progetto.objects.nel_territorio(regione).aggregate(
                numero=Count('codice_locale'),
                costo=Sum('fin_totale_pubblico'),
                pagamento=Sum('pagamento'),
            )

            for key in stats:
                context['map']['data']['regioni'][key][regione.cod_reg] = float(stats[key]) if key != 'numero' else int(stats[key])
#            'regioni' : {
#                'numero': dict(
#                    (t.cod_reg, Territorio.objects.filter(cod_reg=t.cod_reg).aggregate(s=Count('progetto'))['s'])
#                        for t in Territorio.objects.filter(territorio='R')
#                ),
#                'costo': dict(
#                    (t.cod_reg, Territorio.objects.filter(cod_reg=t.cod_reg).aggregate(s=Sum('progetto__fin_totale_pubblico'))['s'])
#                        for t in Territorio.objects.filter(territorio='R')
#                ),
#                'pagamento': dict(
#                    (t.cod_reg, Territorio.objects.filter(cod_reg=t.cod_reg).aggregate(s=Sum('progetto__pagamento'))['s'])
#                        for t in Territorio.objects.filter(territorio='R')
#                )
#            }
#        }

        return context

    def get_object(self, queryset=None):
        # TODO we need a slug for Tema..
        return Tema.objects.get(codice=self.kwargs.get('slug').replace('-','.'))


class ProgettoSearchView(ExtendedFacetedSearchView):
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
