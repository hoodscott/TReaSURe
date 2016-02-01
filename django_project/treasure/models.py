from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from geoposition.fields import GeopositionField

''' start of user models '''


class POI(models.Model):
    name = models.CharField(max_length=100)
    position = GeopositionField()

# model for schools
class School(models.Model):
    name = models.CharField(max_length=128)
    town = models.CharField(max_length=128)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __unicode__(self):
        return self.name       

# model for hubs        
class Hub(models.Model):
    name = models.CharField(max_length=128)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __unicode__(self):
        return self.name
        
# model for the users / teachers
class Teacher(models.Model):
    # Links Teacher to a User model instance.
    user = models.OneToOneField(User)
    
    firstname = models.CharField(max_length=128)
    surname = models.CharField(max_length=128)
    
    # creates a foreign key relationship with school
    school = models.ForeignKey(School, null=True)
    # creates a many to many relationship with hubs
    hubs = models.ManyToManyField(Hub, null=True)
	
    def __unicode__(self):
        return "%s %s" % (self.firstname, self.surname)

'''  end of user models '''

''' start of material models '''

# model for tags of resources and packs    
class Tag(models.Model):
    name = models.CharField(max_length=128)
    
    #define types of tags
    TAGTYPES = (
        ('0', 'level'),
        ('1', 'topic'),
        ('2', 'other'),
    )
    type = models.CharField(max_length=1, choices=TAGTYPES)
    
    def __unicode__(self):
        return self.name

# model for a pack of resources
class Pack(models.Model):
    explore  = models.IntegerField(max_length=1)
    name = models.CharField(max_length=128)
    image = models.CharField(max_length=128)

    # creates foreign key to teacher
    author = models.ForeignKey(Teacher)

    # pack description
    description = models.TextField()
    
    # short summary
    summary = models.CharField(max_length=128)
    
    # should the resource be shown (basically deleted if not)
    hidden = models.IntegerField()
    
    # is this resource restricted to scottish teachers
    restricted = models.IntegerField()

    # creates a many to many relationship with tags
    tags = models.ManyToManyField(Tag, null=True)

    class Meta:
        db_table = 'treasure_pack'

    def __unicode__(self):
        return self.name

# model for super/parent resource table
class Resource(models.Model):
    name = models.CharField(max_length=128)
    
    # comma separated field for easier tree searching
    tree = models.TextField(null=True)
  
    # creates foreign key to teacher
    author = models.ForeignKey(Teacher)
    
    # creates a many to many relationship with tags
    tags = models.ManyToManyField(Tag, null=True)
    packs = models.ManyToManyField(Pack, null=True, blank=True)
    
    # long description
    description = models.TextField()
    
    # short description
    summary = models.CharField(max_length=128)
    
    # stores the form of evolution (creation, amendment, etc.)
    evolution_type = models.CharField(max_length=128)
    
    # stores the reasoning for making an evolution
    evolution_explanation = models.TextField()
    
    # should the resource be shown (basically deleted if not)
    hidden = models.IntegerField()
    
    # is this resource restricted to scottish teachers
    restricted = models.IntegerField()
    
    # what type of resource is this (file, web, something else?)
    resource_type = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.name
        
# model for subclass of resource for files        
class FilesResource(models.Model):
    # one to one relationship with abstract resource
    resource = models.OneToOneField(Resource)
    # path to resource
    path = models.FileField(upload_to='resources/%Y/%m/%d')

    def __unicode__(self):
        return self.resource.name

# model for subclass of resource for web pages   
class WebResource(models.Model):
    # one to one relationship with abstract resource
    resource = models.OneToOneField(Resource)
    # url of web resource
    url = models.URLField()

    def __unicode__(self):
        return self.resource.name
        
'''
ADD NEW RESOURCES HERE
class TemplateResource(models.Model):
    # one to one relationship with abstract resource
    resource = models.OneToOneField(Resource)

    # your resource properties go here 

    def __unicode__(self):
        return self.resource.name
''' 

        
''' end of material models '''

''' start of material relationship models '''

# model to store whether users downloaded a resource        
class TeacherDownloadsResource(models.Model):
    teacher = models.ForeignKey(Teacher)
    resource = models.ForeignKey(Resource)
    # used or not
    used = models.IntegerField()
    datetime = models.DateTimeField()
    # lat and long of where it was used
    latitude = models.FloatField()
    longitude = models.FloatField()
    # rated or not
    rated = models.IntegerField()
    
    def __unicode__(self):
        return "%s %s" % (self.teacher.name, self.resource.name)
        
# model to store a users rating of a resource        
class TeacherRatesResource(models.Model):
    id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(Teacher)
    resource = models.ForeignKey(Resource)
    # rating measures
    measure1 = models.CharField(max_length=128)
    measure2 = models.CharField(max_length=128)
    measure3 = models.CharField(max_length=128)
    # comment box
    comment = models.TextField()
    
    def __unicode__(self):
        return "%s %s" % (self.teacher, self.resource.name)
        
# model to indicate if users want to talk about a resource        
class TeacherWantstoTalkResource(models.Model):
    teacher = models.ForeignKey(Teacher)
    resource = models.ForeignKey(Resource)
    # comment box
    comment = models.TextField()
    # lat and long of where it was used
    latitude = models.FloatField()
    longitude = models.FloatField()
    datetime = models.DateTimeField()
    disable = models.IntegerField()
    def __unicode__(self):
        return "%s %s" % (self.teacher.name, self.resource.name)
     
''' end of material relationship models '''    

''' start of discussion relationship models '''

''' Don't know what this is
# model to disucssions of a resource        
class TeacherRatesResource(models.Model):
    owner = models.ForeignKey(Teacher)
    resource = models.ForeignKey(Resource)
    # many to many field for all teachers who participate in this discussion
    attendees = models.ManyToManyField(Teacher)
    # foreign key if discussion was at a hub (can be null if not at a hub)
    hub = models.ForeignKey(Hub, null=True)
    # if discussion was offline or online
    physical = models.BooleanField()
    # location of discussion
    location = models.CharField(max_length=128)
    # time of discussion
    time = models.DateTimeField()
    
    def __unicode__(self):
        return "%s %s" % (self.teacher.name, self.resource.name)
'''

''' end of discussion relationship models '''

# postcode Models        
class ScotlandPostcodes(models.Model):
    Postcode = models.TextField(primary_key=True)
    Latitude = models.FloatField()
    Longitude = models.FloatField()
    
    def __unicode__(self):
        return "%s" % (self.Postcode)
# postcode Models        
class EnglandPostcodes(models.Model):
    Postcode = models.TextField(primary_key=True)
    Latitude = models.FloatField()
    Longitude = models.FloatField()
    
    def __unicode__(self):
        return "%s" % (self.Postcode)
# postcode Models        
class WalesPostcodes(models.Model):
    Postcode = models.TextField(primary_key=True)
    Latitude = models.FloatField()
    Longitude = models.FloatField()
    
    def __unicode__(self):
        return "%s" % (self.Postcode)

# postcode Models        
class NorthernIrelandPostcodes(models.Model):
    Postcode = models.TextField(primary_key=True)
    Latitude = models.FloatField()
    Longitude = models.FloatField()
    
    def __unicode__(self):
        return "%s" % (self.Postcode)
