from django import forms
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.safestring import mark_safe

## custom widget to prevent autocapitalisation and autocompletion of certail fields
class DisableAutoInput(forms.widgets.Input):
   input_type = 'text'

   def render(self, name, value, attrs=None):
       if attrs is None:
           attrs = {}
       attrs.update(dict(autocorrect='off',
                         autocapitalize='off',
                         spellcheck='false'))
       return super(DisableAutoInput, self).render(name, value, attrs=attrs)
