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


class CustomRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):

    """
        http://dashdrum.com/blog/2012/12/more-relatedfieldwidgetwrapper-the-popup/
        Based on RelatedFieldWidgetWrapper, this does the same thing
        outside of the admin interface

        the parameters for a relation and the admin site are replaced
        by a url for the add operation
    """

    def __init__(self, widget, add_url,permission=True):
        self.is_hidden = widget.is_hidden
        self.needs_multipart_form = widget.needs_multipart_form
        self.attrs = widget.attrs
        self.choices = widget.choices
        self.widget = widget
        self.add_url = add_url
        self.permission = permission

    def render(self, name, value, *args, **kwargs):
        self.widget.choices = self.choices
        output = [self.widget.render(name, value, *args, **kwargs)]
        if self.permission:
            output.append(u'<a href="%s" class="add-another btn btn-info" id="add_id_%s" onclick="return showAddAnotherPopup(this);">Add Another</a><br>' % \
                (self.add_url, name))
            #output.append(u'<img src="" width="10" height="10" alt="Add Another"/></a>')
        return mark_safe(u''.join(output))