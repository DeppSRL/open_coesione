from __future__ import absolute_import
from django import forms
from api.query import request
from widgets.models import Widget


__author__ = 'daniele'


class SoggettoWidget(Widget):

    code = "soggetto"
    name = "Soggetto"

    def get_context_data(self):
        context = super(SoggettoWidget, self).get_context_data()
        if self.is_valid():
            cleaned_data = self.get_data()
            context['soggetto'] = request('soggetti/{0}'.format(cleaned_data['soggetto']))
            context['top_progetti'] = request('progetti',
                                              soggetto=cleaned_data['soggetto'],
                                              order_by='-costo', page_size='5')
        return context

    def get_form(self):
        form = super(SoggettoWidget, self).get_form()
        form.fields['soggetto'] = forms.CharField()
        return form

    def get_initial(self):
        initial = super(SoggettoWidget, self).get_initial()
        initial['soggetto'] = 'miur-97429780584'
        return initial
