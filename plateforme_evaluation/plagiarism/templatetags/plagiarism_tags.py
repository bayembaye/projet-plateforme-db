from django import template

register = template.Library()

@register.filter(name='status_badge')
def status_badge(status):
    badge_classes = {
        'pending': 'bg-info',
        'processing': 'bg-primary',
        'completed': 'bg-success',
        'failed': 'bg-danger'
    }
    return badge_classes.get(status.lower(), 'bg-secondary')

@register.filter(name='score_color')
def score_color(score):
    if score is None:
        return 'secondary'
    if score < 30:
        return 'success'
    elif score < 60:
        return 'warning'
    else:
        return 'danger'