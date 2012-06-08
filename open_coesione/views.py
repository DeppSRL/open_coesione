from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView


class AggregatoView(object):
    raise Exception("Class AggregatoView needs to be implemented")

class HomeView(AggregatoView, TemplateView):
    template_name = 'homepage.html'
