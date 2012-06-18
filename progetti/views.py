from django.core.urlresolvers import reverse
from django.views.generic.detail import DetailView

from oc_search.forms import RangeFacetedSearchForm
from oc_search.views import ExtendedFacetedSearchView

from models import Progetto
from open_coesione.views import AggregatoView


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

        context['stesso_tema'] = Progetto.objects.con_tema(self.object.tema).nei_territori( self.object.territori )
        context['stesso_tipologia'] = Progetto.objects.del_tipo(self.object.tipo_operazione).nei_territori( self.object.territori )
        context['stessi_destinatari'] = Progetto.objects.con_tema(self.object.tema).nei_territori( self.object.territori )
        context['stessi_realizzatori'] = Progetto.objects.con_tema(self.object.tema).nei_territori( self.object.territori )

        # calcolo della percentuale del finanziamento erogato
        context['percentuale_finanziamento'] = "{0:.0%}".format(
            float(self.object.pagamento or 0) / float(self.object.fin_totale_pubblico or 0)
        )

        return context

    def get_object(self, queryset=None):
        return Progetto.objects.get(codice_locale=self.kwargs.get('slug'))

class TipologiaView(AggregatoView, DetailView):
    # raise Exception("Class TipologiaView needs to be implemented")
    pass

class TemaView(AggregatoView, DetailView):
    # raise Exception("Class TemaView needs to be implemented")
    pass


class ProgettoSearchView(ExtendedFacetedSearchView):
    """

    This view allows faceted search and navigation of a progetto.

    It extends an extended version of the basic FacetedSearchView,
    and can be customized whenever

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
        extra['tipo_operazioni'] = dict(Progetto.TIPO_OPERAZIONE)
        extra['base_url'] = reverse('progetti_search') + '?' + extra['params'].urlencode()


        return extra
