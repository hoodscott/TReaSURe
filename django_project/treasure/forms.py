from django import forms
from treasure.models import *
from django.contrib.auth.models import User
from treasure.widgets import *
from django.utils.safestring import mark_safe
from captcha.fields import CaptchaField

#define values for hidden
HIDDEN = (
    ('0', 'Visible'),
    ('1', 'Hidden'),
)

# define values for restriction
RESTRICTED = (
    ('0', 'Public'),
    ('1', 'Scottish Teachers Only'),
)

# define types for evolutions
EVOLUTIONS = (
    ('1', 'Amendments'),
    ('2', 'Style'),
    ('3', 'Translation'),
    ('4', 'Recontext'),
    ('5', 'New Difficulty'),
    ('6', 'New Format')
)

countries= (("Scotland", "Scotland"),
        ("England", "England"),("NorthernIreland", "NorthernIreland"),
        ("Wales", "Wales"))

rating= (('5','5'),('4','4'),('3','3'),('2','2'),('1','1'))

class RatingForm(forms.Form):
    teacher = forms.CharField(widget = forms.HiddenInput(), required=False)
    resource = forms.CharField(widget = forms.HiddenInput(), required=False)
    measure1 = forms.ChoiceField(label='Engagement',help_text="How engaging was the material for the class?", choices=rating)
    measure2 = forms.ChoiceField(label='Effectiveness',help_text="How effective was it? Did it achieve attainment of learning outcomes? Did students enjoy it? ", choices=rating)
    measure3 = forms.ChoiceField(label='Ease of use',help_text="How easy was it to prepare the materials and use it in the classroom?", choices=rating)
    comment = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
                            max_length=128,
                            help_text="Feedback for the resource",
                            label='Feedback/Comment*')
    captcha= CaptchaField(label='Captcha', help_text= 'Are we human, or are we dancers?')

class PackRatingForm(forms.Form):
    teacher = forms.CharField(widget = forms.HiddenInput(), required=False)
    resource = forms.CharField(widget = forms.HiddenInput(), required=False)
    measure1 = forms.ChoiceField(label='Measure1',help_text="Measure1 Description", choices=rating)
    measure2 = forms.ChoiceField(label='Measure2',help_text="Measure2 Description", choices=rating)
    measure3 = forms.ChoiceField(label='Measure3',help_text="Measure3 Description", choices=rating)
    comment = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
                            max_length=128,
                            help_text="Feedback for the resource",
                            label='Feedback/Comment*')
    captcha= CaptchaField(label='Captcha', help_text= 'Are we human, or are we dancers?')


class ResourceForm(forms.ModelForm):
        
    name = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
                            max_length=128,
                            help_text="The resource name.",
                            label='Name*')
    
    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                        max_length=128,
                        label='Summary*',
                        help_text="A short description. This will appear in resource lists.")
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="The full description of the Resource. This will appear when viewing that resource.",
                            required=False,
                            label='Description')
                            
    tree = forms.CharField(widget = forms.HiddenInput(), required=False)
    user = forms.CharField(widget = forms.HiddenInput(), required=False)
    
    evolution_type = forms.CharField(widget = forms.HiddenInput(), required=False)
    evolution_explanation = forms.CharField(widget = forms.HiddenInput(), required=False)
    
    # should the resource be shown (basically deleted if not)
    hidden = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    # is this resource restricted to scottish teachers
    restricted = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    # what type of resource is this (file, web, something else?)
    resource_type = forms.CharField(widget = forms.HiddenInput(), required=False)
    
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(tagtype=0).order_by('name'),
                                                required=True,
                                                label='Level Tags*',
                                                help_text="Tags that describe the Level that this material concerns")
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(tagtype=1).order_by('name'),
                                                required=True,
                                                label='Topic Tags*',
                                                help_text="Tags that describe the Topic that this material covers")
    other_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(tagtype=2).order_by('name'),
                                                required=False,
                                                label='Other Tags',
                                                help_text="Any other tags not falling under the Level and Topic categories (optional)")
              
    def __init__(self,tags,*args,**kwargs):
        self.tag_ids = tags
        super(ResourceForm, self).__init__(*args,**kwargs)
        
        # set initial selected tags
        self.fields['level_tags'].initial = tags['level']
        self.fields['topic_tags'].initial = tags['topic']
        self.fields['other_tags'].initial = tags['other']

    
    class Meta:
        model = Resource
        fields = ('evolution_type', 'evolution_explanation', 'name', 'summary', 'description', 'tree', 'user', 'hidden', 'restricted', 'resource_type')
        exclude = []

# extends the resource form for verified teachers to allow them to hide their work from non verified users
class VerifiedResourceForm(ResourceForm):
    restricted = forms.ChoiceField(choices=RESTRICTED,
                        required=True,
                        label='Restricted*',
                        help_text="Should this be viewable by anyone or just scottish teachers?",
                        widget = forms.Select(attrs={'tabindex':'1'}))

# extends the resource form to add the evolution types
class EvolveResourceForm(ResourceForm):
    # stores the form of evolution (creation, amendment, etc.)
    evolution_type = forms.ChoiceField(widget=forms.Select(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
                            choices=EVOLUTIONS,
                            required=True,
                            label='Evolution Type*',
                            help_text="What is the evolution type?")
    
    evolution_explanation = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="In what way have you \"evolved\" this resource?",
                            required=False,
                            label='Explanation of Evolution')
                            
    name = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                            max_length=128,
                            help_text="The resource name.",
                            label='Name*')
                            
# extends the evolve form for verified teachers to allow them to hide their work from non verified users
class VerifiedEvolveResourceForm(EvolveResourceForm):
    restricted = forms.ChoiceField(choices=RESTRICTED,
                        required=True,
                        label='Restricted*',
                        help_text="Should this be viewable by anyone or just scottish teachers?",
                        widget = forms.Select(attrs={'tabindex':'1'}))

        
class FileForm(forms.ModelForm):
    path = forms.FileField(widget = forms.ClearableFileInput(attrs={'tabindex':'1'}),
                            label='Select the resource to upload*',
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
                                label='Username*')
    email = forms.CharField(widget = DisableAutoInput(attrs={'tabindex':'1'}),
                            help_text = "The email address",
                            label='E-mail*')
    password = forms.CharField(widget = forms.PasswordInput(attrs={'tabindex':'1'}),
                            help_text = "The account password.",
                            label='Password*')
    captcha= CaptchaField(label='Captcha', help_text= 'Are we human, or are we dancers?')

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        exclude = []
        
class UserFormNoPW(forms.ModelForm):
    username = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
                                help_text="The account username",
                                label='Username*')
    email = forms.CharField(widget = DisableAutoInput(attrs={'tabindex':'1'}),
                            help_text = "The email address",
                            label='E-mail*')

    password = forms.CharField(widget = forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        exclude = []
        
class TeacherForm(forms.ModelForm):
    firstname = forms.CharField(max_length=128,
                                help_text="Your first name",
                                label='First Name*',
                                widget = forms.TextInput(attrs={'tabindex':'1'}))
    surname = forms.CharField(max_length=128,
                                help_text="Your last name",
                                label='Last Name*',
                                widget = forms.TextInput(attrs={'tabindex':'1'}))
    school = forms.ModelChoiceField(queryset=School.objects.all().order_by('name'),
                                    required=False,
                                    label='School',
                                    help_text="The school you work for",
                                    widget = forms.Select(attrs={'tabindex':'1'}))

    hubs = forms.ModelMultipleChoiceField(queryset=Hub.objects.all().order_by('name'),
                                            required=False,
                                            label='Hubs',
                                            help_text="The teaching hubs that you are member of (eg. Plan C)",
                                            widget = forms.SelectMultiple(attrs={'tabindex':'1'}))

    scottishTeacher= forms.BooleanField(widget=forms.CheckboxInput(attrs={'tabindex':'1'}),
                                            help_text="Are you a registered teacher in Scotland?",
                                            required=False,
                                            label="Registered Scottish Teacher?")

    def __init__(self,*args,**kwargs):
        super(TeacherForm, self).__init__(*args,**kwargs)

        self.fields['school'].queryset=School.objects.all().order_by('name')
        

        self.fields['hubs'].queryset=Hub.objects.all().order_by('name')
        
    class Meta:
        model = Teacher
        fields = ('firstname', 'surname', 'school', 'hubs')
        exclude = []

class SchoolForm(forms.Form):

    name = forms.CharField(max_length=128,
                            help_text="The name of the school",
                            label='Name*',
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
                                label='Postcode*',
                                widget = forms.TextInput(attrs={'tabindex':'1'}))
        
class HubForm(forms.Form):
    name = forms.CharField(max_length=128,
                            help_text="The name of the hub.",
                            label='Name*',
                            widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}))

    country = forms.ChoiceField(label='Country',help_text="The Country the Hub is in", choices=countries)
    address = forms.CharField( label='Address',help_text="The address of the hub",
                                widget = forms.Textarea(attrs={'tabindex':'1'}))
    postcode = forms.CharField(help_text="The Postcode of the Hub",
                                label='Postcode*',
                                widget = forms.TextInput(attrs={'tabindex':'1'}))
        
class SearchForm(forms.Form):
    
    # tag forms
    level_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(tagtype=0).order_by('name'),
                                                required=False,
                                                label='Level Tags',
                                                help_text="Tags that describe the Level that this material concerns",
                                                widget = forms.SelectMultiple(attrs={'tabindex':'1'}))
    topic_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(tagtype=1).order_by('name'),
                                                required=False,
                                                help_text="Tags that describe the Topic that his material covers",
                                                widget = forms.SelectMultiple(attrs={'tabindex':'1'}))
    other_tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(tagtype=2).order_by('name'),
                                                required=False,
                                                help_text="Any other tags not falling into Level or Topic category (optional)",
                                                widget = forms.SelectMultiple(attrs={'tabindex':'1'}))
                                                
class TagForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                            help_text="The name of the new tag (Should be Descriptive)",
                            label='Name*',
                            widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}))
    tagtype = forms.CharField(widget = forms.HiddenInput(), required=False)
    
    class Meta:
        model = Tag
        fields = ('name','tagtype')
        exclude = []
        
class PackForm(forms.ModelForm):
    explore = forms.CharField(widget = forms.HiddenInput(), required=False)

    name = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}),
                            max_length=128,
                            help_text="The name of the pack",
                            label='Name*')
    
    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                        max_length=128,
                        help_text="A short description for the pack. This will appear in pack lists.",
                        label='Summary*')
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="The full description of the pack. This will appear when viewing a pack.",
                            required=False,
                            label='Description')
                            
    user = forms.CharField(widget = forms.HiddenInput(), required=False)
    
    image = forms.ImageField(widget = forms.FileInput(attrs={'tabindex':'1'}),
                            label="Upload Image",
                            required=False,
                            help_text='Select the resource to upload: Maximum of 42MB')
    
    # should the pack be shown (basically deleted if not)
    hidden = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    # is this pack restricted to scottish teachers
    restricted = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(tagtype=0).order_by('name'),
                                                required=False, help_text="Tags that describe the Level that this material concerns",
                                                label='Level Tags')
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(tagtype=1).order_by('name'),
                                                required=False, help_text="Tags that describe the Topic that his material covers",
                                                label='Topic Tags')
    other_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(tagtype=2).order_by('name'),
                                                required=False,
                                                help_text="Any other tags not falling into Level or Topic category (optional)",
                                                label='Other Tags')
              
    def __init__(self,tags,*args,**kwargs):
        self.tag_ids = tags
        super(PackForm, self).__init__(*args,**kwargs)
        # set initial selected tags
        self.fields['level_tags'].initial = tags['level']
        self.fields['topic_tags'].initial = tags['topic']
        self.fields['other_tags'].initial = tags['other']
    
    class Meta:
        model = Pack
        fields = ('explore', 'name', 'summary', 'description', 'image', 'hidden', 'restricted')
        exclude = []

# extends the pack form for verified teachers to allow them to hide their work from non verified users
class VerifiedPackForm(PackForm):
    restricted = forms.ChoiceField(choices=RESTRICTED,
                        required=True,
                        label='Restricted*',
                        help_text="Should this be viewable by anyone or just scottish teachers?",
                        widget = forms.Select(attrs={'tabindex':'1'}))
        
class EditResourceForm(forms.ModelForm):
    
    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                        max_length=128,
                        label='Summary*',
                        help_text="A short description. This will appear in resource lists.")
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="The full description of the Resource. This will appear when viewing that resource.",
                            required=False,
                            label='Description')
                            
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(tagtype=0).order_by('name'),
                                                required=True,
                                                label='Level Tags*',
                                                help_text="Tags that describe the Level that this material concerns")
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(tagtype=1).order_by('name'),
                                                required=True,
                                                label='Topic Tags*',
                                                help_text="Tags that describe the Topic that this material covers")
    other_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(tagtype=2).order_by('name'),
                                                required=False,
                                                label='Other Tags',
                                                help_text="Any other tags not falling under the Level and Topic categories (optional)")

    hidden = forms.ChoiceField(choices=HIDDEN,
                                required=True,
                                label='Visible*',
                                help_text="Should this be visible or hidden?",
                                widget = forms.Select(attrs={'tabindex':'1'}))
    
    restricted = forms.IntegerField(widget = forms.HiddenInput(), required=False)
                            
    def __init__(self,tags,*args,**kwargs):
        self.tag_ids = tags
        super(EditResourceForm, self).__init__(*args,**kwargs)
        
        # set initial selected tags
        self.fields['level_tags'].initial = tags['level']
        self.fields['topic_tags'].initial = tags['topic']
        self.fields['other_tags'].initial = tags['other']
        
    class Meta:
        model = Resource
        fields = ('name', 'summary', 'description', 'hidden', 'restricted')
        exclude = []
        
# extends the edit resource form for verified teachers to allow them to hide their work from non verified users
class VerifiedEditResourceForm(EditResourceForm):
    restricted = forms.ChoiceField(choices=RESTRICTED,
                        required=True,
                        label='Restricted*',
                        help_text="Should this be viewable by anyone or just scottish teachers?",
                        widget = forms.Select(attrs={'tabindex':'1'}))
    
                                                
class EditPackForm(forms.ModelForm):

    summary = forms.CharField(widget = forms.TextInput(attrs={'tabindex':'1'}),
                        max_length=128,
                        help_text="A short description for the pack. This will appear in pack lists.",
                        label='Summary')
    
    description = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="The full description of the pack. This will appear when viewing a pack.",
                            required=False,
                            label='Description')
    
    image = forms.ImageField(widget = forms.ClearableFileInput(attrs={'tabindex':'1'}),
                            label="Upload Image",
                            required=False,
                            help_text='Select the resource to upload: Maximum of 42MB')
    
    level_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(tagtype=0).order_by('name'),
                                                required=False, help_text="Tags that describe the Level that this material concerns",
                                                label='Level Tags')
    topic_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(tagtype=1).order_by('name'),
                                                required=False, help_text="Tags that describe the Topic that his material covers",
                                                label='Topic Tags')
    other_tags = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'tabindex':'1'}),
                                                queryset=Tag.objects.filter(tagtype=2).order_by('name'),
                                                required=False,
                                                help_text="Any other tags not falling into Level or Topic category (optional)",
                                                label='Other Tags')

    hidden = forms.ChoiceField(choices=HIDDEN,
                                required=True,
                                label='Visible*',
                                help_text="Should this be visible or hidden?",
                                widget = forms.Select(attrs={'tabindex':'1'}))
                                
    restricted = forms.IntegerField(widget = forms.HiddenInput(), required=False)
                            
    def __init__(self,tags,*args,**kwargs):
        self.tag_ids = tags
        super(EditPackForm, self).__init__(*args,**kwargs)
        
        # set initial selected tags
        self.fields['level_tags'].initial = tags['level']
        self.fields['topic_tags'].initial = tags['topic']
        self.fields['other_tags'].initial = tags['other']
        
    class Meta:
        model = Pack
        fields = ('summary', 'description', 'image', 'hidden', 'restricted')
        exclude = []
        
# extends the edit resource form for verified teachers to allow them to hide their work from non verified users
class VerifiedEditPackForm(EditPackForm):
    restricted = forms.ChoiceField(choices=RESTRICTED,
                        required=True,
                        label='Restricted*',
                        help_text="Should this be viewable by anyone or just scottish teachers?",
                        widget = forms.Select(attrs={'tabindex':'1'}))
        
class PostThreadForm(forms.ModelForm):
    
    title = forms.CharField(max_length=128,
                                help_text="The title of the thread.",
                                label='Thread Title*',
                                widget = forms.TextInput(attrs={'tabindex':'1', 'autofocus':'autofocus'}))
                                
    content = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="The body content of the thread.",
                            required=True,
                            label='Thread Body*')
                            
    TYPE = (
        ('1', 'Question'),
        ('2', 'Discussion'),
    )
    threadtype = forms.ChoiceField(widget=forms.Select(attrs={'tabindex':'1'}),
                            choices=TYPE,
                            required=True,
                            label='Thread Type*',
                            help_text="Is this a question or the start of a discussion?")
    
    board = forms.CharField(widget = forms.HiddenInput(), required=False)
    datetime = forms.CharField(widget = forms.HiddenInput(), required=False)
    author = forms.CharField(widget = forms.HiddenInput(), required=False)
    rating = forms.CharField(widget = forms.HiddenInput(), required=False)
    user = forms.CharField(widget = forms.HiddenInput(), required=False)
    
    restricted = forms.IntegerField(widget = forms.HiddenInput(), required=False)
    
    class Meta:
        model = Thread
        fields = ('title', 'content', 'threadtype', 'restricted')
        exclude = []
        
# extends the post thread form for verified teachers to allow them to hide their work from non verified users
class VerifiedPostThreadForm(PostThreadForm):
    restricted = forms.ChoiceField(choices=RESTRICTED,
                        required=True,
                        label='Restricted*',
                        help_text="Should this be viewable by anyone or just scottish teachers?",
                        widget = forms.Select(attrs={'tabindex':'1'}))
        
class PostPostForm(forms.ModelForm):
    
        # basic information about post
    thread = forms.CharField(widget = forms.HiddenInput(), required=False)
    datetime = forms.CharField(widget = forms.HiddenInput(), required=False)
    author = forms.CharField(widget = forms.HiddenInput(), required=False)
    
    # content of thread
    content = forms.CharField(widget = forms.Textarea(attrs={'tabindex':'1'}),
                            help_text="The content you wish to post.",
                            required=True,
                            label='Add to the Discussion:')
                            
    class Meta:
        model = Post
        fields=('content',)
        exclude = []
