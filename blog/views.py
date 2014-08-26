from django.conf import settings
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from blog.models import Entry
from open_coesione.views import PilloleView
from tagging.views import TagFilterMixin
from open_coesione.mixins import DateFilterMixin

# from tagging.models import TaggedItem
# from django.contrib.contenttypes.models import ContentType

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

        context['related_pillole'] = PilloleView(request=self.request).get_queryset() if self._get_tag_filter_value() else None

        return context

class BlogEntryView(DetailView):
    model = Entry

def blogEntryItem(request, slug):
    entry = get_object_or_404(Entry, slug=slug);
    return render_to_response('blog/entry_item.html', {'full_view': True, 'title_linked': True, 'object': entry, 'SITE_URL': 'http://' + Site.objects.get(pk=settings.SITE_ID).domain})

# class BlogByTagView(BlogView):
#     def get_queryset(self):
#         return Entry.objects.filter(tagged_items__tag__slug=self.kwargs['slug'])
#         # entry_ids = []
#         # entry_type = ContentType.objects.get_for_model(Entry)
#         # taggeditems = TaggedItem.objects.filter(tag__slug=self.kwargs['slug'], content_type=entry_type)
#         # for taggeditem in taggeditems:
#         #     entry_ids.append(taggeditem.object_id)
#         # return Entry.objects.filter(id__in=entry_ids)
#
# class BlogByDateView(BlogView):
#     def get_queryset(self):
#         now = timezone.now()
#         start_date = now.date()
#         end_date = start_date + datetime.timedelta(days = 1)
#         if self.kwargs['date'] == 'w':
#           start_date = start_date - datetime.timedelta(days=7)
#         elif self.kwargs['date'] == 'm':
#           start_date = start_date.replace(day=1)
#         elif self.kwargs['date'] == 'y':
#           start_date = start_date.replace(month=1, day=1)
#         return Entry.objects.filter(published_at__gte=start_date, published_at__lt=end_date)
