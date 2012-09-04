from django.conf.urls import patterns, url
from django.views.generic.list import ListView
from blog.models import Entry

class BlogView(ListView):
    model = Entry

urlpatterns = patterns('',
    url(r'^$', BlogView.as_view(), name='blog_home')
)