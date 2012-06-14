from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from territori.views import RegioneView, ComuneView, ProvinciaView

urlpatterns = patterns('',
   url(r'^regioni/(?P<slug>[-\w]+)/$',
       RegioneView.as_view(), name='territori_regione'),
   url(r'^province/(?P<slug>[-\w]+)/$',
       ProvinciaView.as_view(), name='territori_provincia'),
   url(r'^comuni/(?P<slug>[-\w]+)/$',
       ComuneView.as_view(), name='territori_comune'),
   url(r'^polymaps.html$', TemplateView.as_view(template_name='territori/polymaps.html'), name='territori_polymaps'),
   url(r'^highcharts.html$', TemplateView.as_view(template_name='territori/highcharts.html'), name='territori_highcharts'),
)
