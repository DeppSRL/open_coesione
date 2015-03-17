from django import template
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
import simplejson

register = template.Library()


@register.filter
def jsonify(object):
    if isinstance(object, QuerySet):
        json = serialize('json', object)
    else:
        json = simplejson.dumps(object)

    return mark_safe(json)
