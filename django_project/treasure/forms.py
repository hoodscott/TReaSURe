from django import forms
from treasure.models import *
from django.contrib.auth.models import User

class ResourceForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the resource name.")
    description = forms.CharField(widget = forms.Textarea, help_text="Please enter a description.")
    tree = forms.CharField(widget = forms.HiddenInput(), required=False)
    user = forms.CharField(widget = forms.HiddenInput(), required=False)    
    
    level_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=0).order_by('name'),
                                                required=True, help_text="Please select level(s).")
    topic_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=True, help_text="Please select topic(s).")
    other_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False, help_text="Please select other tags (optional).")                                                
    
    class Meta:
        model = Resource
        fields = ('name','description', 'tree', 'user')
        exclude = []
        
class FileForm(forms.ModelForm):
    path = forms.FileField(label='Select the resource to upload', help_text='Maximum of 42MB')
    
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
    school = forms.ModelChoiceField(queryset=School.objects.all().order_by('name'),
                                                required=False, help_text="Please select your school.")
    hubs = forms.ModelMultipleChoiceField(queryset=Hub.objects.all().order_by('name'),
                                                required=False, help_text="Please select your hubs.")
                                                
    class Meta:
        model = Teacher
        fields = ('firstname', 'surname', 'school', 'hubs')
        exclude = []

class SchoolForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the name of the school.")
    town = forms.CharField(max_length=128, help_text="Please enter the town the school is in.")
    address = forms.CharField( widget = forms.Textarea, help_text="Please enter the address of the school.")
    latitude = forms.FloatField(help_text="Please enter the latitude of the school.")
    longitude = forms.FloatField(help_text="Please enter the longitude of the school.")

    class Meta:
        model = School
        fields = ('name', 'town', 'address', 'latitude', 'longitude')
        exclude = []
        
class HubForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the name of the hub.")
    address = forms.CharField( widget = forms.Textarea, help_text="Please enter the address of the hub.")
    latitude = forms.FloatField(help_text="Please enter the latitude of the hub.")
    longitude = forms.FloatField(help_text="Please enter the longitude of the hub.")

    class Meta:
        model = Hub
        fields = ('name', 'address', 'latitude', 'longitude')
        exclude = []
        
class SearchForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all().order_by('name'),
                                                required=False, help_text="Please select tags.")
