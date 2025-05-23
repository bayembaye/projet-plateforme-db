# accounts/templatetags/math_filters.py
from django import template

register = template.Library()

@register.filter(name='subtract')
def subtract(value, arg):
    """Soustrait arg de value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value