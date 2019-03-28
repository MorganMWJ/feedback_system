from django import template

register = template.Library()

@register.filter
def runtime_format(timedelta):
    total_seconds = int(timedelta.total_seconds())
    hours, remainder = divmod(total_seconds,60*60)
    minutes, seconds = divmod(remainder,60)
    return '{} hrs {} mins {} secs'.format(hours,minutes,seconds)

@register.filter
def question_time_format(timedelta):
    total_seconds = int(timedelta.total_seconds())
    hours, remainder = divmod(total_seconds,60*60)
    minutes, seconds = divmod(remainder,60)
    return 'Posted {} mins {} secs ago'.format(minutes,seconds)
