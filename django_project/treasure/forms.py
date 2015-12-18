from django import forms
from treasure.models import *
from django.contrib.auth.models import User
from treasure.widgets import *

#define values for hidden
HIDDEN = (
    ('0', 'Visible'),
    ('1', 'Hidden'),
)

# define values for restriction
RESTRICTED = (
    ('0', 'Pubic'),
    ('1', 'Scottish Teachers Only'),
)

#define types of search
SEARCHTYPES = (
    ('0', 'Resources'),
    ('1', 'Packs'),
    
) 

class ResourceForm(forms.ModelForm):
        
    name = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
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
                                                required=True,
                                                help_text="Please select level(s).")
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=True,
                                                help_text="Please select topic(s).")
    other_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False,
                                                help_text="Please select other tags (optional)")
              
    def __init__(self,tags,*args,**kwargs):
        self.tag_ids = tags
        super(ResourceForm, self).__init__(*args,**kwargs)

        # wrap the model widget in the wrapper        
        self.fields['other_tags'].widget = CustomRelatedFieldWidgetWrapper(
                                                forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                '/treasure/tags/new/',
                                                True,)
                                                
        self.fields['other_tags'].queryset=Tag.objects.filter(type=2).order_by('name')
        
        # set initial selected tags
        self.fields['level_tags'].initial = tags['level']
        self.fields['topic_tags'].initial = tags['topic']
        self.fields['other_tags'].initial = tags['other']   

    
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
    username = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
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
                                    widget = forms.Select(attrs={'tabindex':'1'})
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
                            widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}))
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
                            widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}))
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
    
    searchtype = forms.ChoiceField(choices=SEARCHTYPES,
                                required=True,
                                label='Resource',
                                help_text="What do you want to search for.",
                                widget = forms.Select(attrs={'tabindex':'1', 'autofocus':'autofocus'}))
    
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
                            widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}))
    type = forms.CharField(widget = forms.HiddenInput(), required=False)               
    
    class Meta:
        model = Tag
        fields = ('name','type')
        exclude = []
        
class PackForm(forms.ModelForm):
    explore = forms.CharField(widget = forms.HiddenInput(), required=False)

    name = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
                            max_length=128,
                            help_text="Please enter the pack name.")
    
    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                        max_length=128,
                        help_text="Please enter a short description.")
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="Please enter the full description.",
                            required=False)
                            
    user = forms.CharField(widget = forms.HiddenInput(), required=False)
    
    image = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                            max_length=128,
                            help_text="Enter image url.")
    
    # should the pack be shown (basically deleted if not)
    hidden = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    # is this pack restricted to scottish teachers
    restricted = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=0).order_by('name'),
                                                required=False, help_text="Select level(s).")
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=False, help_text="Select topic(s).")
    other_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False,
                                                help_text="Please select other tags (optional)")
              
    def __init__(self,tags,*args,**kwargs):
        self.tag_ids = tags
        super(PackForm, self).__init__(*args,**kwargs)

        # wrap the model widget in the wrapper        
        self.fields['other_tags'].widget = CustomRelatedFieldWidgetWrapper(
                                                forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                '/treasure/tags/new/',
                                                True,)
                                                
        self.fields['other_tags'].queryset=Tag.objects.filter(type=2).order_by('name')
        
        # set initial selected tags
        self.fields['level_tags'].initial = tags['level']
        self.fields['topic_tags'].initial = tags['topic']
        self.fields['other_tags'].initial = tags['other']
    
    class Meta:
        model = Pack
        fields = ('explore', 'name', 'summary', 'description', 'image', 'hidden', 'restricted')
        exclude = []
        
class EditResourceForm(forms.ModelForm):
    
    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
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
    other_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False,
                                                help_text="Please select other tags (optional)")
     
    hidden = forms.ChoiceField(choices=HIDDEN,
                                required=True,
                                label='Visible',
                                help_text="Should this be visible or hidden?",
                                widget = forms.Select(attrs={'tabindex':'1'}))
    
    ''' todo: implement restrictions
    visible = forms.ChoiceField(choices=VISIBLE,
                            required=True,
                            label='Visible',
                            help_text="Should this be viewable by anyone or just scottish teachers?",
                            widget = forms.Select(attrs={'tabindex':'1'}))'''
                            
    def __init__(self,tags,*args,**kwargs):
        self.tag_ids = tags
        super(EditResourceForm, self).__init__(*args,**kwargs)
        
        # wrap the model widget in the wrapper        
        self.fields['other_tags'].widget = CustomRelatedFieldWidgetWrapper(
                                                forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                '/treasure/tags/new/',
                                                True,)                                        
        self.fields['other_tags'].queryset=Tag.objects.filter(type=2).order_by('name')
        
        # set initial selected tags
        self.fields['level_tags'].initial = tags['level']
        self.fields['topic_tags'].initial = tags['topic']
        self.fields['other_tags'].initial = tags['other']
    
                                                
class EditPackForm(forms.ModelForm):

    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
                        max_length=128,
                        help_text="Please enter a short description.")
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="Please enter the full description.",
                            required=False)
                            
    image = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                            max_length=128,
                            help_text="Enter image url.")
    
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=0).order_by('name'),
                                                required=False, help_text="Please select level(s).")
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=False, help_text="Please select topic(s).")
    other_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False,
                                                help_text="Please select other tags (optional)")
                                                     
    hidden = forms.ChoiceField(choices=HIDDEN,
                                required=True,
                                label='Visible',
                                help_text="Should this be visible or hidden?",
                                widget = forms.Select(attrs={'tabindex':'1'}))
    
    ''' todo: implement restrictions    
    visible = forms.ChoiceField(choices=VISIBLE,
                            required=True,
                            label='Visible',
                            help_text="Should this be viewable by anyone or just scottish teachers?",
                            widget = forms.Select(attrs={'tabindex':'1'}))'''
                            
    def __init__(self,tags,*args,**kwargs):
        self.tag_ids = tags
        super(EditPackForm, self).__init__(*args,**kwargs)
        
        # wrap the model widget in the wrapper        
        self.fields['other_tags'].widget = CustomRelatedFieldWidgetWrapper(
                                                forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                '/treasure/tags/new/',
                                                True,)
                                                
        self.fields['other_tags'].queryset=Tag.objects.filter(type=2).order_by('name')        
        
        # set initial selected tags
        self.fields['level_tags'].initial = tags['level']
        self.fields['topic_tags'].initial = tags['topic']
        self.fields['other_tags'].initial = tags['other']