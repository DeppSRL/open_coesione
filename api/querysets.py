# -*- coding: utf-8 -*-
from haystack.models import SearchResult

__author__ = 'guglielmo'


class PatchedSearchResult(SearchResult):
    """
    Patched to raise an exception when self.__iter__ is called.
    Used by django_rest_framework, when serializing paginated objects
    """
    def __getattr__(self, attr):
        if attr in ('__getnewargs__', '__iter__', ):
            raise AttributeError

        return self.__dict__.get(attr, None)
