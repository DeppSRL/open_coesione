from django import template
register = template.Library()

@register.filter
def progetti_search_url(obj):
    return obj.get_progetti_search_url()

@register.filter
def progetti_search_url_by_natura(obj, natura):
    return obj.get_progetti_search_url(natura=natura)

@register.filter
def progetti_search_url_by_tema(obj, tema):
    return obj.get_progetti_search_url(tema=tema)
