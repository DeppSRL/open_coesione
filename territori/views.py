from django.views.generic.detail import DetailView
from open_coesione.views import AggregatoView


class LuogoView(AggregatoView, DetailView):
    #raise Exception("Class LuogoView needs to be implemented")
    pass


class RegioneView(LuogoView):
    #raise Exception("Class RegioneView needs to be implemented")
    pass

class ProvinciaView(LuogoView):
    #raise Exception("Class ProvinciaView needs to be implemented")
    pass

class ComuneView(LuogoView):
    #raise Exception("Class ComuneView needs to be implemented")
    pass