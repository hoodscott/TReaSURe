from django import forms
from treasure.models import *
from django.contrib.auth.models import User
from treasure.widgets import *
from django.utils.safestring import mark_safe

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
countries= (("Scotland", "Scotland"),
        ("England", "England"),("NorthernIreland", "NorthernIreland"),
        ("Wales", "Wales"))

rating= (('5','5'),('4','4'),('3','3'),('2','2'),('1','1'))

class RatingForm(forms.Form):
    teacher = forms.CharField(widget = forms.HiddenInput(), required=False)
    resource = forms.CharField(widget = forms.HiddenInput(), required=False)
    measure1 = forms.ChoiceField(label='Measure1',help_text="Measure 1 Description", choices=rating)
    measure2 = forms.ChoiceField(label='Measure1',help_text="Measure 1 Description", choices=rating)
    measure3 = forms.ChoiceField(label='Measure1',help_text="Measure 1 Description", choices=rating)
    comment = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
                            max_length=128,
                            help_text="Feedback for the resource",
                            label='Feedback/Comment')


class ResourceForm(forms.ModelForm):
        
    name = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
                            max_length=128,
                            help_text="The resource name.",
                            label='Name')
    
    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                        max_length=128,
                        label='Summary',
                        help_text="A short description. This will appear in resource lists.")
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="The full description of the Resource. This will appear when viewing that resource.",
                            required=False,
                            label='Description')
                            
    tree = forms.CharField(widget = forms.HiddenInput(), required=False)
    user = forms.CharField(widget = forms.HiddenInput(), required=False) 

    # stores the form of evolution (creation, amendment, etc.)
    evolution_type = forms.CharField(widget = forms.HiddenInput(), required=False)
    
    # should the resource be shown (basically deleted if not)
    hidden = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    # is this resource restricted to scottish teachers
    restricted = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    # what type of resource is this (file, web, something else?)
    resource_type = forms.CharField(widget = forms.HiddenInput(), required=False)
    
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=0).order_by('name'),
                                                required=True,
                                                label='Level Tags',
                                                help_text="Tags that describe the Level that this material concerns")
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=True,
                                                label='Topic Tags',
                                                help_text="Tags that describe the Topic that this material covers")
    other_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False,
                                                label='Other Tags',
                                                help_text="Any other tags not falling under the Level and Topic categories (optional)")
              
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
                            help_text='Select the resource to upload: Maximum of 42MB')
    
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
                                help_text="The account username",
                                label='Username')
    email = forms.CharField(widget = DisableAutoInput(attrs={'tabindex':'1'}),
                            help_text = "The email address",
                            label='E-mail')
    password = forms.CharField(widget = forms.PasswordInput(attrs={'tabindex':'1'}),
                            help_text = "The account password.",
                            label='Password')

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        exclude = []
        
class UserFormNoPW(forms.ModelForm):
    username = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
                                help_text="The account username",
                                label='Username')
    email = forms.CharField(widget = DisableAutoInput(attrs={'tabindex':'1'}),
                            help_text = "The email address",
                            label='E-mail')

    password = forms.CharField(widget = forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        exclude = []
        
class TeacherForm(forms.ModelForm):
    firstname = forms.CharField(max_length=128,
                                help_text="Your first name",
                                label='First Name',
                                widget = forms.TextInput(attrs={'tabindex':'1'}))
    surname = forms.CharField(max_length=128,
                                help_text="Your last name",
                                label='Last Name',
                                widget = forms.TextInput(attrs={'tabindex':'1'}))
    school = forms.ModelChoiceField(queryset=School.objects.all().order_by('name'),
                                    required=False,
                                    label='School',
                                    help_text="The school you work for")                                   
    hubs = forms.ModelMultipleChoiceField(queryset=Hub.objects.all().order_by('name'),
                                            required=False,
                                            label='Hubs',
                                            help_text="The teaching hubs that you are member of (eg. Plan C)")                                                
    def __init__(self,*args,**kwargs):
        super(TeacherForm, self).__init__(*args,**kwargs)
        # wrap the model widget in the wrapper        
        self.fields['school'].widget = CustomRelatedFieldWidgetWrapper(
                                               forms.Select(attrs={'tabindex':'1'}),
                                               '/treasure/add_school/',
                                                True,)
        self.fields['school'].queryset=School.objects.all().order_by('name')
        
        # do the same for hubs
        self.fields['hubs'].widget = CustomRelatedFieldWidgetWrapper(
                                               forms.SelectMultiple(attrs={'tabindex':'1'}),
                                               '/treasure/add_hub/',
                                                True,)
        self.fields['hubs'].queryset=Hub.objects.all().order_by('name')
        
    class Meta:
        model = Teacher
        fields = ('firstname', 'surname', 'school', 'hubs')
        exclude = []

class SchoolForm(forms.Form):

    name = forms.CharField(max_length=128,
                            help_text="The name of the school",
                            label='Name',
                            widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}))
    country = forms.ChoiceField(label='Country',help_text="The Country the School is in", choices=countries)
    town = forms.CharField(max_length=128,
                            help_text="The town the school is in",
                            label='Town',
                            widget = forms.TextInput(attrs={'tabindex':'1'}))
    address = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                                help_text="The address of the school",
                                label='Address (eg. 3 George Street)')
    postcode = forms.CharField(help_text="The Postcode of the school",
                                label='Postcode',
                                widget = forms.TextInput(attrs={'tabindex':'1'}))
        
class HubForm(forms.Form):
    name = forms.CharField(max_length=128,
                            help_text="The name of the hub.",
                            label='Name',
                            widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}))

    country = forms.ChoiceField(label='Country',help_text="The Country the Hub is in", choices=countries)
    address = forms.CharField( label='Address',help_text="The address of the hub",
                                widget = forms.Textarea(attrs={'tabindex':'1'}))
    postcode = forms.CharField(help_text="The Postcode of the Hub",
                                label='Postcode',
                                widget = forms.TextInput(attrs={'tabindex':'1'}))
        
class SearchForm(forms.Form):
    
    searchtype = forms.ChoiceField(choices=SEARCHTYPES,
                                required=True,
                                label='Search for',
                                help_text="What do you want to search for",
                                widget = forms.Select(attrs={'tabindex':'1', 'autofocus':'autofocus'}))
    
    # tag forms
    level_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=0).order_by('name'),
                                                required=False,
                                                label='Level Tags',
                                                help_text="Tags that describe the Level that this material concerns",
                                                widget = forms.SelectMultiple(attrs={'tabindex':'1'}))
    topic_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=False,
                                                help_text="Tags that describe the Topic that his material covers",
                                                widget = forms.SelectMultiple(attrs={'tabindex':'1'}))
    other_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False,
                                                help_text="Any other tags not falling into Level or Topic category (optional)",
                                                widget = forms.SelectMultiple(attrs={'tabindex':'1'}))
                                                
class TagForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                            help_text="The name of the new tag (Should be Descriptive)",
                            label='Name',
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
                            help_text="The name of the pack",
                            label='Name')
    
    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                        max_length=128,
                        help_text="A short description for the pack. This will appear in pack lists.",
                        label='Summary')
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="The full description of the pack. This will appear when viewing a pack.",
                            required=False,
                            label='Description')
                            
    user = forms.CharField(widget = forms.HiddenInput(), required=False)
    
    image = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                            max_length=128,
                            help_text="URL for the Pack's image",
                            label='Image URL')
    
    # should the pack be shown (basically deleted if not)
    hidden = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    # is this pack restricted to scottish teachers
    restricted = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=0).order_by('name'),
                                                required=False, help_text="Tags that describe the Level that this material concerns",
                                                label='Level Tags')
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=False, help_text="Tags that describe the Topic that his material covers",
                                                label='Topic Tags')
    other_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False,
                                                help_text="Any other tags not falling into Level or Topic category (optional)",
                                                label='Other Tags')
              
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
    
    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                        max_length=128,
                        label='Summary',
                        help_text="A short description. This will appear in resource lists.")
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="The full description of the Resource. This will appear when viewing that resource.",
                            required=False,
                            label='Description')
                            
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=0).order_by('name'),
                                                required=True,
                                                label='Level Tags',
                                                help_text="Tags that describe the Level that this material concerns")
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=True,
                                                label='Topic Tags',
                                                help_text="Tags that describe the Topic that this material covers")
    other_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False,
                                                label='Other Tags',
                                                help_text="Any other tags not falling under the Level and Topic categories (optional)")

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

    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                        max_length=128,
                        help_text="A short description for the pack. This will appear in pack lists.",
                        label='Summary')
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="The full description of the pack. This will appear when viewing a pack.",
                            required=False,
                            label='Description')
    
    image = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                            max_length=128,
                            help_text="URL for the Pack's image",
                            label='Image URL')
    
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=0).order_by('name'),
                                                required=False, help_text="Tags that describe the Level that this material concerns",
                                                label='Level Tags')
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(type=1).order_by('name'),
                                                required=False, help_text="Tags that describe the Topic that his material covers",
                                                label='Topic Tags')
    other_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type=2).order_by('name'),
                                                required=False,
                                                help_text="Any other tags not falling into Level or Topic category (optional)",
                                                label='Other Tags')

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
