from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from localita.views import RegionDetailView, RegionListView, ProvinceListView, ProvinceDetailView, MunicipalityDetailView

urlpatterns = patterns('',
   url(r'^$', TemplateView.as_view(template_name='localita/leaflet.html')),
   url(r'^regioni.json$',
       RegionListView.as_view(), name='json_province_list_url'),
   url(r'^province.json$',
       ProvinceListView.as_view(), name='json_region_list_url'),
   url(r'^regione/(?P<cod_reg>[^/]+)/(?P<type>[^/]).json$',
       RegionDetailView.as_view(), name='json_region_details_url'),
   url(r'^provincia/(?P<cod_prov>[^/]+).json$',
       ProvinceDetailView.as_view(), name='json_province_details_url'),
   url(r'^comune/(?P<cod_com>[^/]+).json$',
       MunicipalityDetailView.as_view(), name='json_municipality_details_url'),
)
