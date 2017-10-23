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
    cup = forms.CharField(required=False)
    soggetto = forms.CharField(required=False)
    ruolo = forms.CharField(required=False)
    gruppo_programmi = forms.CharField(required=False)
    territorio_tipo = forms.CharField(required=False)
    territorio_com = forms.IntegerField(required=False)
    territorio_prov = forms.IntegerField(required=False)
    territorio_reg = forms.IntegerField(required=False)
    fonte_fin = forms.CharField(required=False)

    def search(self):
        sqs = super(OCFacetedSearchForm, self).search()

        if self.is_valid():
            # aggiunge filtro cups, se presente
            cups = self.cleaned_data.get('cup')
            if cups:
                sqs = sqs.filter(cup_s__in=cups.split('|'))

            # aggiunge filtro soggetto, se presente
            soggetto = self.cleaned_data.get('soggetto')
            if soggetto:
                from progetti.models import Ruolo

                codici_ruolo = dict(Ruolo.RUOLO).keys()

                sqs = sqs.filter(soggetto__in=['{}|{}'.format(soggetto, r) for r in codici_ruolo])

                ruolo = self.cleaned_data.get('ruolo')
                if ruolo:
                    for r in codici_ruolo:
                        condition = {'soggetto': '{}|{}'.format(soggetto, r)}
                        if r in ruolo:
                            sqs = sqs.filter(**condition)
                        else:
                            sqs = sqs.exclude(**condition)

            # aggiunge filtro gruppo_programmi, se presente
            gruppo_programmi_codice = self.cleaned_data.get('gruppo_programmi')
            if gruppo_programmi_codice:
                from progetti.gruppo_programmi import GruppoProgrammi
                try:
                    gruppo_programmi = GruppoProgrammi(codice=gruppo_programmi_codice)
                except:
                    pass
                else:
                    sqs = sqs.filter(fonte_fin__in=[p.codice for p in gruppo_programmi.programmi])

            # aggiunge filtri territorio e fonte_fin, se presenti
            for fld in ('territorio_tipo', 'territorio_com', 'territorio_prov', 'territorio_reg', 'fonte_fin'):
                val = self.cleaned_data.get(fld)
                if val or val == 0:
                    sqs = sqs.filter(**{fld: val})

        return sqs
