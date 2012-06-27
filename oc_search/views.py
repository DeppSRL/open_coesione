from haystack.views import SearchView
from forms import RangeFacetedSearchForm
from django.utils.translation import ugettext_lazy as _
from progetti.models import Progetto, ClassificazioneQSN

class ExtendedFacetedSearchView(SearchView):
    """
    Extends the SearchView class, allowing building filters and breadcrumbs
    for faceted navigation
    """
    __name__ = 'ExtendedFacetedSearchView'

    ## simplified date-ranges definitions
    SIXMONTHS = '[NOW/DAY-180DAYS TO NOW/DAY]'
    ONEYEAR   = '[NOW/DAY-365DAYS TO NOW/DAY]'
    TWOYEARS  = '[NOW/DAY-730DAYS TO NOW/DAY]'

    COST_RANGES = {
        '0TO1K':      '[* TO 1000]',
        '1KTO10K':    '[1001 TO 10000]',
        '10KTO100K':  '[10001 TO 100000]',
        '100KTOINF':  '[100001 TO *]',
    }

    def __init__(self, *args, **kwargs):
        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = RangeFacetedSearchForm

        super(ExtendedFacetedSearchView, self).__init__(*args, **kwargs)

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        # This way the form can always receive a list containing zero or more
        # facet expressions:
        form_kwargs['selected_facets'] = self.request.GET.getlist('selected_facets')

        return super(ExtendedFacetedSearchView, self).build_form(form_kwargs)

    def _get_extended_facets_fields(self):
        """
        Returns the facets fields information along with a *is_facet_selected*
        field, that allows easy filtering of the selected facets in the
        navigation filters
        """
        selected_facets = self.request.GET.getlist('selected_facets')
        facet_counts_fields = self.results.facet_counts().get('fields', {})

        facets = {'fields': {}, 'dates': {}, 'queries': {}}
        for field, counts in facet_counts_fields.iteritems():
            facets['fields'][field] = {'is_field_selected': False, 'counts': []}
            for count in counts:
                if count > 0:
                    facet = list(count)
                    is_facet_selected = "%s:%s" % (field, facet[0]) in selected_facets
                    facet.append(is_facet_selected)
                    facets['fields'][field]['counts'].append(facet)
                    if is_facet_selected:
                        facets['fields'][field]['is_field_selected'] = True

        return facets

    def _get_extended_selected_facets(self):
        """
        Returns the selected_facets list, in an extended dictionary,
        in order to make it easy to write faceted navigation breadcrumbs
        with *unselect* urls
        unselecting a breadcrumb remove all following selections
        """

        ## original selected facets list
        selected_facets = self.request.GET.getlist('selected_facets')

        extended_selected_facets = []
        for f in selected_facets:
            ## start building unselection url
            url = "?q=%s" % self.query
            for cf in selected_facets:
                if cf != f:
                    url += "&amp;selected_facets=%s" % cf
            field, x, label = f.partition(":")

            r_label = label
            if field == 'tipo_operazione':
                r_label = dict(Progetto.TIPO_OPERAZIONE)[label]

            # TODO: use an associative array
            if label == self.SIXMONTHS:
                r_label = 'ultimi sei mesi'
            elif label == self.ONEYEAR:
                r_label = 'ultimo anno'
            elif label == self.TWOYEARS:
                r_label = 'ultimi due anni'

            elif label == self.COST_RANGES['0TO1K']:
                r_label = 'da 0 a 1.000&euro;'
            elif label == self.COST_RANGES['1KTO10K']:
                r_label = 'da 1.000 a 10.000&euro;'
            elif label == self.COST_RANGES['10KTO100K']:
                r_label = 'da 10.000 a 100.000&euro;'
            elif label == self.COST_RANGES['100KTOINF']:
                r_label = 'oltre 100.000&euro;'


            sf = {'field': field, 'label': label, 'r_label': r_label, 'url': url}
            extended_selected_facets.append(sf)

        return extended_selected_facets

    def _get_custom_facet_queries_date(self):
        """

        """
        selected_facets = self.request.GET.getlist('selected_facets')
        facet_counts_queries = self.results.facet_counts().get('queries', {})

        facets = {'is_selected': False}
        if "data_inizio:%s" % self.SIXMONTHS in facet_counts_queries:
            facets['sixmonths'] = {
                'key': "data_inizio:%s" % self.SIXMONTHS,
                'count': facet_counts_queries["data_inizio:%s" % self.SIXMONTHS]
            }
            if facets['sixmonths']['key'] in selected_facets:
                facets['is_selected'] = True

        if "data_inizio:%s" % self.ONEYEAR in facet_counts_queries:
            facets['oneyear'] = {
                'key': "data_inizio:%s" % self.ONEYEAR,
                'count': facet_counts_queries["data_inizio:%s" % self.ONEYEAR]
            }
            if facets['oneyear']['key'] in selected_facets:
                facets['is_selected'] = True

        if "data_inizio:%s" % self.TWOYEARS in facet_counts_queries:
            facets['twoyears'] = {
                'key': "data_inizio:%s" % self.TWOYEARS,
                'count': facet_counts_queries["data_inizio:%s" % self.TWOYEARS]
            }
            if facets['twoyears']['key'] in selected_facets:
                facets['is_selected'] = True

        return facets

    def _get_custom_facet_queries_cost(self):
        """

        """
        selected_facets = self.request.GET.getlist('selected_facets')
        facet_counts_queries = self.results.facet_counts().get('queries', {})

        facets = {'is_selected': False}
        for r in ('0TO1K', '1KTO10K', '10KTO100K', '100KTOINF'):
            if "costo:%s" % self.COST_RANGES[r] in facet_counts_queries:
                facets['costrange_'+r] = {
                    'key': "costo:%s" % self.COST_RANGES[r],
                    'count': facet_counts_queries["costo:%s" % self.COST_RANGES[r]]
                }
                if facets['costrange_'+r]['key'] in selected_facets:
                    facets['is_selected'] = True

        return facets


    def extra_context(self):
        """

        Builds extra context, to build facets filters and breadcrumbs

        """
        extra = super(ExtendedFacetedSearchView, self).extra_context()
        extra['n_results'] = len(self.results)
        extra['request'] = self.request
        extra['selected_facets'] = self._get_extended_selected_facets()
        extra['facets'] = self._get_extended_facets_fields()
        extra['facet_queries_date'] = self._get_custom_facet_queries_date()
        extra['facet_queries_cost'] = self._get_custom_facet_queries_cost()

        # make get array as mutable QueryDict
        params = self.request.GET.copy()
        if 'q' not in params:
            params.update({'q': ''})
        if 'page' in params:
            params.pop('page')
        extra['params'] = params

        return extra

