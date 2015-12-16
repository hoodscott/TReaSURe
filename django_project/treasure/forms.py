from django import forms
from treasure.models import *
from django.contrib.auth.models import User

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

class ResourceForm(forms.ModelForm):
    name = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                            max_length=128,
                            help_text="Please enter the resource name.")
    
    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                        max_length=128,
                        help_text="Please enter a short description.")
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="Please enter the full description.",
                            required=False)
                            
    tree = forms.CharField(widget = forms.HiddenInput(), required=False)
    user = forms.CharField(widget = forms.HiddenInput(), required=False) 

    # stores the form of evolution (creation, amendment, etc.)
    evolution_type = forms.CharField(widget = forms.HiddenInput(), required=False)
    
    # should the resource be shown (basically deleted if not)
    hidden = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    # is this resource restricted to scottish teachers
    restricted = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    # what type of resource is this (file, web, something else?)
    resource_type = models.forms.CharField(widget = forms.HiddenInput(), required=False)
    
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=0).order_by('name'),
                                                required=True, help_text="Please select level(s).")
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=True, help_text="Please select topic(s).")
    other_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False, help_text="Please select other tags (optional).")                                                
    
    class Meta:
        model = Resource
        fields = ('name', 'summary', 'description', 'tree', 'user', 'evolution_type', 'hidden', 'restricted', 'resource_type')
        exclude = []
        
class FileForm(forms.ModelForm):
    path = forms.FileField(widget = forms.ClearableFileInput(attrs={'tabindex':'1'}),
                            label='Select the resource to upload',
                            help_text='Maximum of 42MB')
    
    class Meta:
        model = FilesResource
        fields = ('path',)
        exclude = []
        
class WebForm(forms.ModelForm):
    url = forms.URLField(widget = DisableAutoInput(attrs={'tabindex':'1'}),
                            max_length=128,
                            help_text="Please enter the url of the resource.")
    
    class Meta:
        model = WebResource
        fields = ('url',)
        exclude = []
              
class UserForm(forms.ModelForm):
    username = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                                help_text="Please enter a username.")
    email = forms.CharField(widget = DisableAutoInput(attrs={'tabindex':'1'}),
                            help_text = "Please enter your email.")
    password = forms.CharField(widget = forms.PasswordInput(attrs={'tabindex':'1'}),
                            help_text = "Please enter a password.")

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        exclude = []
        
class TeacherForm(forms.ModelForm):
    firstname = forms.CharField(max_length=128,
                                help_text="Please enter your first name.",
                                widget = forms.TextInput(attrs={'tabindex':'1'}))
    surname = forms.CharField(max_length=128,
                                help_text="Please enter your surname.",
                                widget = forms.TextInput(attrs={'tabindex':'1'}))
    school = forms.ModelChoiceField(queryset=School.objects.all().order_by('name'),
                                    required=False,
                                    help_text="Please select your school.",
                                    widget = forms.SelectMultiple(attrs={'tabindex':'1'})
                                    )
    hubs = forms.ModelMultipleChoiceField(queryset=Hub.objects.all().order_by('name'),
                                            required=False,
                                            help_text="Please select your hubs.",
                                            widget = forms.SelectMultiple(attrs={'tabindex':'1'}))
                                                
    class Meta:
        model = Teacher
        fields = ('firstname', 'surname', 'school', 'hubs')
        exclude = []

class SchoolForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                            help_text="Please enter the name of the school.",
                            widget = forms.TextInput(attrs={'tabindex':'1'}))
    town = forms.CharField(max_length=128,
                            help_text="Please enter the town the school is in.",
                            widget = forms.TextInput(attrs={'tabindex':'1'}))
    address = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                                help_text="Please enter the address of the school.")
    latitude = forms.FloatField(help_text="Please enter the latitude of the school.",
                                widget = forms.TextInput(attrs={'tabindex':'1'}))
    longitude = forms.FloatField(help_text="Please enter the longitude of the school.",
                                widget = forms.TextInput(attrs={'tabindex':'1'}))

    class Meta:
        model = School
        fields = ('name', 'town', 'address', 'latitude', 'longitude')
        exclude = []
        
class HubForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                            help_text="Please enter the name of the hub.",
                            widget = forms.TextInput(attrs={'tabindex':'1'}))
    address = forms.CharField( help_text="Please enter the address of the hub.",
                                widget = forms.Textarea(attrs={'tabindex':'1'}))
    latitude = forms.FloatField(help_text="Please enter the latitude of the hub.",
                                widget = forms.TextInput(attrs={'tabindex':'1'}))
    longitude = forms.FloatField(help_text="Please enter the longitude of the hub.",
                                widget = forms.TextInput(attrs={'tabindex':'1'}))

    class Meta:
        model = Hub
        fields = ('name', 'address', 'latitude', 'longitude')
        exclude = []
        
class SearchForm(forms.Form):
    
    #define types of search
    SEARCHTYPES = (
        ('0', 'Resources'),
        ('1', 'Packs'),
        
    )
    
    searchtype = forms.ChoiceField(choices=SEARCHTYPES,
                                required=True,
                                label='Resource',
                                help_text="What do you want to search for.",
                                widget = forms.Select(attrs={'tabindex':'1'}))
    
    # tag forms
    level_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=0).order_by('name'),
                                                required=False,
                                                help_text="Select levels.",
                                                widget = forms.SelectMultiple(attrs={'tabindex':'1'}))
    topic_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=False,
                                                help_text="Select topics.",
                                                widget = forms.SelectMultiple(attrs={'tabindex':'1'}))
    other_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False,
                                                help_text="Select other tags.",
                                                widget = forms.SelectMultiple(attrs={'tabindex':'1'}))
                                                
class TagForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                            help_text="Please enter the new tag.",
                            widget = forms.TextInput(attrs={'tabindex':'1'}))
    type = forms.CharField(widget = forms.HiddenInput(), required=False)               
    
    class Meta:
        model = Tag
        fields = ('name','type')
        exclude = []
        
class PackForm(forms.ModelForm):
    explore = forms.CharField(widget = forms.HiddenInput(), required=False)

    name = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                            max_length=128,
                            help_text="Please enter the resource name.")
    
    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                        max_length=128,
                        help_text="Please enter a short description.")
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="Please enter the full description.",
                            required=False)
                            
    user = forms.CharField(widget = forms.HiddenInput(), required=False) 
    
    # should the resource be shown (basically deleted if not)
    hidden = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    # is this resource restricted to scottish teachers
    restricted = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=0).order_by('name'),
                                                required=False, help_text="Select level(s).")
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=False, help_text="Select topic(s).")
    other_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False, help_text="Select other tags.")
                                                
    class Meta:
        model = Pack
        fields = ('explore', 'name', 'image', 'summary', 'description', 'hidden', 'restricted')
        exclude = []
        
class EditResourceForm(forms.ModelForm):
    
    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                        max_length=128,
                        help_text="Please enter a short description.")
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="Please enter the full description.",
                            required=False)
    
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=0).order_by('name'),
                                                required=True, help_text="Please select level(s).")
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=True, help_text="Please select topic(s).")
    other_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False, help_text="Please select other tags (optional).")                                                

                                                
class EditPackForm(forms.ModelForm):

    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                        max_length=128,
                        help_text="Please enter a short description.")
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="Please enter the full description.",
                            required=False)
    
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=0).order_by('name'),
                                                required=False, help_text="Please select level(s).")
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=False, help_text="Please select topic(s).")
    other_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False, help_text="Please select other tags (optional).")
