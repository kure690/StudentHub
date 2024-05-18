from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def add_time(value, minutes):
    try:
        time_obj = datetime.strptime(value, '%I:%M %p')
        new_time = time_obj + timedelta(minutes=minutes)
        return new_time.strftime('%I:%M %p')
    except ValueError:
        return value
    

@register.filter
def decrement(value):
    try:
        return int(value) - 1
    except ValueError:
        return value
    
    
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
    