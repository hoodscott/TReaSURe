from django.db import models
from django.contrib.auth.models import User

''' start of user models '''

# model for the users / teachers
class Teacher(models.Model):
    # Links Teacher to a User model instance.
    user = models.OneToOneField(User)
    
    firstname = models.CharField(max_length=128)
    surname = models.CharField(max_length=128)
	
    def __unicode__(self):
        return self.user.username
        
# model for schools
class School(models.Model):
    schoolname = models.CharField(max_length=128)
    location = models.CharField(max_length=128) #lat long?
    address = models.CharField(max_length=128)

    def __unicode__(self):
        return self.schoolname

# relationship between teachers and schools
class TeacherSchool(models.Model):
	# //todo foreignkeys
    #teacher = models.ForeignKey(Teacher)
    #school = models.ForeignKey(School)

    def __unicode__(self):
        return self.teacher.user.username, self.school.schoolname        

# model for hubs        
class Hub(models.Model):
    hubname = models.CharField(max_length=128)
    location = models.CharField(max_length=128) #lat long?
    address = models.CharField(max_length=128)

    def __unicode__(self):
        return self.hubname
        
# relationship between teachers and hubs
class TeacherHub(models.Model):
	# //todo foreignkeys
    #teacher = models.ForeignKey(Teacher)
    #hub = models.ForeignKey(Hub)

    def __unicode__(self):
        return self.teacher.user.username, self.hub.hubname

'''  end of user models '''

''' start of material models '''

class Resource(models.Model):
    resourcename = models.CharField(max_length=128)
    description = models.TextField()
    
    # //todo comma separated tree for viewing evolution
    #trees = models.CharField(max_length=128)
    
	# //todo foreignkeys
    #author = models.ForeignKey(Teacher)
    
    def __unicode__(self):
        return self.resourcename
        
        
class FilesResource(models.Model):
    # one to one relationship
    resource = models.OneToOneField(Resource)

    path = models.CharField(max_length=128)

    def __unicode__(self):
        return self.resource.resourcename
        
class WebResource(models.Model):
    # one to one relationship
    resource = models.OneToOneField(Resource)

    url = models.URLField()

    def __unicode__(self):
        return self.resource.resourcename
    
class Tag(models.Model):
	# //todo implement tags
    #tagname = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.tagname
    
class ResourceTag(models.Model):
	# //todo foreignkeys
    #resource = models.ForeignKey(Resource)
    #tag = models.ForeignKey(Tag)

    def __unicode__(self):
        return self.resource.resourcname, self.tag.tagname   
    
''' end of material models '''

''' start of material relationship models '''

# //todo enter teacher to resource reltionships here

''' end of material realtionship models '''     
