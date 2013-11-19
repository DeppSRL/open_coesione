# coding=utf-8
from django.conf import settings
from django.test import RequestFactory
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from open_coesione.utils import setup_view
from open_coesione.views import HomeView
from progetti.models import Progetto, Tema, ProgrammaAsseObiettivo, Ruolo, ClassificazioneQSN
from progetti.urls import sqs as progetti_sqs
from progetti.views import TemaView, TipologiaView
from soggetti.urls import sqs as soggetti_sqs
from api.serializers import *
from soggetti.views import SoggettoView
from territori.models import Territorio
from django.utils.datastructures import SortedDict
from territori.views import AmbitoNazionaleView, AmbitoEsteroView, RegioneView, ProvinciaView, ComuneView, MapnikProvinceView, MapnikRegioniView, MapnikComuniView


@api_view(('GET',))
def api_root(request, format=None):
    """
    This is the root entry-point of the OpenCoesione APIs.

    The APIs are read-only, freely accessible to all through HTTP requests at ``http://www.opencoesione.gov/api``.

    Responses are emitted in both **browseable-HTML** and **JSON** formats (``http://www.opencoesione.gov/api/.json``)

    To serve all requests and avoid slow responses or downtimes due to misuse, we limit the requests rate.
    When accessing the API **anonymously**, your client is limited to **12 requests per minute** from the same IP.
    You can contact us to become an **authenticated API user** (it's still free),
    then the rate-limit would be lifted to **1 request per second**.

    If for some reasons, you need to scrape all the Open Coesione data, please consider a bulk **CSV download**.
    See the ``http://www.opencoesione.gov.it/open-data/`` page in the web site.
    """
    return Response(
        SortedDict([
            ('progetti', reverse('api-progetto-list', request=request, format=format)),
            ('soggetti', reverse('api-soggetto-list', request=request, format=format)),
            ('aggregati', reverse('api-aggregati-home', request=request, format=format)),
            ('temi', reverse('api-tema-list', request=request, format=format)),
            ('nature', reverse('api-natura-list', request=request, format=format)),
            ('territori', reverse('api-territorio-list', request=request, format=format)),
            ('programmi', reverse('api-programma-list', request=request, format=format)),
            ('classificazioni', reverse('api-classificazione-list', request=request, format=format)),
        ])
    )

class ProgettoList(generics.ListAPIView):
    """
    List of all **progetti**.

    Progetti can be filtered through ``natura``, ``tema`` and ``territorio`` filters in the GET query-string parameters.
    Filters use slugs, and multiple filters can be built.

    Slugs values to be used in the filters are shown in the progetto list, and the complete lists can be extracted at:

    * ``/api/temi``
    * ``/api/nature``
    * ``/api/territori``

    Examples
    ========

    * ``/api/progetti?natura=incentivi-alle-imprese``
    * ``/api/progetti?tema=istruzione``
    * ``/api/progetti?natura=incentivi-alle-imprese&tema=istruzione``
    * ``/api/progetti?natura=incentivi-alle-imprese&tema=istruzione``
    * ``/api/progetti?territorio=palermo-comune``
    * ``/api/progetti?natura=incentivi-alle-imprese&tema=istruzione&territorio=roma-comune``
    * ``/api/progetti?soggetto=miur``

    The results are paginated by default to 25 items per page.
    The number of items per page can be changed through the ``page_size`` GET parameter.
    100 is the maximum value allowed for the page_size parameter.

    Results are sorted by default by descending costs (``-costo``).
    You can change the sorting order, using the ``order_by`` GET parameter.
    These are the possible values:

    * ``-costo`` (default), ``costo``
    * ``-pagamento``, ``pagamento``
    * ``-perc_pagamento``, ``perc_pagamento``
    * ``-data_inizio_effettiva``, ``data_inizio_effettiva``
    * ``-data_fine_effettiva``, ``data_fine_effettiva``

    a minus (-) in front of the field name indicates a *descending* order criterion.

    """
    pagination_serializer_class = PaginatedProgettoSerializer
    serializer_class = ProgettoSearchResultSerializer

    def get_paginate_by(self, queryset=None):
        if self.paginate_by_param:
            query_params = self.request.QUERY_PARAMS
            try:
                return min(int(query_params.get(self.paginate_by_param, settings.REST_FRAMEWORK['PAGINATE_BY'])), self.paginate_by)
            except (KeyError, ValueError):
                pass

        return self.paginate_by


    def get_queryset(self):

        ret_sqs = progetti_sqs.all()

        natura_slug = self.request.QUERY_PARAMS.get('natura', None)
        if natura_slug:
            natura = ClassificazioneAzione.objects.get(slug=natura_slug)
            ret_sqs = ret_sqs.filter(natura=natura.codice)

        tema_slug = self.request.QUERY_PARAMS.get('tema', None)
        if tema_slug:
            tema = Tema.objects.get(slug=tema_slug)
            ret_sqs = ret_sqs.filter(tema=tema.codice)

        territorio_slug = self.request.QUERY_PARAMS.get('territorio', None)
        if territorio_slug:
            territorio = Territorio.objects.get(slug=territorio_slug)
            if territorio.territorio == Territorio.TERRITORIO.R:
                ret_sqs = ret_sqs.filter(territorio_reg=territorio.cod_reg)
            if territorio.territorio == Territorio.TERRITORIO.P:
                ret_sqs = ret_sqs.filter(territorio_prov=territorio.cod_prov)
            if territorio.territorio == Territorio.TERRITORIO.C:
                ret_sqs = ret_sqs.filter(territorio_com=territorio.cod_com)

        programma = self.request.QUERY_PARAMS.get('programma', None)
        if programma:
            ret_sqs = ret_sqs.filter(fonte_fin=programma)

        soggetto = self.request.QUERY_PARAMS.get('soggetto', None)
        if soggetto:
            ret_sqs = ret_sqs.filter(soggetto=soggetto)

        sort_field = self.request.QUERY_PARAMS.get('order_by')
        sortable_fields = (
            'costo',
            '-pagamento', 'pagamento',
            '-perc_pagamento', 'perc_pagamento',
            '-data_fine_effettiva', 'data_fine_effettiva',
            '-data_inizio_effettiva', 'data_inizio_effettiva'
        )
        if sort_field and sort_field in sortable_fields:
            # reset default order_by parameter set in progetti.search_querysets.sqs definition
            ret_sqs.query.order_by = []
            ret_sqs = ret_sqs.order_by(sort_field)

        return ret_sqs



class ProgettoDetail(generics.RetrieveAPIView):
    queryset = Progetto.objects.all()
    serializer_class = ProgettoModelSerializer


class SoggettoList(generics.ListAPIView):
    """
    List of all **soggetti**.

    Soggetti can be filtered through ``tema`` and ``ruolo`` filters in the GET query-string parameters.
    Filters use slugs, and multiple filters can be built.

    Slugs values to be used in the filters are shown in the soggetto list.

    Examples
    ========

    * ``/api/soggetti?tema=competitivita-imprese``
    * ``/api/soggetti?ruolo=attuatore``
    * ``/api/soggetti?tema=istruzione&ruolo=attuatore``


    The results are paginated by default to 25 items per page.
    The number of items per page can be changed through the ``page_size`` GET parameter.
    100 is the maximum value allowed for the page_size parameter.

    Results are sorted by default by descending total projects' costs (``-costo``).
    You can change the sorting order, using the ``order_by`` GET parameter.
    These are the possible values:

    * ``-costo`` (default)
    * ``-n_progetti``, ``n_progetti``

    a minus (-) in front of the field name indicates a *descending* order criterion.
    """
    pagination_serializer_class = PaginatedSoggettoSerializer
    serializer_class = SoggettoSearchResultSerializer

    def get_paginate_by(self, queryset=None):
        if self.paginate_by_param:
            query_params = self.request.QUERY_PARAMS
            try:
                return min(int(query_params.get(self.paginate_by_param, settings.REST_FRAMEWORK['PAGINATE_BY'])), self.paginate_by)
            except (KeyError, ValueError):
                pass

        return self.paginate_by


    def get_queryset(self):
        ret_sqs = soggetti_sqs.all()

        tema_slug = self.request.QUERY_PARAMS.get('tema', None)
        if tema_slug:
            tema = Tema.objects.get(slug=tema_slug)
            ret_sqs = ret_sqs.filter(tema=tema.codice)

        ruolo = self.request.QUERY_PARAMS.get('ruolo', None)
        if ruolo:
            ruolo_code = Ruolo.inv_ruoli_dict[ruolo]
            ret_sqs = ret_sqs.filter(ruolo=ruolo_code)

        sort_field = self.request.QUERY_PARAMS.get('order_by')
        sortable_fields = (
            'costo',
            '-n_progetti', 'n_progetti',
        )
        if sort_field and sort_field in sortable_fields:
            # reset default order_by parameter set in soggetti.search_querysets.sqs definition
            ret_sqs.query.order_by = []
            ret_sqs = ret_sqs.order_by(sort_field)

        return ret_sqs



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


class ProgrammiList(generics.ListAPIView):
    """
    List of all programmi operativi.

    Can be filtered by ``descrizione`` GET parameter, to extract all items containing a given substring, case-insensitive.

    Examples
    ========

    To filter ``FSE`` and ``FESR`` groups::

        GET api/programmi?descrizione=FSE
        GET api/programmi?descrizione=FESR

    To get all programmi for a given region

        GET api/programmi?descrizione=Lazio

    To filter on codice::

        GET api/programmmi?codice=2007IT052PO012

    """
    serializer_class = ProgrammaModelSerializer

    def get_queryset(self):
        ret_qs = ProgrammaAsseObiettivo.objects.all()

        descrizione = self.request.GET.get('descrizione', None)
        if descrizione:
            ret_qs = ret_qs.filter(descrizione__icontains=descrizione)

        codice = self.request.GET.get('codice', None)
        if codice:
            if codice.startswith('^'):
                ret_qs = ret_qs.filter(codice__startswith=codice[1:])
            elif ',' in codice:
                ret_qs = ret_qs.filter(codice__in=codice.split(','))
            else:
                ret_qs = ret_qs.filter(codice=codice)

        return ret_qs


class ClassificazioneList(generics.ListAPIView):
    """
    List of all classificazioni of quadro strategico nazionale (QSN).

    Can be filtered by ``descrizione`` GET parameter, to extract all items containing a given substring, case-insensitive.

    Examples
    ========

    To get all classificazioni for a given topic

        GET api/classificazioni?descrizione=occupazione

    """
    serializer_class = ClassificazioneQSNModelSerializer
    model = ClassificazioneQSN
    paginate_by = 100

    #def get_queryset(self):
    #    ret_qs = ClassificazioneQSN.objects.filter(tipo_classificazione=ClassificazioneQSN.TIPO.priorita)
    #
    #    descrizione = self.request.GET.get('descrizione', None)
    #    if descrizione:
    #        ret_qs = ret_qs.filter(descrizione__icontains=descrizione)
    #
    #    return ret_qs

@api_view(('GET',))
def api_aggregati_temi_list(request, format=None):
    """
    Shows URLs linking to aggregated temi pages.
    """
    queryset = Tema.objects.filter(tipo_tema='sintetico')
    ret = SortedDict()
    for item in queryset:
        ret[item.slug] = reverse('api-aggregati-tema-detail', request=request, format=format, kwargs={'slug': item.slug})

    return Response(ret)


@api_view(('GET',))
def api_aggregati_nature_list(request, format=None):
    """
    Shows URLs linking to aggregated nature pages.
    """
    queryset = ClassificazioneAzione.objects.filter(tipo_classificazione='natura')
    ret = SortedDict()
    for item in queryset:
        ret[item.slug] = reverse('api-aggregati-natura-detail', request=request, format=format, kwargs={'slug': item.slug})

    return Response(ret)


@api_view(('GET',))
def api_aggregati_territori_list(request, format=None):
    """
    Shows URLs linking to aggregated regioni and province pages.
    """
    ret = SortedDict([
        ('ambito_estero', reverse('api-aggregati-territorio-detail', request=request, format=format, kwargs={'slug': 'ambito-estero'})),
        ('ambito_nazionale', reverse('api-aggregati-territorio-detail', request=request, format=format, kwargs={'slug': 'ambito-nazionale'})),
        ('regioni', get_regioni_list(request, format)),
        ('provincie', get_province_list(request, format)),
    ])

    return Response(ret)



#
# helper functions used to extract list of urls for territori aggregated data
#

def get_territori_list(request, format=None, queryset=None):
    if not queryset:
        raise APIException("Need to specify queryset")
    ret = SortedDict()
    for item in queryset:
        ret[item.slug] = reverse('api-aggregati-territorio-detail', request=request, format=format, kwargs={'slug': item.slug})
    return ret

def get_regioni_list(request, format=None):
    return get_territori_list(request, format, queryset=Territorio.objects.regioni())

def get_province_list(request, format=None, regione=None):
    qs = Territorio.objects.provincie()
    if regione:
        return get_territori_list(request, format, queryset=qs.filter(cod_reg=regione.cod_reg))
    else:
        return get_territori_list(request, format, queryset=qs.all())


def get_comuni_list(request, format=None, regione=None, provincia=None):
    if not regione and not provincia:
        raise APIException("Need to specify a regione or a provincia")
    if regione and provincia:
        raise APIException("Need to specify just a regione OR a provincia")

    if regione:
        return get_territori_list(request, format, queryset=Territorio.objects.comuni().filter(cod_reg=regione.cod_reg))
    if provincia:
        return get_territori_list(request, format, queryset=Territorio.objects.comuni().filter(cod_prov=provincia.cod_prov))

def get_comuni_provincia_list(request, format=None, provincia=None):
    if not provincia:
        raise APIException("Need to specify a provincia")
    return get_territori_list(request, format, queryset=Territorio.objects.comuni().filter(cod_prov=provincia.cod_prov))



class AggregatoView(APIView):
    """
    Base aggregated data view. Used to show home page data, and as a base for other pages.

    Set ``with_territori`` GET parameter to ``False`` to de-activate territori list (useful for speeding testing)
    """

    totali = {}
    temi = SortedDict()
    nature = SortedDict()
    territori = SortedDict()

    def get_aggregate_page_url(self):
        return "/"

    def get_aggregate_page_view_class(self):
        return HomeView

    def get_mapnik_names(self):
        return [
            (MapnikRegioniView, 'territori_mapnik_regioni', 'regioni', {}),
            (MapnikProvinceView, 'territori_mapnik_province', 'province', {}),
        ]

    def get_extra_context(self):
        ret = SortedDict([

        ])
        return None

    def get_navigation_links(self, request, format=None):
        return SortedDict([
            ('ambito-estero', reverse('api-aggregati-territorio-detail', request=request, format=format, kwargs={'slug': 'ambito-estero'})),
            ('ambito-nazionale', reverse('api-aggregati-territorio-detail', request=request, format=format, kwargs={'slug': 'ambito-nazionale'})),
            ('regioni', get_regioni_list(request, format)),
        ])



    def update_totali(self, context, thematization):
        self.totali[thematization] = context['totale_{0}'.format(thematization)]


    def update_temi(self, format, context, thematization):
        for t in context['temi_principali']:
            if not self.temi.get(t.slug, None):
                self.temi[t.slug] = {
                    'label': t.short_label,
                    'codice': t.codice,
                    'link': reverse('api-aggregati-tema-detail', request=self.request, format=format, kwargs={'slug': t.slug}),
                    'totali': {}
                }
            self.temi[t.slug]['totali'][thematization] = t.tot

    def update_nature(self, format, context, thematization):
        for n in context['nature_principali']:
            if not self.nature.get(n.slug, None):
                self.nature[n.slug] = {
                    'label': n.short_label,
                    'codice': n.codice,
                    'link': reverse('api-aggregati-natura-detail', request=self.request, format=format, kwargs={'slug': n.slug}),
                    'totali': {}
                }
            self.nature[n.slug]['totali'][thematization] = n.tot

    def update_territori(self, tipo_territorio, format, context, thematization):
        for (t,v) in context['data'].iteritems():
            if not self.territori.get(tipo_territorio, None):
                self.territori[tipo_territorio] = SortedDict()
            if not self.territori[tipo_territorio].get(t, None):
                self.territori[tipo_territorio][t] = {
                    'link': reverse('api-aggregati-territorio-detail', request=self.request, format=format, kwargs={'slug': t}),
                    'totali': {}
                }
            self.territori[tipo_territorio][t]['totali'][thematization] = v

    def get(self, request, format=None, *args, **kwargs):
        """
        returns Response with computed context information on the aggregate
        """

        view = self.get_aggregate_page_view_class()(kwargs=kwargs)


        if 'slug' in self.kwargs and self.kwargs['slug'] == 'ambito-nazionale':
            del kwargs['slug']

        with_territori = self.request.QUERY_PARAMS.get('with_territori', None)
        if not with_territori or with_territori.lower == 'true' or with_territori == '1' or with_territori.lower == 'yes':
            with_territori = True
        else:
            with_territori = False

        if 'slug' in self.kwargs and self.kwargs['slug'] == 'ambito-nazionale':
            del kwargs['slug']

        for thematization in ('costi', 'pagamenti', 'progetti'):
            page_view = setup_view(
                view,
                RequestFactory().get("{0}?tematizzazione=totale_{1}".format(self.get_aggregate_page_url(), thematization)),
                *args, **kwargs
            )
            if hasattr(page_view, 'get_object'):
                page_view.object = getattr(page_view, 'get_object')()
            context = page_view.get_context_data(*args, **kwargs)

            self.update_totali(context, thematization)

            if 'temi_principali' in context:
                self.update_temi(format, context, thematization)

            if 'nature_principali' in context:
                self.update_nature(format, context, thematization)

            print "with_territori: ", with_territori

            if with_territori:
                for (mapnik_view_name, mapnik_url_name, tipo_territori, mapnik_kwargs) in self.get_mapnik_names():
                    map_view = setup_view(
                         mapnik_view_name(),
                         RequestFactory().get("{0}?tematizzazione=totale_{1}".format(reverse(mapnik_url_name, *args, kwargs=mapnik_kwargs), thematization)),
                         *args, **kwargs
                    )
                    map_context = map_view.get_context_data(*args, **mapnik_kwargs)
                    self.update_territori(tipo_territori, format,  map_context, thematization)

        aggregated_data = SortedDict([
            ('totali', self.totali),
            ('temi', self.temi),
            ('nature', self.nature),
            ('territori', self.territori),
        ])


        return Response(SortedDict([
            ('contesto', self.get_extra_context()),
            ('aggregati', aggregated_data),
        ]))




class AggregatoTemaDetailView(AggregatoView):
    """
    AggregatoView subclass to handle a selected tema page
    """
    def get_aggregate_page_view_class(self):
        return TemaView

    def get_aggregate_page_url(self):
        return "/progetti/temi/{0}/".format(self.kwargs['slug'])


class AggregatoNaturaDetailView(AggregatoView):
    """
    AggregatoView subclass to handle a selected natura page
    """
    def get_aggregate_page_view_class(self):
        return TipologiaView

    def get_aggregate_page_url(self):
        return "/progetti/nature/{0}/".format(self.kwargs['slug'])

class AggregatoTerritorioDetailView(AggregatoView):
    """
    AggregatoView subclass to handle a selected territorio page
    """
    def get_slug(self):
        return self.kwargs['slug']

    def get_territorio(self):
        tipo = self.get_tipo()
        if tipo == 'nazionale':
            return Territorio.objects.nazione()
        return Territorio.objects.get(slug=self.get_slug())

    def get_tipo(self):
        """
        returns a tipo from a slug
        """
        return self.get_slug().split('-')[-1:][0]

    def pluralize_tipo(self, tipo):
        if tipo == u'regione':
            return u'regioni'
        elif tipo == u'provincia':
            return u'province'
        elif tipo == u'comune':
            return u'comuni'
        else:
            return tipo

    def get_aggregate_page_view_class(self):
        """
        Get the class type dynamically from the territorio-slug
        """
        slug = self.get_slug()
        if slug == u'ambito-nazionale':
            return AmbitoNazionaleView
        elif slug == u'ambito-estero':
            return AmbitoEsteroView
        else:
            tipo = self.get_tipo()
            if tipo == u'regione':
                return RegioneView
            elif tipo == u'provincia':
                return ProvinciaView
            elif tipo == u'comune':
                return ComuneView
            else:
                raise Exception(u'Wrong tipo: {0}'.format(tipo))

    def get_aggregate_page_url(self):
        slug = self.get_slug()
        tipo = self.get_tipo()
        if tipo is 'estero' and tipo is 'nazionale':
            return "/territori/{0}/".format(slug)
        else:
            return "/territori/{0}/{1}/".format(self.pluralize_tipo(tipo), slug)

    def get_extra_context(self):
        if self.get_tipo() == 'estero':
            return SortedDict([
                ('nome_territorio', 'Ambito Estero'),
                ('tipo_territorio', Territorio.TERRITORIO.E),
                ('popolazione', ''),
            ])
        territorio = self.get_territorio()
        return SortedDict([
            ('nome_territorio', territorio.denominazione),
            ('tipo_territorio', territorio.territorio),
            ('popolazione', territorio.popolazione_totale),
        ])


    def get_mapnik_names(self):
        tipo = self.get_tipo()
        if tipo in ('nazionale', 'estero'):
            return []

        selected_territorio = Territorio.objects.get(slug=self.get_slug())

        if tipo == 'regione':
            mapnik_kwargs = {'cod_reg': selected_territorio.cod_reg}
            return [
                (MapnikProvinceView, 'territori_mapnik_province_regione', 'province', mapnik_kwargs),
                (MapnikComuniView, 'territori_mapnik_comuni_regione', 'comuni', mapnik_kwargs)
            ]
        elif tipo == 'provincia':
            mapnik_kwargs = {'cod_prov': selected_territorio.cod_prov}
            return [
                (MapnikComuniView, 'territori_mapnik_comuni_provincia', 'comuni', mapnik_kwargs)
            ]
        elif tipo == 'comune':
            return []



class SoggettoDetail(AggregatoView, generics.RetrieveAPIView):
    queryset = Soggetto.objects.all()
    serializer_class = SoggettoModelSerializer

    def get_aggregate_page_view_class(self):
        return SoggettoView

    def get_aggregate_page_url(self):
        return "/soggetti/{0}/".format(self.kwargs['slug'])

    def update_territori(self, tipo_territorio, format, context, thematization):
        for (territorio, v) in context['lista_finanziamenti_per_regione']:
            t = territorio.slug
            if not self.territori.get(tipo_territorio, None):
                self.territori[tipo_territorio] = SortedDict()
            if not self.territori[tipo_territorio].get(t, None):
                self.territori[tipo_territorio][t] = {
                    'link': reverse('api-aggregati-territorio-detail', request=self.request, format=format, kwargs={'slug': t}),
                    'totali': {}
                }
            self.territori[tipo_territorio][t]['totali'][thematization] = v

    def get(self, request, format=None, *args, **kwargs):
        """
        this code is a copy of AggregatoView.get
        without mapnik requests
        """

        response = generics.RetrieveAPIView.get(self, request, format=format, *args, **kwargs)

        view = self.get_aggregate_page_view_class()(kwargs=kwargs)
        if hasattr(view, 'get_object'):
            view.object = getattr(view, 'get_object')()

        for thematization in ('costi', 'pagamenti', 'progetti'):
            page_view = setup_view(
                view,
                RequestFactory().get("{0}?tematizzazione=totale_{1}".format(self.get_aggregate_page_url(), thematization)),
                *args, **kwargs
            )
            context = page_view.get_context_data(*args, **kwargs)

            self.update_totali(context, thematization)

            if 'temi_principali' in context:
                self.update_temi(format, context, thematization)

            if 'nature_principali' in context:
                self.update_nature(format, context, thematization)

            self.update_territori('regioni', format,  context, thematization)

        aggregated_data = SortedDict([
            ('totali', self.totali),
            ('temi', self.temi),
            ('nature', self.nature),
            ('territori', self.territori),
        ])

        response.data['aggregati'] = aggregated_data

        # preparo i territori più finanziati
        response.data['territori_piu_finanziati_pro_capite'] = sorted([
            {
                'link': reverse('api-aggregati-territorio-detail', request=self.request, format=format, kwargs={'slug': t.slug}),
                'territorio': t.denominazione,
                'slug': t.slug,
                'pro_capite': t.totale,
            }
            # per ogni territorio
            for t in context['territori_piu_finanziati_pro_capite']
        # ordinati per il totale pro capite
        ], key=lambda x: x['pro_capite'], reverse=True)

        # preparo la classifica dei collaboratori
        response.data['top_collaboratori'] = sorted([
            {
                'link': reverse('api-soggetto-detail', request=self.request, format=format, kwargs={'slug': s['soggetto'].slug}),
                'soggetto': s['soggetto'].denominazione,
                'slug': s['soggetto'].slug,
                'numero_progetti': s['numero'],
            }
            for s in context['top_collaboratori']
        # ordinati per il numero di progetti
        ], key=lambda x: x['numero_progetti'], reverse=True)

        # preparo la classifica dei progetti
        response.data['top_progetti'] = sorted([
            {
                'link': reverse('api-progetto-detail', request=self.request, format=format, kwargs={'slug': p.slug}),
                'titolo_progetto': p.titolo_progetto,
                'slug': p.slug,
                'fin_totale_pubblico': p.fin_totale_pubblico,
            }
            for p in context['top_progetti']
        ], key=lambda x: x['fin_totale_pubblico'], reverse=True)
        return response
