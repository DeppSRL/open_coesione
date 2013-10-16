from django.views.generic import TemplateView

__author__ = 'daniele'


class WidgetBuilderView(TemplateView):
    template_name = 'widgets/builder.html'

    def get_context_data(self, **kwargs):

        context = super(WidgetBuilderView, self).get_context_data(**kwargs)

        return context


class WidgetView(TemplateView):

    def get_template_names(self):
        return ["widgets/widget_{0}.html".format(self.kwargs.get('widget', 'empty'))]

    def get_context_data(self, **kwargs):

        from . import api

        context = super(WidgetView, self).get_context_data(**kwargs)

        params = self.request.GET.dict()
        context.update({
            'params': params,
            'result_set': api.request('progetti', **params)
        })

        return context
