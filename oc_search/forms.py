# -*- coding: utf-8 -*-
from django import forms
from haystack.backends import SQ
from haystack.forms import SearchForm


class RangeFacetedSearchForm(SearchForm):
    territorio_com = forms.IntegerField(required=False)
    territorio_prov = forms.IntegerField(required=False)
    territorio_reg = forms.IntegerField(required=False)
    territorio_tipo = forms.CharField(required=False)
    soggetto = forms.CharField(required=False)
    ruolo = forms.CharField(required=False)
    fonte_fin = forms.CharField(required=False)
    gruppo_programmi = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.selected_facets = kwargs.pop('selected_facets', [])
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
            if ':' not in facet:
                continue

            field, value = facet.split(':', 1)

            if value:
                if value[0] == '[' and value[-1] == ']':
                    sqs = sqs.narrow(u'{}:{}'.format(field, value))
                else:
                    sqs = sqs.narrow(u'{}:"{}"'.format(field, sqs.query.clean(value)))

        if self.is_valid():
            # aggiunge filtro soggetto, se presente
            soggetto = self.cleaned_data.get('soggetto')
            if soggetto:
                import operator
                from progetti.models import Ruolo

                codici_ruolo = dict(Ruolo.RUOLO).keys()

                # sqs = sqs.filter_and(reduce(operator.or_, (SQ(soggetto='{}|{}'.format(soggetto, r)) for r in codici_ruolo)))
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
