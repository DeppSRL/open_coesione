# -*- coding: utf-8 -*-
from django.utils.functional import cached_property
from haystack.views import SearchView
from forms import OCFacetedSearchForm, format_facet_field
from territori.models import Territorio


class ExtendedFacetedSearchView(SearchView):
    """
    Extends the SearchView class, allowing building filters and breadcrumbs for faceted navigation
    """
    RANGES = {}

    def __init__(self, *args, **kwargs):
        if kwargs.get('load_all') is None:
            kwargs['load_all'] = False

        # Needed to switch out the default form class.
        if kwargs.get('form_class') is None:
            kwargs['form_class'] = OCFacetedSearchForm

        super(ExtendedFacetedSearchView, self).__init__(*args, **kwargs)

    @staticmethod
    def _get_objects_by_pk(pks):
        return {}

    def build_page(self):
        (paginator, page) = super(ExtendedFacetedSearchView, self).build_page()

        objects_by_pk = self._get_objects_by_pk(object.pk for object in page.object_list)
        for object in page.object_list:
            try:
                object.object = objects_by_pk[object.pk]
            except KeyError:
                pass

        return paginator, page

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        # This way the form can always receive a list containing zero or more facet expressions.
        # form_kwargs can contain the selected_facets, since ProgettoSearchView sets a default initial facet (is_active:1)
        if 'selected_facets' in form_kwargs:
            form_kwargs['selected_facets'] += self.request.GET.getlist('selected_facets')
        else:
            form_kwargs['selected_facets'] = self.request.GET.getlist('selected_facets')

        return super(ExtendedFacetedSearchView, self).build_form(form_kwargs)

    def _build_facet_field_info(self, field, label, key_to_labels):
        facet_counts_fields = self.results.facet_counts().get('fields', {})

        facet = {}
        if field in facet_counts_fields:
            facet['label'] = label
            facet['values'] = [
                {
                    'key': c[0],
                    'label': key_to_labels[c[0]][0],
                    'short_label': key_to_labels[c[0]][1],
                    'count': c[1],
                    'urls': self._get_facet_urls(field, c[0]),
                } for c in facet_counts_fields[field]]

        return facet

    def _build_range_facet_queries_info(self, field, label):
        facet_counts_queries = self.results.facet_counts().get('queries', {})

        facet = {}
        if field in self.RANGES:
            ranges = self.RANGES[field]

            facet['label'] = label
            facet['values'] = [
                {
                    'key': ranges[range]['qrange'],
                    'label': ranges[range]['label'],
                    'short_label': ranges[range]['label'],
                    'count': facet_counts_queries.get('{}:{}'.format(format_facet_field(field), ranges[range]['qrange'])),
                    'urls': self._get_facet_urls(field, ranges[range]['qrange']),
                } for range in sorted(ranges.keys())]

        return facet

    def _get_facet_urls(self, facet, key):
        facet_key = '{}:{}'.format(facet, key)

        params = self.params

        urls = {'add_filter': False, 'remove_filter': False}

        if facet_key in params.getlist('selected_facets'):
            params.getlist('selected_facets').remove(facet_key)
            urls['remove_filter'] = params.urlencode(safe=':')
        else:
            params.getlist('selected_facets').append(facet_key)
            urls['add_filter'] = params.urlencode(safe=':')

        return urls

    @property
    def params(self):
        params = self.request.GET.copy()

        if 'q' not in params:
            params['q'] = ''
        if 'page' in params:
            del(params['page'])

        params.setlist('selected_facets', sorted(set(params.getlist('selected_facets'))))

        return params


class OCFacetedSearchView(ExtendedFacetedSearchView):
    def extra_context(self):
        extra = super(OCFacetedSearchView, self).extra_context()

        territorio_com = self.request.GET.get('territorio_com')
        territorio_prov = self.request.GET.get('territorio_prov')
        territorio_reg = self.request.GET.get('territorio_reg')

        if territorio_com and territorio_com != '0':
            extra['territorio'] = Territorio.objects.comuni().get(cod_com=territorio_com).nome
        elif territorio_prov and territorio_prov != '0':
            extra['territorio'] = Territorio.objects.provincie().get(cod_prov=territorio_prov).nome_con_provincia
        elif territorio_reg:
            extra['territorio'] = Territorio.objects.regioni(with_nation=True).get(cod_reg=territorio_reg).nome

        return extra
