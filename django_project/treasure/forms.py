from django import forms
from treasure.models import *
from django.contrib.auth.models import User

class ResourceForm(forms.ModelForm):
    resourcename = forms.CharField(max_length=128, help_text="Please enter the resource name.")
    description = forms.CharField(widget = forms.Textarea, help_text="Please enter a description.")
    #tree = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Resource
        fields = ('resourcename','description')
        exclude = []
        
class FileForm(forms.ModelForm):
    path = forms.CharField(max_length=128, help_text="Please pretend to upload a file.")
    
    class Meta:
        model = FilesResource
        fields = ('path',)
        exclude = []
        
class WebForm(forms.ModelForm):
    url = forms.URLField(max_length=128, help_text="Please enter the url of the resource.")
    
    class Meta:
        model = WebResource
        fields = ('url',)
        exclude = []
              
class UserForm(forms.ModelForm):
    username = forms.CharField(help_text="Please enter a username.")
    email = forms.CharField(help_text="Please enter your email.")
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Please enter a password.")

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        exclude = []
        
class TeacherForm(forms.ModelForm):

	firstname = forms.CharField(max_length=128, help_text="Please enter your first name.")
	surname = forms.CharField(max_length=128, help_text="Please enter your surname.")

	class Meta:
		model = Teacher
		fields = ('firstname', 'surname')
                exclude = []

class SchoolForm(forms.ModelForm):
    schoolname = forms.CharField(max_length=128, help_text="Please enter the name of the school.")
    location = forms.CharField(max_length=128, help_text="Please enter the school's location.")
    address = forms.CharField(max_length=128, help_text="Please enter the school's address.")

    class Meta:
        model = School
        exclude = []
        
class HubForm(forms.ModelForm):
    hubname = forms.CharField(max_length=128, help_text="Please enter the name of the hub.")
    location = forms.CharField(max_length=128, help_text="Please enter the hub's location.")
    address = forms.CharField(max_length=128, help_text="Please enter the hub's address.")

    class Meta:
        model = Hub
        exclude = []
