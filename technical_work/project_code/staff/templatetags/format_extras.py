from django import template
import datetime

register = template.Library()

@register.filter
def runtime_format(total_seconds):
    hours, remainder = divmod(total_seconds,60*60)
    minutes, seconds = divmod(remainder,60)
    return '{} hrs {} mins {} secs'.format(hours,minutes,seconds)

@register.filter
def runtime_format_english_notation(total_seconds):
    return str(datetime.timedelta(seconds=total_seconds))

@register.filter
def question_time_format(timedelta):
    total_seconds = int(timedelta.total_seconds())
    hours, remainder = divmod(total_seconds,60*60)
    minutes, seconds = divmod(remainder,60)
    return 'Posted {} mins {} secs ago'.format(minutes,seconds)

@register.simple_tag
def session_numbering(counter, page_num, per_page):
    if(page_num<=1):
        return counter
    return ((page_num-1)*per_page)+counter
