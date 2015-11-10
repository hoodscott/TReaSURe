from django import forms
from treasure.models import Resource, Teacher
#from django.contrib.auth.models import User

class ResourceForm(forms.ModelForm):
    resourcename = forms.CharField(max_length=128, help_text="Please enter the resource name.")
    #tree = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    #author = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    # An inline class to provide additional information on the form.
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Resource
        
class TeacherForm(forms.ModelForm):
    username = forms.CharField(max_length=128, help_text="Please enter a username.")
    firstname = forms.CharField(max_length=128, help_text="Please enter your first name.")
    surname = forms.CharField(max_length=128, help_text="Please enter your surname.")

    # An inline class to provide additional information on the form.
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Teacher
