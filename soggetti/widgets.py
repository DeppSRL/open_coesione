from __future__ import absolute_import
from django import forms
from api.query import request
from widgets.models import Widget


__author__ = 'daniele'


class SoggettoWidget(Widget):

    code = "soggetto"
    title = "Soggetto"

    def get_context_data(self):
        context = super(SoggettoWidget, self).get_context_data()
        if self.get_form().is_valid():
            cleaned_data = self.get_form().cleaned_data
            context['soggetto'] = request('soggetti/{0}'.format(cleaned_data['soggetto']))
            context['top_progetti'] = request('progetti',
                                              soggetto=cleaned_data['soggetto'],
                                              order_by='-costo', page_size='5')
        return context

    def build_form_fields(self, form):
        form.fields['soggetto'] = forms.CharField()
        super(SoggettoWidget, self).build_form_fields(form)
        del form.fields['title']

    def get_initial(self):
        initial = super(SoggettoWidget, self).get_initial()
        initial['soggetto'] = 'miur'
        return initial
