from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from localita.views import RegionDetailView, RegionListView

urlpatterns = patterns('',
   url(r'^$', TemplateView.as_view(template_name='localita/leaflet.html')),
   url(r'^regioni.json$',
       RegionListView.as_view(), name='json_region_url'),
   url(r'^regione/(?P<cod_reg>[^/]+).json$',
       RegionDetailView.as_view(), name='json_region_url'),
)

