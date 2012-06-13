from django.views.generic.detail import DetailView
from open_coesione.views import AggregatoView
from territori.models import Territorio


class LuogoView(AggregatoView, DetailView):

    def get_object(self, queryset=None):
        return Territorio.objects.get(denominazione=self.kwargs['slug'])


class RegioneView(LuogoView):
    #raise Exception("Class RegioneView needs to be implemented")
    pass

class ProvinciaView(LuogoView):
    #raise Exception("Class ProvinciaView needs to be implemented")
    pass

class ComuneView(LuogoView):
    #raise Exception("Class ComuneView needs to be implemented")
    pass