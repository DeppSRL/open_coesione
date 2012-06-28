from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from open_coesione.views import AggregatoView, AccessControlView

class SoggettiView(AggregatoView, TemplateView):
    #raise Exception("Class SoggettiView needs to be implemented")
    pass

class SoggettoView(AccessControlView, DetailView):
    #raise Exception("Class SoggettoView needs to be implemented")
    pass