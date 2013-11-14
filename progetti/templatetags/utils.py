from django import template

register = template.Library()

def key(d, key_name):
    try:
        value = d[str(key_name)]
    except KeyError:
        from django.conf import settings
        value = "(%s)"%key_name
    return value
key = register.filter('key', key)


@register.filter
def topic(project, topic_name):
    try:
        topic_name = {
            'costo': 'fin_totale_pubblico',
        }[topic_name]
    except KeyError:
        pass
    return project.get(topic_name, '')