from django.views.generic import TemplateView
from territori.models import Territorio

__author__ = 'daniele'


class WidgetBuilderView(TemplateView):
    template_name = 'widgets/builder.html'

    def get_context_data(self, **kwargs):

        context = super(WidgetBuilderView, self).get_context_data(**kwargs)

        return context


class WidgetView(TemplateView):
    """
    This is a abstract view that handle a widget request.

    """
    widget_name = None

    def get_template_names(self):
        if not self.widget_name:
            raise NotImplemented("Please set a widget_name in {0}".format(self.__class__))
        return ["widgets/widget_{0}.html".format(self.widget_name)]

    def get_context_data(self, **kwargs):

        #from . import api

        context = super(WidgetView, self).get_context_data(**kwargs)

        params = self.request.GET.dict()
        context.update({
            'params': params,
            #'result_set': api.request('aggregati/territori/', **params)
        })

        return context


class TerritorioWidgetView(WidgetView):
    widget_name = 'territorio'

    def get_context_data(self, **kwargs):

        context = super(TerritorioWidgetView, self).get_context_data(**kwargs)

        # prendo gli aggregati (temi e nature)
        uri = 'aggregati'   # volontariamente senza slash finale
        territorio = self.request.GET.get('territorio', None)
        if territorio:
            uri += '/territori/{0}'.format(territorio)
            context['object'] = Territorio.objects.get(slug=territorio)

        from . import api
        data = api.request(uri)
        context.update(data)

        import time
        time.sleep(1)

        # prendo i TOP 5 progetti
        uri = 'progetti?page_size=5'
        if territorio:
            uri += '&territorio={0}'.format(territorio)
        data = api.request(uri)
        context['top_progetti_per_costo'] = data['results']

        return context


class NaturaWidgetView(WidgetView):
    widget_name = 'natura'


class TemaWidgetView(WidgetView):
    widget_name = 'tema'