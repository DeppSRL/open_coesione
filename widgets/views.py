from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.utils import importlib
from django.views.generic import TemplateView


__author__ = 'daniele'


WIDGETS = getattr(settings, 'WIDGETS', False) or []


def import_widget(path):
    try:
        parts = path.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        msg = "Could not import '%s'. %s: %s." % (path, e.__class__.__name__, e)
        raise ImportError(msg)


class WidgetSelectorMixin(object):

    # request
    # kwargs
    # widget_classes

    def get_widget(self):
        if self.get_widget_code() is None:
            return None
        return self.get_widget_class(self.get_widget_code())(self.request)

    def get_widget_code(self):
        return self.kwargs.get('widget', None)
        #raise NotImplemented("Need to implement method {0}.get_widget_code()".format(self.__class__.__name__))

    @property
    def widgets(self):
        if not hasattr(self, 'widget_classes'):
            self.widget_classes = {}
            for path in WIDGETS:
                widget_class = import_widget(path)
                self.widget_classes[widget_class.code] = widget_class
        return self.widget_classes

    def get_widget_class(self, code):
        """
        this method load a class through the code defined in settings.
        """
        if code not in self.widgets:
            raise ImproperlyConfigured("Cannot load a widget with code '{0}'".format(code))

        return self.widgets[code]


class WidgetBuilderView(TemplateView, WidgetSelectorMixin):
    """
    This class renders a template with a widget builder if its name is provided
    in GET parameters. Else it shows a list of available widget builders.
    """
    template_name = 'widgets/builder.html'

    def get_context_data(self, **kwargs):

        context = super(WidgetBuilderView, self).get_context_data(**kwargs)
        context['available_widgets'] = [(w.code, w.title) for w in self.widgets.values()]
        if not self.get_widget_code() is None:
            context['widget'] = self.get_widget()
        return context


class WidgetView(TemplateView, WidgetSelectorMixin):

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response with a template rendered with the given context.
        """
        widget = self.get_widget()
        return self.response_class(
            request=self.request,
            template=widget.get_template_name(),
            context=widget.get_context_data(),
            **response_kwargs
        )

    def get(self, request, *args, **kwargs):
        response = super(WidgetView, self).get(request, *args, **kwargs)
        # add CORS
        if isinstance(response, HttpResponse):
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Max-Age'] = '120'
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = 'HEAD, GET, OPTIONS, POST, DELETE'
            response['Access-Control-Allow-Headers'] = 'origin, content-type, accept, x-requested-with'
        return response

#class WidgetView(TemplateView, WidgetSelectorMixin):
#    """
#    This is a abstract view that handle a widget request.
#
#    """
#    widget_name = None
#
#    def get_template_names(self):
#        if not self.widget_name:
#            raise NotImplemented("Please set a widget_name in {0}".format(self.__class__))
#        return ["widgets/{0}_widget.html".format(self.widget_name)]
#
#    def get_object(self, queryset=None):
#        assert False, "Implement get_object"
#
#    def get_context_data(self, *args, **kwargs):
#        view = self.get_aggregate_page_view_class()(kwargs=kwargs)
#        self.object = view.object = self.get_object()
#        tematizzazione = self.request.GET.get('tematizzazione', 'costi')
#        page_view = setup_view(
#            view,
#            RequestFactory().get("{0}?tematizzazione=totale_{1}".format(self.get_aggregate_page_url(), tematizzazione)),
#            *args, **kwargs
#        )
#        context = page_view.get_context_data(*args, **kwargs)
#        context['widget'] = self.widget_name
#        return context
#
#    def get_aggregate_page_view_class(self):
#        assert False, "Implement get_aggregate_page_view_class"
#
#    def get_aggregate_page_url(self):
#        return self.get_object().get_absolute_url()
#
#
#class TerritorioWidgetView(WidgetView):
#    widget_name = 'territorio'
#
#    def get_object(self, queryset=None):
#        return Territorio.objects.get(slug=self.request.GET.get('territorio', False) or 'ambito-nazionale')
#
#    def get_aggregate_page_view_class(self):
#        return TerritorioView
#
#
#class NaturaWidgetView(WidgetView):
#    widget_name = 'natura'
#
#
#class TemaWidgetView(WidgetView):
#    widget_name = 'tema'