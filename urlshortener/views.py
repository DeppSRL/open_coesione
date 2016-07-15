# -*- coding: utf-8 -*-
from django.http import Http404
from django.views.generic import RedirectView
from models import URL


class ShortURLRedirectView(RedirectView):
    def get_redirect_url(self, **kwargs):
        try:
            url = URL.objects.get_by_code(kwargs['code'])
        except:
            raise Http404
        else:
            url.visit_count += 1
            url.save()

            return url.url
