from django import template
from django.utils.safestring import mark_safe
import django.contrib.staticfiles
register = template.Library()

@register.simple_tag
def render_help_text(field):
    if hasattr(field, 'help_text'):
        return mark_safe(
            "<a><img src='/plancsharing/static/images/help.png' title='{help_text}' /></a>".format(**{'help_text': field.help_text})
        )
    return ''