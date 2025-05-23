from django import template

register = template.Library()

@register.filter
def filter_grade_range(submissions, range_str):
    try:
        min_val, max_val = map(float, range_str.split(','))
    except:
        return submissions.none()
    
    return [s for s in submissions if s.grade and min_val <= s.grade < max_val]


# submissions/templatetags/submission_tags.py (nouveau fichier)

from django import template
from django.template.defaultfilters import stringfilter
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
@stringfilter
def to_json(value):
    return json.loads(value)