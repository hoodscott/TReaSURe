from django.template import Library
from django.template.defaultfilters import stringfilter
import re

register = Library()

@stringfilter
def nospace(value):
    return value.replace(' ', '')

register.filter(nospace)
