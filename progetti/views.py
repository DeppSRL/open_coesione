from django.core.urlresolvers import reverse
from django.views.generic.detail import DetailView

from oc_search.forms import RangeFacetedSearchForm
from oc_search.views import ExtendedFacetedSearchView

from models import Progetto
from open_coesione.views import AggregatoView


class ProgettoView(DetailView):
    raise Exception("Class ProgettoView needs to be implemented")

class TipologiaView(AggregatoView, DetailView):
    raise Exception("Class TipologiaView needs to be implemented")

class TemaView(AggregatoView, DetailView):
    raise Exception("Class TemaView needs to be implemented")


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
        extra['base_url'] = reverse('oc_progetto_search') + '?' + extra['params'].urlencode()


        return extra
