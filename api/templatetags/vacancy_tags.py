from django import template

register = template.Library()

@register.filter
def truncatechars(value, arg):
    if len(value) > arg:
        return value[:arg] + '...'
    return value