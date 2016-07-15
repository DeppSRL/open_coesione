# -*- coding: utf-8 -*-
from django import forms
from haystack.forms import SearchForm


format_facet_field = lambda x: '{{!ex={0}_tag}}{0}'.format(x)


class MultiSelectWithRangeFacetedSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        self.selected_facets = kwargs.pop('selected_facets', [])
        super(MultiSelectWithRangeFacetedSearchForm, self).__init__(*args, **kwargs)

    def no_query_found(self):
        return self.searchqueryset.all()

    def search(self):
        sqs = super(MultiSelectWithRangeFacetedSearchForm, self).search()

        for field, values in self._parse_selected_facets(self.selected_facets).items():
            if values:
                field = '{{!tag={0}_tag}}{0}'.format(field)
                sqs = sqs.narrow(u'{}:({})'.format(field, ' OR '.join(v if v.startswith('[') and v.endswith(']') else '"{}"'.format(sqs.query.clean(v)) for v in values)))

        return sqs

    def _parse_selected_facets(self, facets):
        from collections import defaultdict

        parsed_facets = defaultdict(list)

        for facet in facets:
            if ':' in facet:
                field, value = facet.split(':', 1)
                parsed_facets[field].append(value)

        return parsed_facets

    # def _parse_selected_facets(self, facets):
    #     from itertools import groupby
    #     return {k: [x[1] for x in g] for k, g in groupby(sorted((f.split(':', 1) for f in facets if ':' in f), key=lambda x: x[0]), key=lambda x: x[0])}


class OCFacetedSearchForm(MultiSelectWithRangeFacetedSearchForm):
    soggetto = forms.CharField(required=False)
    ruolo = forms.CharField(required=False)
    territorio_tipo = forms.CharField(required=False)
    territorio_com = forms.IntegerField(required=False)
    territorio_prov = forms.IntegerField(required=False)
    territorio_reg = forms.IntegerField(required=False)
    fonte_fin = forms.CharField(required=False)
    gruppo_programmi = forms.CharField(required=False)

    def search(self):
        sqs = super(OCFacetedSearchForm, self).search()

        if self.is_valid():
            # aggiunge filtro soggetto, se presente
            soggetto = self.cleaned_data.get('soggetto')
            if soggetto:
                from progetti.models import Ruolo

                codici_ruolo = dict(Ruolo.RUOLO).keys()

                sqs = sqs.filter_and(soggetto__in=['{}|{}'.format(soggetto, r) for r in codici_ruolo])

                ruolo = self.cleaned_data.get('ruolo')
                if ruolo:
                    for r in codici_ruolo:
                        condition = {'soggetto': '{}|{}'.format(soggetto, r)}
                        if r in ruolo:
                            sqs = sqs.filter_and(**condition)
                        else:
                            sqs = sqs.exclude(**condition)

            # aggiunge filtri territorio, se presenti
            if self.cleaned_data.get('territorio_tipo'):
                sqs = sqs.filter_and(territorio_tipo=self.cleaned_data['territorio_tipo'])
            if self.cleaned_data.get('territorio_com'):
                sqs = sqs.filter_and(territorio_com=self.cleaned_data['territorio_com'])
            if self.cleaned_data.get('territorio_prov'):
                sqs = sqs.filter_and(territorio_prov=self.cleaned_data['territorio_prov'])
            if self.cleaned_data.get('territorio_reg') or self.cleaned_data.get('territorio_reg') == 0:
                sqs = sqs.filter_and(territorio_reg=self.cleaned_data['territorio_reg'])

            # aggiunge filtro fonte_fin, se presente
            if self.cleaned_data.get('fonte_fin'):
                sqs = sqs.filter_and(fonte_fin=self.cleaned_data.get('fonte_fin'))

            # aggiunge filtro gruppo_programmi, se presente
            if self.cleaned_data.get('gruppo_programmi'):
                from progetti.gruppo_programmi import GruppoProgrammi
                try:
                    sqs = sqs.filter_and(fonte_fin__in=[p.codice for p in GruppoProgrammi(codice=self.cleaned_data.get('gruppo_programmi')).programmi])
                except:
                    pass

        return sqs
