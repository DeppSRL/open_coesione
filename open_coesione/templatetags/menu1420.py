# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.inclusion_tag('commons/menu1420.html', takes_context=True)
def menu1420(context):
    request = context['request']

    items = [
        ['OpenCoesione nella programmazione 2014-2020', '/programmazione_2014_2020/'],
        ['Risorse', '/risorse_2014_2020/'],
        ['Programmi', '/programmi_2014_2020/'],
        ['Opportunità', '/opportunita_2014_2020/'],
        ['Bandi', '/bandi_2014_2020/'],
        ['Progetti', '/progetti_2014_2020/'],
        ['Aiuti', '/aiuti_2014_2020/'],
    ]

    for item in items:
        item.append(item[1] == request.path)

    return {
        'items': items,
    }
