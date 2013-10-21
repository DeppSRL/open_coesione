from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.views.generic import TemplateView
from rest_framework.compat import RequestFactory
from open_coesione.utils import setup_view
from territori.views import TerritorioView
from territori.models import Territorio

__author__ = 'daniele'


class WidgetBuilderView(TemplateView):

    def get_widget_name(self):
        widget_name = self.request.GET.get('widget', None)
        if widget_name not in ('territorio', 'tema', 'natura', 'progetto', 'soggetto'):
            return None
        return widget_name

    def get_template_names(self):
        name = self.get_widget_name()
        if name is None:
            return 'widgets/builder.html'
        return ["widgets/{0}_builder.html".format(name)]

    def get_context_data(self, **kwargs):

        context = super(WidgetBuilderView, self).get_context_data(**kwargs)
        context['widget'] = self.get_widget_name()
        return context


class WidgetView(TemplateView):
    """
    This is a abstract view that handle a widget request.

    """
    widget_name = None

    def get_template_names(self):
        if not self.widget_name:
            raise NotImplemented("Please set a widget_name in {0}".format(self.__class__))
        return ["widgets/{0}_widget.html".format(self.widget_name)]

    def get_object(self, queryset=None):
        assert False, "Implement get_object"

    def get_context_data(self, *args, **kwargs):
        view = self.get_aggregate_page_view_class()(kwargs=kwargs)
        self.object = view.object = self.get_object()
        tematizzazione = self.request.GET.get('tematizzazione', 'costi')
        page_view = setup_view(
            view,
            RequestFactory().get("{0}?tematizzazione=totale_{1}".format(self.get_aggregate_page_url(), tematizzazione)),
            *args, **kwargs
        )
        context = page_view.get_context_data(*args, **kwargs)
        context['widget'] = self.widget_name
        return context

    def get_aggregate_page_view_class(self):
        assert False, "Implement get_aggregate_page_view_class"

    def get_aggregate_page_url(self):
        return self.get_object().get_absolute_url()


class TerritorioWidgetView(WidgetView):
    widget_name = 'territorio'

    def get_object(self, queryset=None):
        return Territorio.objects.get(slug=self.request.GET.get('territorio', False) or 'ambito-nazionale')

    def get_aggregate_page_view_class(self):
        return TerritorioView


class NaturaWidgetView(WidgetView):
    widget_name = 'natura'


class TemaWidgetView(WidgetView):
    widget_name = 'tema'