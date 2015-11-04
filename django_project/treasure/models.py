from django.db import models

''' start of user models '''

# model for the users / teachers
class Teacher(models.Model):
    username = models.CharField(max_length=128, unique=True)
    firstname = models.CharField(max_length=128)
    surname = models.CharField(max_length=128)
	
    def __unicode__(self):
        return self.username
        
# model for schools
class School(models.Model):
    schoolname = models.CharField(max_length=128)
    #lat long?
    location = models.CharField(max_length=128)
    address = models.CharField(max_length=128)

    def __unicode__(self):
        return self.schoolname

# relationship between teachers and schools
class TeacherSchool(models.Model):
    teacher = models.ForeignKey(Teacher)
    school = models.ForeignKey(School)

    def __unicode__(self):
        return self.teacher.username, self.school.schoolname        

# model for hubs        
class Hub(models.Model):
    hubname = models.CharField(max_length=128)
    #lat long?
    location = models.CharField(max_length=128)
    address = models.CharField(max_length=128)

    def __unicode__(self):
        return self.hubname
        
# relationship between teachers and hubs
class TeacherHub(models.Model):
    teacher = models.ForeignKey(Teacher)
    hub = models.ForeignKey(Hub)

    def __unicode__(self):
        return self.teacher.username, self.hub.hubname

'''  end of user models '''

''' start of material models '''

class Resource(models.Model):
    resourcename = models.CharField(max_length=128)
    # comma separated tree for viewing evolution
    tree = models.CharField(max_length=128)
    author = models.ForeignKey(Teacher)
    
    def __unicode__(self):
        return self.resourcename
        
# resource extensions go here
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
    tagname = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.tagname
    
class ResourceTag(models.Model):
    resource = models.ForeignKey(Resource)
    tag = models.ForeignKey(Tag)

    def __unicode__(self):
        return self.resource.resourceusername, self.tag.tagname   
    
''' end of material models '''

''' start of material relationship models '''

# enter teacher to resource reltionships here

''' end of material realtionship models '''     