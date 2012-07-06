from django import forms
from haystack.forms import SearchForm
import sys

class RangeFacetedSearchForm(SearchForm):
    territorio_id = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        self.selected_facets = kwargs.pop("selected_facets", [])
        super(RangeFacetedSearchForm, self).__init__(*args, **kwargs)

    def no_query_found(self):
        """
        Determines the behavior when no query was found.
        """
        return self.searchqueryset.all()

    def search(self):
        sqs = super(RangeFacetedSearchForm, self).search()

        # We need to process each facet to ensure that the field name and the
        # value are quoted correctly and separately:
        for facet in self.selected_facets:
            if ":" not in facet:
                continue

            field, value = facet.split(":", 1)

            if value:
                if  value[0]=='[' and value[-1]==']':
                    sqs = sqs.narrow(u'%s:%s' % (field, value))
                else:
                    sqs = sqs.narrow(u'%s:"%s"' % (field, sqs.query.clean(value)))

        # aggiunge filtro territorio, se presente
        if self.is_valid() and self.cleaned_data.get('territorio_id'):
            sqs = sqs.filter_and(territorio=self.cleaned_data['territorio_id'])

        return sqs
