from django import template

register = template.Library()

@register.filter
def score_color(score):
    if score is None:
        return 'secondary'
    if score < 30:
        return 'success'
    elif score < 60:
        return 'warning'
    else:
        return 'danger'

@register.filter
def status_badge(status):
    status_map = {
        'pending': 'info',
        'processing': 'primary',
        'completed': 'success',
        'failed': 'danger'
    }
    return status_map.get(status, 'secondary')