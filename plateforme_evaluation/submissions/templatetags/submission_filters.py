# submissions/templatetags/submission_filters.py
from django import template

register = template.Library()

@register.filter
def filter_grade_range(submissions, range_str):
    """
    Filters submissions by grade range.
    Usage: {{ submissions|filter_grade_range:"min,max" }}
    """
    try:
        min_grade, max_grade = map(float, range_str.split(','))
    except (ValueError, AttributeError):
        return submissions.none()  # Return empty queryset if invalid format
    
    return [s for s in submissions if min_grade <= (s.grade or 0) < max_grade]