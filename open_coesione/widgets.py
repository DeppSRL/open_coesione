# coding=utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from django import forms
from api.query import request
from widgets.models import Widget

__author__ = 'joke2k'


class AggregateWidget(Widget):

    code = ''

    _COMPONENTS = (
        ('temi', 'Classificazione per tema'),
        ('nature', 'Visualizza le nature'),
        ('top_progetti', 'Visualizza i 5 progetti più finanziati'),
        ('progetti_conclusi', 'Visualizza gli ultimi 5 progetti conclusi'),
    )
    EXCLUDED_COMPONENT = None

    @property
    def COMPONENTS(self):
        return filter(lambda x: x[0] != self.EXCLUDED_COMPONENT, self._COMPONENTS)

    API_PATH = ''
    API_TOPIC = ''
    INITIAL_TOPIC = '', '--'

    def get_context_data(self):
        context = super(AggregateWidget, self).get_context_data()
        if self.is_valid():
            cleaned_data = self.data
            url = 'aggregati'
            topic = cleaned_data.get(self.API_TOPIC, None)
            if topic:
                url += '/{0}{1}'.format(self.API_PATH, topic)
            context.update(request(url))

            if 'top_progetti' in cleaned_data['component_set']:
                data = {'order_by': '-costo', 'page_size': 5}
                if topic:
                    data[self.API_TOPIC] = topic
                context.update({'top_progetti': request('progetti', **data)})

            if 'progetti_conclusi' in cleaned_data['component_set']:
                data = {'order_by': '-data_fine_effettiva', 'page_size': 5}
                if topic:
                    data[self.API_TOPIC] = topic
                context.update({'progetti_conclusi': request('progetti', **data)})

        return context

    def get_form(self):
        form = super(AggregateWidget, self).get_form()
        form.fields[self.API_TOPIC] = self.get_topic_field()
        form.fields['component_set'] = forms.MultipleChoiceField(
            label="Componenti da visualizzare", required=False, choices=self.COMPONENTS,
            widget=forms.CheckboxSelectMultiple)
        return form

    def get_topic_field(self):
        choices = self.get_topic_choices()
        if choices:
            return forms.ChoiceField(choices=choices, initial=choices[0][0])
        return forms.CharField()

    def get_topic_choices(self):
        pass

    def get_topic(self):
        return self.raw_data.get(self.API_TOPIC, self.INITIAL_TOPIC[0])

    def get_title(self):
        choices = self.get_topic_choices()
        if choices:
            if self.API_TOPIC in self.raw_data and self.raw_data.get(self.API_TOPIC):
                return "{0}: {1}".format(self.name, filter(lambda x: x[0] == self.raw_data.get(self.API_TOPIC), choices)[0][1])
            else:
                return "{0}: {1}".format(self.name, choices[0][1])
        return self.title

    def get_initial(self):
        initial = super(AggregateWidget, self).get_initial()
        choices = self.get_topic_choices()

        initial.update({
            'component_set': [x[0] for x in self.COMPONENTS],
            self.API_TOPIC: (choices[0] if choices else getattr(self, 'INITIAL_TOPIC'))[0]
        })

        return initial