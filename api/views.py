from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from progetti.models import Progetto, Tema
from progetti.urls import sqs as progetti_sqs
from soggetti.urls import sqs as soggetti_sqs
from api.serializers import *
from territori.models import Territorio


@api_view(('GET',))
def api_root(request, format=None):
    """
    This is the root of the OpenCoesione API.

    Qui descrivo come usare le API *Pippo*.
    """
    return Response({
        'progetti': reverse('api-progetto-list', request=request, format=format),
        'soggetti': reverse('api-soggetto-list', request=request, format=format),
        'temi': reverse('api-tema-list', request=request, format=format),
        'nature': reverse('api-natura-list', request=request, format=format),
        'territori': reverse('api-territorio-list', request=request, format=format),
        'custom': reverse('a-custom-view', request=request, format=format),
    })


class ProgettoList(generics.ListAPIView):
    """
    List all **progetti**, showing relevant data.

    Progetti can be filtered through ``natura`` and ``tema`` filters in the GET query-string parameters.

    The results are paginated, by default to 100 items per page.
    The number of items per page can be changed through the ``page_size`` GET parameter.
    100 is the maximum value allowed for the page_size parameter.
    """
    pagination_serializer_class = PaginatedProgettoSerializer
    serializer_class = ProgettoSearchResultSerializer

    def get_paginate_by(self, queryset=None):
        if self.paginate_by_param:
            query_params = self.request.QUERY_PARAMS
            try:
                return min(int(query_params[self.paginate_by_param]), self.paginate_by)
            except (KeyError, ValueError):
                pass

        return self.paginate_by


    def get_queryset(self):
        natura = self.request.GET.get('natura', None)
        tema = self.request.GET.get('tema', None)
        cod_reg = self.request.GET.get('cod_reg', None)
        cod_prov = self.request.GET.get('cod_prov', None)
        cod_com = self.request.GET.get('cod_com', None)

        ret_sqs = progetti_sqs.all()

        if natura:
            ret_sqs = ret_sqs.filter(natura=natura)
        if tema:
            ret_sqs = ret_sqs.filter(tema=tema)

        if cod_reg:
            ret_sqs = ret_sqs.filter(territorio_reg=cod_reg)
        if cod_prov:
            ret_sqs = ret_sqs.filter(territorio_prov=cod_prov)
        if cod_com:
            ret_sqs = ret_sqs.filter(territorio_com=cod_com)

        return ret_sqs



class ProgettoDetail(generics.RetrieveAPIView):
    queryset = Progetto.objects.all()
    serializer_class = ProgettoModelSerializer





class SoggettoList(generics.ListAPIView):
    """
    List all soggetti
    """
    pagination_serializer_class = PaginatedSoggettoSerializer
    serializer_class = SoggettoSearchResultSerializer

    def get_paginate_by(self, queryset=None):
        if self.paginate_by_param:
            query_params = self.request.QUERY_PARAMS
            try:
                return min(int(query_params[self.paginate_by_param]), self.paginate_by)
            except (KeyError, ValueError):
                pass

        return self.paginate_by


    def get_queryset(self):
        tema = self.request.GET.get('tema', None)
        ruolo = self.request.GET.get('ruolo', None)

        ret_sqs = soggetti_sqs.all()

        if tema:
            ret_sqs = ret_sqs.filter(tema=tema)

        if ruolo:
            ret_sqs = ret_sqs.filter(ruolo=ruolo)

        return ret_sqs


class SoggettoDetail(generics.RetrieveAPIView):
    queryset = Soggetto.objects.all()
    serializer_class = SoggettoModelSerializer




class TemaList(generics.ListAPIView):
    """
    List all Temi
    """
    queryset = Tema.objects.filter(tipo_tema='sintetico')
    serializer_class = TemaModelSerializer


class NaturaList(generics.ListAPIView):
    """
    Elenco di tutte le nature
    """
    queryset = ClassificazioneAzione.objects.filter(tipo_classificazione='natura')
    serializer_class = NaturaModelSerializer


class TerritorioList(generics.ListAPIView):
    """
    Elenco di tutti i territori

    Filtrabili per

     * ``tipo_territorio`` (C, R, P, N, E)
     * ``cod_com`` (codice ISTAT del comune: Roma-58091)
     * ``cod_prov`` (codice ISTAT della provincia: Roma-58)
     * ``cod_reg`` (codice ISTAT della regione: Lazio-12)
     * ``denominazione`` (estrae tutti i territori che iniziano per ...)
    """
    serializer_class = TerritorioModelSerializer

    def get_queryset(self):
        tipo_territorio = self.request.GET.get('tipo_territorio', None)
        cod_reg = self.request.GET.get('cod_reg', None)
        cod_prov = self.request.GET.get('cod_prov', None)
        cod_com = self.request.GET.get('cod_com', None)
        denominazione = self.request.GET.get('denominazione', None)

        ret_qs = Territorio.objects.all()

        if tipo_territorio:
            ret_qs = ret_qs.filter(territorio=tipo_territorio)

        if cod_reg:
            ret_qs = ret_qs.filter(cod_reg=cod_reg)

        if cod_prov:
            ret_qs = ret_qs.filter(cod_prov=cod_prov)

        if cod_com:
            ret_qs = ret_qs.filter(cod_com=cod_com)

        if denominazione:
            ret_qs = ret_qs.filter(denominazione__istartswith=denominazione)

        return ret_qs



class MyCustomView(APIView):
    """
    This is a custom view that can be anything at all. It's not using a serializer class,
    but I can define my own parameters like so!

    horse -- the name of your horse

    """
    def get(self, *args, **kwargs):
        """ Docs there """
        return Response({'foo':'bar'})
