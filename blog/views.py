# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from models import Entry
from open_coesione.views import PillolaListView
from tagging.views import TagFilterMixin
from open_coesione.mixins import DateFilterMixin


class BlogView(ListView, TagFilterMixin, DateFilterMixin):
    model = Entry

    def get_queryset(self):
        queryset = super(BlogView, self).get_queryset()
        queryset = self._apply_date_filter(queryset)
        queryset = self._apply_tag_filter(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(BlogView, self).get_context_data(**kwargs)
        context['date_choices'] = self._get_date_choices()
        context['tag_choices'] = self._get_tag_choices()

        context['related_pillole'] = PillolaListView(request=self.request).get_queryset() if self._get_tag_filter_value() else None

        return context


class BlogEntryView(DetailView):
    model = Entry


def blog_entry_item(request, slug):
    entry = get_object_or_404(Entry, slug=slug)
    return render_to_response('blog/entry_item.html', {'full_view': True, 'title_linked': True, 'object': entry, 'SITE_URL': 'http://' + Site.objects.get(pk=settings.SITE_ID).domain})
