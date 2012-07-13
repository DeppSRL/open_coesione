"""
These mixins allow to use custom range facets on different fields.
Ranges must be defined in the extending class.
The extending class, must also extend a View (possibly a SearchView) class,
in order to make the self.request work.
"""
class FacetRangeNProgettiMixin:
    N_PROGETTI_RANGES = {}

    def get_custom_facet_queries_n_progetti(self):
        """
        return a structure to work with custom range facets
        """
        selected_facets = self.request.GET.getlist('selected_facets')
        facet_counts_queries = self.results.facet_counts().get('queries', {})

        facets = {'is_selected': False, 'ranges': []}
        for r in sorted(self.N_PROGETTI_RANGES.keys()):
            if "n_progetti:%s" % self.N_PROGETTI_RANGES[r]['qrange'] in facet_counts_queries:
                facets['ranges'].append({
                    'key': "n_progetti:%s" % self.N_PROGETTI_RANGES[r]['qrange'],
                    'count': facet_counts_queries["n_progetti:%s" % self.N_PROGETTI_RANGES[r]['qrange']],
                    'label': self.N_PROGETTI_RANGES[r]['r_label']
                })
                if "n_progetti:%s" % self.N_PROGETTI_RANGES[r]['qrange'] in selected_facets:
                    facets['is_selected'] = True

        return facets


    def add_n_progetti_extended_selected_facets(self, extended_selected_facets):
        for selected_facet in extended_selected_facets:
            if selected_facet['field'] == 'n_progetti':
                for range in self.N_PROGETTI_RANGES.keys():
                    if selected_facet['label'] == self.N_PROGETTI_RANGES[range]['qrange']:
                        selected_facet['r_label'] = self.N_PROGETTI_RANGES[range]['r_label']
        return extended_selected_facets



class FacetRangeCostoMixin:
    COST_RANGES = {}

    def get_custom_facet_queries_costo(self):
        """

        """
        selected_facets = self.request.GET.getlist('selected_facets')
        facet_counts_queries = self.results.facet_counts().get('queries', {})

        facets = {'is_selected': False, 'ranges': []}
        for r in sorted(self.COST_RANGES.keys()):
            if "costo:%s" % self.COST_RANGES[r]['qrange'] in facet_counts_queries:
                facets['ranges'].append({
                    'key': "costo:%s" % self.COST_RANGES[r]['qrange'],
                    'count': facet_counts_queries["costo:%s" % self.COST_RANGES[r]['qrange']],
                    'label': self.COST_RANGES[r]['r_label']
                })
                if "costo:%s" % self.COST_RANGES[r]['qrange'] in selected_facets:
                    facets['is_selected'] = True

        return facets


    def add_costo_extended_selected_facets(self, extended_selected_facets):
        for selected_facet in extended_selected_facets:
            if selected_facet['field'] == 'costo':
                for range in self.COST_RANGES.keys():
                    if selected_facet['label'] == self.COST_RANGES[range]['qrange']:
                        selected_facet['r_label'] = self.COST_RANGES[range]['r_label']
        return extended_selected_facets
