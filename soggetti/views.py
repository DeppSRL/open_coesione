from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from open_coesione.views import AggregatoView

class SoggettiView(AggregatoView, TemplateView):
    raise Exception("Class SoggettiView needs to be implemented")

class SoggettoView(DetailView):
    raise Exception("Class SoggettoView needs to be implemented")
