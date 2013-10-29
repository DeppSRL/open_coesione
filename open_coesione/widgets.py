# coding=utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from django import forms
from api.query import request
from widgets.models import Widget

__author__ = 'joke2k'


class AggregateWidget(Widget):

    code = ''
    title = ""

    EXCLUDE_TITLE = False

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
        if self.get_form().is_valid():
            cleaned_data = self.get_form().cleaned_data
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

    def build_form_fields(self, form):
        #form.fields['tematizzazione'] = forms.ChoiceField(
        #    label='Tematizzazione',
        #    initial='costi',
        #    choices=(('costi', 'Costi'), ('pagamenti', 'Pagamenti'), ('progetti', 'Progetti'))
        #)
        form.fields[self.API_TOPIC] = self.get_topic_field()
        super(AggregateWidget, self).build_form_fields(form)
        form.fields['component_set'] = forms.MultipleChoiceField(
            label="Componenti da visualizzare", required=False, choices=self.COMPONENTS,
            widget=forms.CheckboxSelectMultiple)
        if self.EXCLUDE_TITLE:
            del form.fields['title']

    def get_topic_field(self):
        choices = self.get_topic_choices()
        if choices:
            return forms.ChoiceField(choices=choices, initial=choices[0][0])
        return forms.CharField()

    def get_topic_choices(self):
        pass

    def get_title(self):
        choices = self.get_topic_choices()
        if self.EXCLUDE_TITLE:
            if choices:
                if self.API_TOPIC in self.request.GET and self.request.GET[self.API_TOPIC]:
                    return "{0}: {1}".format(self.title, filter(lambda x: x[0] == self.request.GET[self.API_TOPIC], choices)[0][1])
                else:
                    return "{0}: {1}".format(self.title, choices[0][1])
            return self.title
        return self.request.GET.get('title', "{0}: {1}".format(self.title, choices[0][1]) if choices else self.title)

    def get_initial(self):
        initial = super(AggregateWidget, self).get_initial()
        initial.update({
            'title': self.title,
            'component_set': [x[0] for x in self.COMPONENTS],
        })
        initial_topic, initial_topic_label = self.get_initial_topic()
        if initial_topic:
            initial[self.API_TOPIC] = initial_topic
            initial['title'] += ": {1}".format(self.title, initial_topic_label)

        return initial

    def get_initial_topic(self):
        choices = self.get_topic_choices()
        if choices:
            return choices[0]
        return self.INITIAL_TOPIC