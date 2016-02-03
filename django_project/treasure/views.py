from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from treasure.forms import *
from treasure.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core import validators
from string import split, upper
from datetime import datetime
from django.utils.html import escape, escapejs
from django.utils.translation import ugettext as _
from django.db.models import Count


# get the users teacher entry and school for the sidebar
def sidebar(request):
    context_dict = {}
    
    try:
        userid = request.user.id
        teacher = Teacher.objects.get(user = userid)
        context_dict['user_teacher'] = teacher

        if teacher.school:
            context_dict['school'] = teacher.school
        else:
            context_dict['school'] = "No School"
        
    except Teacher.DoesNotExist:
        pass

    return context_dict

def postcodeLocation(country, postcode_given):
    s=upper(str(postcode_given))     #converting given postcode to uppercase
    if ' ' not in s:
        s=s[:-3]+' '+s[-3:]   #if postcode has no space, add appropriately
    try:
        if country=='England':
            result=EnglandPostcodes.objects.get(Postcode=s)
        elif country=='Scotland':
            result=ScotlandPostcodes.objects.get(Postcode=s)
        elif country=='Wales':
            result=WalesPostcodes.objects.all().get(Postcode=s)
        elif country=='NorthernIreland':
            result=NorthernIrelandPostcodes.objects.get(Postcode=s)
        long=result.Longitude
        lat=result.Latitude
        return {'long': long,'lat': lat}
    except:
        return -1

    return

# function to convert a many to many relationship to a list of objects
def get_list(relation):
    objects = [relation[0]]
    i = 1
    while i < len(relation):
        objects += [relation[i]]
        i += 1
    return objects
    
# function to initialise a blank dictionary to pass into forms
# used to preset the tags in the forms
def blank_tag_dict():
    return {'level':[], 'topic':[], 'other':[]}
    
# function to return a list of the current tags
# used to preset the tags in the forms
# object type can be resource or pack
def populate_tag_dict(resource_id, object_type):
    selected_tags = blank_tag_dict()
    
    level_tags = object_type.objects.get(id=resource_id).tags.filter(tagtype='0')
    for tag in level_tags:
        selected_tags['level'] += [tag.id]
    
    topic_tags = object_type.objects.get(id=resource_id).tags.filter(tagtype='1')
    for tag in topic_tags:
        selected_tags['topic'] += [tag.id]
    
    other_tags = object_type.objects.get(id=resource_id).tags.filter(tagtype='2')
    for tag in other_tags:
        selected_tags['other'] += [tag.id]
    
    return selected_tags
    
# functino to return a dtring of the evolution type from an integer
def convert_to_evotype(number):
    print number
    number = int(number)
    EVOLUTIONS = ['Creation', 'Amendments', 'Style', 'Translation', 'Recontext', 'New Difficulty', 'New Format']
    return EVOLUTIONS[number]
    
    
# view for the homepage
def index(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # get teacher
    this_teacher = Teacher.objects.get(user = request.user)

    # get resources to show on homepage
    allresources = Resource.objects.all()
    context_dict['MyResources'] = allresources.filter(author=this_teacher)
    
    allpacks = Pack.objects.all()
    context_dict['MyPacks'] = allpacks.filter(author=this_teacher)
    
    want2talkMine=TeacherWantstoTalkResource.objects.all()
    context_dict['want2talkMine'] = want2talkMine.filter(resource__author=this_teacher)
 
    want2talk=TeacherWantstoTalkResource.objects.all()
    context_dict['want2talk'] = want2talk.filter(teacher_id=this_teacher)
    
    need2rate=TeacherDownloadsResource.objects.all().filter(teacher=this_teacher, rated=0)
    context_dict['need2rate'] = need2rate.filter(teacher=this_teacher)
    
    # return response object
    return render_to_response('treasure/user_home.html', context_dict, context)
   
# view for the homepage
def contribution(request):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # get teacher
    this_teacher = Teacher.objects.get(user = request.user)

    downloaded=TeacherDownloadsResource.objects.all().filter(teacher=this_teacher, used=0, rated=0)
    context_dict['downloaded'] = downloaded
    used=TeacherDownloadsResource.objects.all().filter(teacher=this_teacher, used=1)
    context_dict['used'] = used
    rated=TeacherDownloadsResource.objects.all().filter(teacher=this_teacher, rated=1)
    context_dict['rated'] = rated
    uploaded=Resource.objects.all().filter(author=this_teacher)
    #print uploaded
    context_dict['uploaded'] = uploaded
    link='treasure/contribution.html'

    # return response object
    return render_to_response(link, context_dict, context)


# view for the about page
def about(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # return response object
    return render_to_response('treasure/about.html', context_dict, context)
    
# view for the user's profile page
@login_required
def profile(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)

    # get user profile information
    # first and surname come from sidebar request
    try:
        context_dict['username'] = request.user.username
        context_dict['user_email'] = request.user.email

        userid = request.user.id
		
        teacher = Teacher.objects.get(user = userid)
        context_dict['user_firstname'] = teacher.firstname
        context_dict['user_lastname'] = teacher.surname
        
        # get school from the user, if they have any
        try:
            context_dict['user_school'] = teacher.school
        except:
            print "error"
	    	
        # get hubs from the user, if they have any
        if len(teacher.hubs.all()) >= 1:
            # get list of hub objects
            context_dict['user_hubs'] = get_list(teacher.hubs.all())
	    
	    # used to check the teacher exists
        context_dict['teacher'] = teacher
            
    except Teacher.DoesNotExist:
	    # do nothing as the template shows the "no user" page
        pass
    
    # return response object
    return render_to_response('treasure/profile.html', context_dict, context)

# view to allow the user to edit their profile
@login_required
def edit_profile(request,soc=0):
    # get context of request
    context = RequestContext(request)
    
    updated = False
    
    # get current user and teacher records
    my_user_record = request.user
    my_teacher_record =  request.user.teacher
    
    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # pass in instance of the record to be updated
        user_form = UserFormNoPW(data=request.POST, instance=my_user_record)
        teacher_form = TeacherForm(data=request.POST, instance=my_teacher_record)

        # If the two forms are valid...
        if user_form.is_valid() and teacher_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()
            
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            teacher = teacher_form.save(commit=False)
            teacher.user = user

            # Now we save the UserProfile model instance.
            teacher.save()

            # save the hubs the user has selected
            hubs = teacher_form.cleaned_data['hubs']
            for hub in hubs:
                teacher.hubs.add(hub)
            teacher.save()
            
            # Update our variable to tell the template registration was successful.
            updated = True

        # Invalid form or forms print problems to the terminal.
        else:
            print "ERROR", user_form.errors, teacher_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    else:
        # pass the current records to initially populate the forms
        user_form = UserFormNoPW(instance = my_user_record)
        teacher_form = TeacherForm(instance = my_teacher_record)
    
    # create context dictionary
    context_dict = sidebar(request)
    context_dict['user_form'] = user_form
    context_dict['teacher_form'] = teacher_form
    context_dict['updated'] = updated
    if soc!=0:
        context_dict['soc'] = 'soc'
    
    # return response object
    return render_to_response('treasure/edit_profile.html', context_dict, context)
    
# view to allow the user to edit a resource they have uploaded/created/linkedto
@login_required
def edit_resource(request, resource_id):
    # get context of request
    context = RequestContext(request)
    
    # create context dictionary
    context_dict = sidebar(request)
    context_dict['resource_id'] = resource_id
     
    # get resource
    this_resource = Resource.objects.get(id=resource_id)
    
    # get current user
    teacher = request.user.teacher
    
    # get tags of resource to preload them
    selected_tags = populate_tag_dict(resource_id, Resource)

    # check if current user owns this resource
    if this_resource.author == teacher:

        # If it's a HTTP POST, we're interested in processing form data.
        if request.method == 'POST':
            # Attempt to grab information from the raw form information.
            # pass in instance of the record to be updated
            form = EditResourceForm(selected_tags, data=request.POST, instance=this_resource)

            # If the form is valid...
            if form.is_valid():
                # hold off on saving to avoid integrity errors.
                new_resource = form.save(commit=False)
                
                # clear current tags
                new_resource.tags.clear()

                # combine the tags into one queryset
                tags =  form.cleaned_data['level_tags'] | \
                        form.cleaned_data['topic_tags'] | \
                        form.cleaned_data['other_tags']
                # save the tags the user has selected
                for tag in tags:
                    new_resource.tags.add(tag)
                                
                # save the new resource
                new_resource.save()
                
                # show user the updated page
                return HttpResponseRedirect('/resource/'+str(new_resource.id))

            # Invalid form or forms print problems to the terminal.
            else:
                print "ERROR", form.errors

        # Not a HTTP POST, so we render our form using two ModelForm instances.
        else:
            # pass the current records to initially populate the forms
            form = EditResourceForm(selected_tags, instance = this_resource)
        
        context_dict['form'] = form
            
    else:
        # if it is not their resource, then dont show the form
        pass
    
    # return response object
    return render_to_response('treasure/edit_resource.html', context_dict, context)
    
# view for the user's history (list of all actions) page
@login_required
def user_history(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # return response object
    return render_to_response('treasure/user_history.html', context_dict, context)# view for the user's history (list of all actions) page
    
# register user
def register(request):
    # get the context of request
    context = RequestContext(request)

    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        user_form = UserForm(data=request.POST)
        teacher_form = TeacherForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and teacher_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
            
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            teacher = teacher_form.save(commit=False)
            teacher.user = user

            # Now we save the UserProfile model instance.
            teacher.save()

            # save the hubs the user has selected
            hubs = teacher_form.cleaned_data['hubs']
            for hub in hubs:
                teacher.hubs.add(hub)
            teacher.save()
            
            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms print problems to the terminal.
        else:
            print "ERROR", user_form.errors, teacher_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    else:
        user_form = UserForm()
        teacher_form = TeacherForm()
    
    # create context dictionary
    context_dict = sidebar(request)
    context_dict['user_form'] = user_form
    context_dict['teacher_form'] = teacher_form
    context_dict['registered'] = registered

    # Render the template depending on the context.
    return render_to_response('treasure/register.html', context_dict, context)
            
         
# submit rating
def rate(request, resource_id):
    # get the context of request
    context = RequestContext(request)
    context_dict = sidebar(request)
    this_teacher = Teacher.objects.get(user=request.user)
    this_resource = Resource.objects.get(id=resource_id)
    try:
        condition = TeacherRatesResource.objects.get(teacher_id=this_teacher.id, resource_id=this_resource.id)
        context_dict['condition'] = condition
    except TeacherRatesResource.DoesNotExist:
            # do nothing
            pass
    try:
        download = TeacherDownloadsResource.objects.get(teacher_id=this_teacher.id, resource_id=this_resource.id)
    except TeacherDownloadsResource.DoesNotExist:
            # This could never happen
            pass
    rated = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        rating_form = RatingForm(request.POST)
        # If the form is valid..
        if rating_form.is_valid():
            # Save the rating to the database.
            rating=TeacherRatesResource(teacher_id=this_teacher.id,resource_id=this_resource.id,measure1=rating_form.cleaned_data['measure1'],measure2=rating_form.cleaned_data['measure2'],measure3=rating_form.cleaned_data['measure3'],comment=rating_form.cleaned_data['comment'])
            rating.save()
            download.rated='1'
            download.save()
            
            # Update our variable to tell the template registration was successful.
            rated = True

        # Invalid form or forms print problems to the terminal.
        else:
            print "ERROR", rating_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    else:
        rating_form=RatingForm()
    
    # create context dictionary
    context_dict['this_resource'] = this_resource
    context_dict['this_teacher'] = this_teacher
    context_dict['rating_form'] = rating_form
    context_dict['rated'] = rated

    # Render the template depending on the context.
    return render_to_response('treasure/rate.html', context_dict, context)
            
         
def use(request, resource_id, red):
    # get the context of request
    context = RequestContext(request)
    context_dict = sidebar(request)
    this_teacher = Teacher.objects.get(user=request.user)
    this_resource = Resource.objects.get(id=resource_id)

    try:
        download = TeacherDownloadsResource.objects.get(teacher_id=this_teacher.id, resource_id=this_resource.id)
    except TeacherDownloadsResource.DoesNotExist:
            # This could never happen
            pass

    download.used='1'
    download.save()
    link=''
    if red=='res':
        link= '/resource/'+resource_id
    elif red=='hist':
        link='/history/'
    else:
        link='/me/'

    return HttpResponseRedirect(link)


def talk(request, resource_id, var,red="res"):
    # get the context of request
    context = RequestContext(request)
    context_dict = sidebar(request)
    this_teacher = Teacher.objects.get(user=request.user)
    this_resource = Resource.objects.get(id=resource_id)
    teacher_school = School.objects.get(id=this_teacher.school_id)

    if var=="yes":
        talk=TeacherWantstoTalkResource(resource=this_resource, teacher=this_teacher,datetime=datetime.now(), latitude= teacher_school.latitude, longitude= teacher_school.longitude, disable=0)
        talk.save()
    elif var=="no":
        try:
            wanted = TeacherWantstoTalkResource.objects.get(teacher_id=this_teacher.id, resource_id=this_resource.id)
            wanted.delete()
        except TeacherWantstoTalkResource.DoesNotExist:
            # This could never happen
            pass

    link=''
    if red=='res':
        link= '/resource/'+resource_id
    elif red=='hist':
        link='/history/'
    else:
        link='/me/'

    return HttpResponseRedirect(link)

def talkHide(request, var):
    # get the context of request
    context = RequestContext(request)
    context_dict = sidebar(request)
    this_teacher = Teacher.objects.get(user=request.user)
    discuss=TeacherWantstoTalkResource.objects.all().filter(teacher=this_teacher)
    if var=="yes":
        discuss.update(disable=0)
    elif var=="no":
        discuss.update(disable=1)
    return HttpResponseRedirect('/me/')


def user_login(request):
    # get the context of request
    context = RequestContext(request)
    
    context_dict = sidebar(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                # An inactive account was used - no logging in!
                context_dict['disabled_account'] = "aye"
        else:
            # Bad login details were provided. So we can't log the user in.
            context_dict['bad_details'] = "aye"


    return render_to_response('treasure/login.html', context_dict, context)

# log the user out
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/')
    
    
# view for the add materials page
@login_required
def add_web_resource(request):
    # get context of request
    context = RequestContext(request)
    
    selected_tags = blank_tag_dict()
    
    # A HTTP POST?
    if request.method == 'POST':
        resource_form = ResourceForm(selected_tags, request.POST)
        web_form = WebForm(request.POST)

        # Have we been provided with a valid form?
        if resource_form.is_valid() and web_form.is_valid():
            # delay saving the model until we're ready to avoid integrity problems
            resource = resource_form.save(commit=False)
            
            # set foreign key of the author of the resource
            userid = request.user.id
            teacher = Teacher.objects.get(user = userid)
            resource.author = Teacher.objects.get(id = teacher.id)
            
            # this is a creation
            resource.evolution_type = "0"
            
            # default values for hidden
            resource.hidden = 0
            
            # todo: restrict views
            # initially 0 for now
            resource.restricted = 0
            
            # this is a web resource
            resource.resource_type = "web"
            
            # save the time the resource was created
            resource.datetime = datetime.now()

            # save resource before we add tags / set tree
            resource.save()
             
            # combine the tags into one queryset
            tags =  resource_form.cleaned_data['level_tags'] | \
                    resource_form.cleaned_data['topic_tags'] | \
                    resource_form.cleaned_data['other_tags']
            # save the tags the user has selected
            for tag in tags:
                resource.tags.add(tag)
                
            # this is a root so the tree is just the id
            resource.tree = resource.id
            
            resource.save()

            # delay saving the relationship model until we're ready
            # to avoid integrity problems
            web = web_form.save(commit=False)
            web.resource = resource
            
            # save the instance
            web.save()
            
            # create board for this resource
            board = Board(resource=resource, title=resource.name)
            board.save()            
            
            # Now show the new materials page
            return HttpResponseRedirect('/resource/'+str(resource.id))
        else:
            # The supplied form contained errors - just print them to the terminal.
            print resource_form.errors
            print web_form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        resource_form = ResourceForm(selected_tags)
        web_form = WebForm()
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    context_dict['resource_form'] = resource_form
    context_dict['web_form'] = web_form
    
    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('treasure/add_web_resource.html', context_dict, context)
    
# view for the add materials page
@login_required
def add_file_resource(request):
    # get context of request
    context = RequestContext(request)
    
    selected_tags = blank_tag_dict()

    # A HTTP POST?
    if request.method == 'POST':
        resource_form = ResourceForm(selected_tags, request.POST)
        file_form = FileForm(request.POST, request.FILES)

        # Have we been provided with a valid form?
        if resource_form.is_valid() and file_form.is_valid():
            # delay saving the model until we're ready to avoid integrity problems
            resource = resource_form.save(commit=False)
            
            # set foreign key of the author of the resource
            userid = request.user.id
            teacher = Teacher.objects.get(user = userid)
            resource.author = Teacher.objects.get(id = teacher.id)
                        
            # this is a creation
            resource.evolution_type = "0"
            
            # default values for hidden
            resource.hidden = 0
            
            # todo: restrict views
            # initially 0 for now
            resource.restricted = 0
            
            # this is a file resource
            resource.resource_type = "file"
            
            # set the time the resource was created
            resource.datetime = datetime.now()
            
            # save the instance before we add tags / set tree
            resource.save()
            
            # combine the tags into one queryset
            tags =  resource_form.cleaned_data['level_tags'] | \
                    resource_form.cleaned_data['topic_tags'] | \
                    resource_form.cleaned_data['other_tags']
            # save the tags the user has selected
            for tag in tags:
                resource.tags.add(tag)
                
            # this is a root so the tree is just the id
            resource.tree = resource.id
            
            resource.save()
            
            # add file to object
            files = FilesResource( path = request.FILES['path'])
            
            # associate file resource with parent resource
            files.resource = resource
            
            # save the resource
            files.save()
            
            # create board for this resource
            board = Board(resource=resource, title=resource.name)
            board.save()  
            
            # show user the new materials page
            return HttpResponseRedirect('/resource/'+str(resource.id))
        else:
            # The supplied form contained errors - just print them to the terminal.
            print resource_form.errors
            print file_form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        resource_form = ResourceForm(selected_tags)
        file_form = FileForm()
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    context_dict['resource_form'] = resource_form
    context_dict['file_form'] = file_form
    
    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('treasure/add_file_resource.html', context_dict, context)
    
# view for the add hub page
def add_hub(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = HubForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            geolocationDict=postcodeLocation(form.cleaned_data['country'],form.cleaned_data['postcode'])
            if geolocationDict!=-1:
                hub = Hub(name=form.cleaned_data['name'], address=form.cleaned_data['address'], longitude=geolocationDict['long'],latitude=geolocationDict['lat'])
                hub.save()

                return hub_view(request, hub.id)
            else:
                form._errors['postcode'] = '--Invalid Postcode. '
                print form.errors
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = HubForm()
    
    context_dict['form']  = form
    
    # Render the form depending on context
    return render_to_response('treasure/add_hub.html', context_dict, context)
    
# view for the add users page
def add_school(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = SchoolForm(request.POST)
        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            geolocationDict=postcodeLocation(form.cleaned_data['country'],form.cleaned_data['postcode'])
            if geolocationDict!=-1:
                school= School(name=form.cleaned_data['name'], town=form.cleaned_data['town'], address=form.cleaned_data['address'], latitude=geolocationDict['lat'], longitude=geolocationDict['long'])
                school.save()

                return school_view(request, school.id)
            else:
                form._errors['postcode'] = '--Invalid Postcode. '
                print form.errors
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = SchoolForm()
    
    context_dict['form'] = form
    
    # Render the form to template with context
    return render_to_response('treasure/add_school.html', context_dict, context)

# view to see all of the resource in the database
@login_required
def resources(request):
    # Request the context of the request.
    context = RequestContext(request)
    
    context_dict = sidebar(request)
    
    # get list of all resources
    resource_list = Resource.objects.all()
    context_dict['resources'] = resource_list
    
    # do a search
        # A HTTP POST?
    if request.method == 'POST':
        form = SearchForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # get tags from form
            level_tags = form.cleaned_data['level_tags']
            topic_tags = form.cleaned_data['topic_tags']
            other_tags = form.cleaned_data['other_tags']
        
            # initialise search results
            all_resources = Resource.objects.all()
            
            # if tags have been entered
            if level_tags | topic_tags | other_tags:
                # initialise the queryset
                found_resources = all_resources.filter(tags__name="")
            
                # filter to get the matching resources for level
                if level_tags:
                    level_resources = all_resources.filter(tags__in=level_tags).distinct()
                    
                # filter to get the matching resources for topic
                if topic_tags:
                    topic_resources = all_resources.filter(tags__in=topic_tags).distinct()
                        
                # filter to get the matching resources for level
                if other_tags:
                    other_resources = all_resources.filter(tags__in=other_tags).distinct()
                
                # combine search results (ew)
                if level_tags and topic_tags and other_tags:
                    found_resources = level_resources & topic_resources & other_resources
                elif level_tags and topic_tags:
                    found_resources = level_resources & topic_resources
                elif level_tags and other_tags:
                    found_resources = level_resources & other_resources
                elif topic_tags and other_tags:
                    found_resources = topic_resources & other_resources
                elif level_tags:
                    found_resources = level_resources
                elif topic_tags:
                    found_resources = topic_resources
                elif other_tags:
                    found_resources = other_resources
                                                 
                context_dict['resources'] = found_resources
            else:
                # if no tags are entered, do nothing
                # template handles error message
                pass
            
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = SearchForm()
    
    context_dict['form'] = form
    
    # Render the template depending on the context.
    return render_to_response('treasure/resources.html', context_dict, context)

#view to see all schools sorted in the database
@login_required
def schools(request):
    # Request the context of the request.
    context = RequestContext(request)
    
    context_dict = sidebar(request)
    
    # get list of all schools
    school_list = School.objects.all()
    context_dict['schools'] = school_list
    
    # Render the template depending on the context.
    return render_to_response('treasure/schools.html', context_dict, context)

# view to see all hubs in the database
@login_required
def hubs(request):
    # Request the context of the request.
    context = RequestContext(request)
    
    context_dict = sidebar(request)

    # get list of all resources
    hub_list = Hub.objects.all()
    context_dict['hubs'] = hub_list
    
    # Render the template depending on the context.
    return render_to_response('treasure/hubs.html', context_dict, context)
    
# view for the page for each resource
@login_required
def resource_view(request, resource_id):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    this_teacher = Teacher.objects.get(user=request.user)
    this_resource = Resource.objects.get(id=resource_id)
    try:
        rating_exists = TeacherRatesResource.objects.get(teacher_id=this_teacher.id, resource_id=this_resource.id)
        context_dict['rating_exists'] = rating_exists
    except TeacherRatesResource.DoesNotExist:
            # do nothing
            pass
    try:
        downloaded = TeacherDownloadsResource.objects.get(teacher_id=this_teacher.id, resource_id=this_resource.id)
        context_dict['downloaded'] = downloaded
    except TeacherDownloadsResource.DoesNotExist:
            # do nothing
            pass
    try:
        iWant2Talk = TeacherWantstoTalkResource.objects.get(teacher_id=this_teacher.id, resource_id=this_resource.id)
        context_dict['iWant2Talk'] = iWant2Talk
    except TeacherWantstoTalkResource.DoesNotExist:
            # do nothing
            pass
    try:
        # Can we find a resource with the given id?
        this_resource = Resource.objects.get(id=resource_id)
        try:
            feedback= TeacherRatesResource.objects.all().filter(resource_id=this_resource.id)
            context_dict['feedback']=feedback
        except TeacherRatesResource.DoesNotExist:
            pass
        
        # get fields
        context_dict['resource_name'] = this_resource.name
        context_dict['description'] = this_resource.description
        
        # get authors name
        context_dict['author'] = this_resource.author.firstname + " " + this_resource.author.surname
        
        # check if user owns this resource
        if this_resource.author == request.user.teacher:
            context_dict['owned'] = True
            
        # get tags
        filtered_tags = this_resource.tags.filter(tagtype='0')
        if filtered_tags:
            context_dict['level_tags'] = get_list(filtered_tags)
        
        filtered_tags = this_resource.tags.filter(tagtype='1')
        if filtered_tags:
            context_dict['topic_tags'] = get_list(filtered_tags)
        
        filtered_tags = this_resource.tags.filter(tagtype='2')
        if filtered_tags:
            context_dict['other_tags'] = get_list(filtered_tags)
                    
        try:
            # can we find a web resource with the given resource?
            web_resource = WebResource.objects.get(resource = this_resource)
            
            # add fields to dict
            context_dict['label'] = 'Visit'
            context_dict['web_resource'] = True
            
        except WebResource.DoesNotExist:
            # do nothing
            pass
            
        try:
            # can we find a file resource with the given resource?
            files_resource = FilesResource.objects.get(resource = this_resource)
            
            # add label to dict
            context_dict['label'] = 'Download'
            context_dict['files_resource'] = True
            
        except FilesResource.DoesNotExist:
            # do nothing
            pass
            
        # get packs
        context_dict['partofpacks'] = this_resource.packs.filter(name__isnull=False)

        # get interactions
        want2talk=TeacherWantstoTalkResource.objects.all()
        context_dict['want2talk'] = want2talk.filter(resource_id=resource_id)
        
        # get changelog
        changelog = []
        previous_versions = this_resource.tree.split()[0].split(",")# unicode (ew)
        i = 0

        while i<len(previous_versions)-1:
            prev_resource = Resource.objects.get(id = previous_versions[i])
            next_resource = Resource.objects.get(id = previous_versions[i+1])
            evo_type = convert_to_evotype(next_resource.evolution_type)
            changelog += [[previous_versions[i], prev_resource.name, evo_type, next_resource.evolution_explanation]]
            i += 1
        changelog += [previous_versions[-1]]
        
        context_dict["changelog"] = changelog
        
         # used to verify it exists
        context_dict['resource'] = this_resource
    except Resource.DoesNotExist:
        # We get here if we didn't find the specified resource.
        # Don't do anything - the template displays the "no resource" message for us.
        pass

    # return response object
    return render_to_response('treasure/resource.html', context_dict, context)
    
# view for the page for each hub
@login_required
def hub_view(request, hub_id):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    try:
        # Can we find a hub with the given id?
        this_hub = Hub.objects.get(id=hub_id)
        
        # get fields
        context_dict['hub_name'] = this_hub.name
        context_dict['address'] = this_hub.address
        context_dict['lat'] = this_hub.latitude
        context_dict['lon'] = this_hub.longitude

        # used to verify it exists
        context_dict['hub'] = this_hub
    except Hub.DoesNotExist:
        # We get here if we didn't find the specified hub.
        # Don't do anything - the template displays the "no hub" message for us.
        pass
    
    # return response object
    return render_to_response('treasure/hub.html', context_dict, context)
    
# view for the page for each hub
@login_required
def school_view(request, school_id):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    try:
        # Can we find a school with the given id?
        this_school = School.objects.get(id=school_id)
        
        # get fields
        context_dict['school_name'] = this_school.name
        context_dict['town'] = this_school.town
        context_dict['address'] = this_school.address
        context_dict['lat'] = this_school.latitude
        context_dict['lon'] = this_school.longitude

        # used to verify it exists
        context_dict['school'] = this_school
    except School.DoesNotExist:
        # We get here if we didn't find the specified school.
        # Don't do anything - the template displays the "no school" message for us.
        pass
    
    # return response object
    return render_to_response('treasure/school.html', context_dict, context)

# view to see all tags in the database
@login_required
def tags(request):
    # Request the context of the request.
    context = RequestContext(request)
    
    #create context dictionary to send back to template
    context_dict = sidebar(request)
    
    # get list of all tags
    tag_list = Tag.objects.all()
    
    # get tags
    filtered_tags = tag_list.filter(tagtype='0')
    if filtered_tags:
        context_dict['level_tags'] = get_list(filtered_tags)
    
    filtered_tags = tag_list.filter(tagtype='1')
    if filtered_tags:
        context_dict['topic_tags'] = get_list(filtered_tags)
    
    filtered_tags = tag_list.filter(tagtype='2')
    if filtered_tags:
        context_dict['other_tags'] = get_list(filtered_tags)
    
    # Render the template depending on the context.
    return render_to_response('treasure/tags.html', context_dict, context)

# view to add a tag to the database
@login_required
def add_tag(request):
    # Request the context of the request.
    context = RequestContext(request)
    
    #create context dictionary to send back to template
    context_dict = sidebar(request)
    
    # A HTTP POST?
    if request.method == 'POST':
        form = TagForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Put off saving to avoid integrity errors.
            tag = form.save(commit=False)
            
            # only allow 'other tags' to be created using the form
            # 'levels' and 'topics' should be predefined by admins
            tag.tagtype = '2'
            
            # now save the tag in the database
            tag.save()
                        
            return tags(request)
            
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = TagForm()
    
    context_dict['form'] = form
    
    # Render the template depending on the context.
    return render_to_response('treasure/add_tag.html', context_dict, context)

# view to see all packs in the database
@login_required
def packs(request):
    # Request the context of the request.
    context = RequestContext(request)

    #create context dictionary to send back to template
    context_dict = sidebar(request)

    # get list of all packs
    pack_list = Pack.objects.all()
    context_dict['packs'] = pack_list
    
        # A HTTP POST?
    if request.method == 'POST':
        form = SearchForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # get tags from form
            level_tags = form.cleaned_data['level_tags']
            topic_tags = form.cleaned_data['topic_tags']
            other_tags = form.cleaned_data['other_tags']
            
            # initialise search results
            all_packs = Pack.objects.all()
            
            # if tags have been entered
            if level_tags | topic_tags | other_tags:
                # initialise the queryset
                found_packs = all_packs.filter(tags__name="")
            
                # filter to get the matching resources for level
                if level_tags:
                    level_packs = all_packs.filter(tags__in=level_tags).distinct()
                    
                # filter to get the matching resources for topic
                if topic_tags:
                    topic_packs = all_packs.filter(tags__in=topic_tags).distinct()
                        
                # filter to get the matching resources for level
                if other_tags:
                    other_packs = all_packs.filter(tags__in=other_tags).distinct()
                
                # combine search results (ew)
                if level_tags and topic_tags and other_tags:
                    found_packs = level_packs & topic_packs & other_packs
                elif level_tags and topic_tags:
                    found_packs = level_packs & topic_packs
                elif level_tags and other_tags:
                    found_packs = level_packs & other_packs
                elif topic_tags and other_tags:
                    found_packs = topic_packs & other_packs
                elif level_tags:
                    found_packs = level_packs
                elif topic_tags:
                    found_packs = topic_packs
                elif other_tags:
                    found_packs = other_packs
                                                 
                context_dict['packs'] = found_packs
            else:
                # if no tags are entered, do nothing
                # template handles error message
                pass
            
            searched = True
            
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = SearchForm()
    
    context_dict['form'] = form

    # Render the template depending on the context.
    return render_to_response('treasure/packs.html', context_dict, context)

# view to see resource tagged with a specific tag
@login_required
def tag(request, tag_id):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    try:
        # Can we find a hub with the given id?
        this_tag = Tag.objects.get(id=tag_id)
        
        # get resources (if available)
        filtered_resources = Resource.objects.filter(tags__id=tag_id)
        if filtered_resources:
            context_dict['tagged_resources'] = filtered_resources
            
        # get packs (if available)
        filtered_packs = Pack.objects.filter(tags__id=tag_id)
        if filtered_packs:
            context_dict['tagged_packs'] = filtered_packs
            
        # used to verify tag exists
        context_dict['tag'] = this_tag
    except Tag.DoesNotExist:
        # We get here if we didn't find the specified tag.
        # Don't do anything - the template displays the "no tag" message for us.
        pass
    
    # return response object
    return render_to_response('treasure/tag.html', context_dict, context)
    

    
# Pack view
@login_required
def pack(request, pack_id):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    try:
        this_pack = Pack.objects.get(id=pack_id)
        
        # get resources
        context_dict['pack_resources'] = Resource.objects.filter(packs__id=pack_id)
        
        # check if user owns this resource
        if this_pack.author == request.user.teacher:
            context_dict['owned'] = True

        # get tags
        filtered_tags = this_pack.tags.filter(tagtype='0')
        if filtered_tags:
            context_dict['level_tags'] = get_list(filtered_tags)
        
        filtered_tags = this_pack.tags.filter(tagtype='1')
        if filtered_tags:
            context_dict['topic_tags'] = get_list(filtered_tags)
        
        filtered_tags = this_pack.tags.filter(tagtype='2')
        if filtered_tags:
            context_dict['other_tags'] = get_list(filtered_tags)

        # used to verify it exists
        context_dict['pack'] = this_pack
    except Pack.DoesNotExist:
        # We get here if we didn't find the specified tag.
        # Don't do anything - the template displays the "no tag" message for us.
        pass
    
    # return response object
    return render_to_response('treasure/pack.html', context_dict, context)

# view to allow the user to edit a pack they have uploaded/created/linkedto
@login_required
def edit_pack(request, pack_id):
    # get context of request
    context = RequestContext(request)
    
    # create context dictionary
    context_dict = sidebar(request)
    context_dict['pack_id'] = pack_id
    
    # get tags of parent
    selected_tags = populate_tag_dict(pack_id, Pack)
     
    # get resource
    this_pack = Pack.objects.get(id=pack_id)
    
    # get current user
    teacher = request.user.teacher

    # check if current user owns this pack
    if this_pack.author == teacher:

        # If it's a HTTP POST, we're interested in processing form data.
        if request.method == 'POST':
            # Attempt to grab information from the raw form information.
            # pass in instance of the record to be updated
            form = EditPackForm(selected_tags, data=request.POST, instance=this_pack)

            # If form is valid...
            if form.is_valid():
                # Save the user's form data to the database.
                new_pack = form.save(commit=False)
                
                # clear current tags
                new_pack.tags.clear()

                # combine the tags into one queryset
                tags =  form.cleaned_data['level_tags'] | \
                        form.cleaned_data['topic_tags'] | \
                        form.cleaned_data['other_tags']
                # save the tags the user has selected
                for tag in tags:
                    new_pack.tags.add(tag)
                                
                # save the new pack
                new_pack.save()
                
                # show user the updated page
                return HttpResponseRedirect('/packs/'+str(new_pack.id))

            # Invalid form or forms print problems to the terminal.
            else:
                print "ERROR", form.errors

        # Not a HTTP POST, so we render our form using two ModelForm instances.
        else:
            # pass the current records to initially populate the forms
            form = EditPackForm(selected_tags, instance = this_pack)
        
        context_dict['form'] = form
            
    else:
        # if it is not their pack, then dont show the form
        pass
    
    # return response object
    return render_to_response('treasure/edit_pack.html', context_dict, context)

# view to explore the resources on the site
@login_required
def explore(request):
    # Request the context of the request.
    context = RequestContext(request)
    
    #create context dictionary to send back to template
    context_dict = sidebar(request)

    try:
        packs= Pack.objects.filter(explore=1)
        context_dict['packs'] = packs
    except Pack.DoesNotExist:
        pass
    
    # Render the template depending on the context.
    return render_to_response('treasure/explore.html', context_dict, context)
    
# view to see the evolution of a resource
@login_required
def versions(request, resource_id):
    # Request the context of the request.
    context = RequestContext(request)
    
    #create context dictionary to send back to template
    context_dict = sidebar(request)
    
    # get direct tree
    tree = Resource.objects.get(id = resource_id).tree
    
    #split tree into each node
    nodes = tree.split(',')
    
    all_resources = Resource.objects.all()
    ancestor_nodes = []
    
    for node_id in nodes:
        ancestor_nodes += [all_resources.get(id=node_id)]
    
    context_dict['nodes'] = ancestor_nodes
    context_dict['raw_tree'] = tree
    
    # Render the template depending on the context.
    return render_to_response('treasure/versions.html', context_dict, context)
    
# view to evolve a resource
@login_required
def evolve(request, parent_id):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # get tags of parent
    selected_tags = populate_tag_dict(parent_id, Resource)
    
    # A HTTP POST?
    if request.method == 'POST':
        
        resource_form = EvolveResourceForm(selected_tags,request.POST)
        file_form = FileForm(request.POST, request.FILES)
        web_form = WebForm(request.POST)
        
        # if evolution is a file upload
        if 'file_evolve' in request.POST:
            # Have we been provided with a valid form?
            if resource_form.is_valid() and file_form.is_valid():
                # delay saving the model until we're ready to avoid integrity problems
                resource = resource_form.save(commit=False)
                
                # set foreign key of the author of the resource
                userid = request.user.id
                teacher = Teacher.objects.get(user = userid)
                resource.author = Teacher.objects.get(id = teacher.id)
                
                #default hidden
                resource.hidden = 0
                
                # todo: implement restrictions
                # initially 0 for now
                resource.restricted = 0
                
                # set type of resource
                resource.resource_type = 'file'
                
                # set the time the resource was created
                resource.datetime = datetime.now()
                
                # save the resource before we add tags / set tree
                resource.save()
                
                # append new id to parents tree
                resource.tree = Resource.objects.get(id=parent_id).tree + u',' + unicode(resource.id)
                
                # combine the tags into one queryset
                tags =  resource_form.cleaned_data['level_tags'] | \
                        resource_form.cleaned_data['topic_tags'] | \
                        resource_form.cleaned_data['other_tags']
                # save the tags the user has selected
                for tag in tags:
                    resource.tags.add(tag)
                resource.save()
                
                # add file to object
                files = FilesResource( path = request.FILES['path'])
                
                # associate file resource with parent resource
                files.resource = resource
                
                # save the instance
                files.save()
                
                # create board for this resource
                board = Board(resource=resource, title=resource.name)
                board.save() 
                
                # show user the new materials page
                return HttpResponseRedirect('/resource/'+str(resource.id))
            else:
                # The supplied form contained errors - just print them to the terminal.
                print resource_form.errors
                print file_form.errors
                context_dict['error'] = 'file'


        # if evolution is a web upload
        elif 'web_evolve' in request.POST:
            # Have we been provided with a valid form?
            if resource_form.is_valid() and web_form.is_valid():
                # delay saving the model until we're ready to avoid integrity problems
                resource = resource_form.save(commit=False)
                
                # set foreign key of the author of the resource
                userid = request.user.id
                teacher = Teacher.objects.get(user = userid)
                resource.author = Teacher.objects.get(id = teacher.id)
                
                #default hidden
                resource.hidden = 0
                
                # todo: implement restrictions
                # initially 0 for now
                resource.restricted = 0
                
                # set type of resource
                resource.resource_type = 'web'
                
                # set the time the resource was created
                resource.datetime = datetime.now()
                
                # save resource so that tree / tags can be set
                resource.save()
                
                # append new id to parents tree
                resource.tree = Resource.objects.get(id=parent_id).tree + u',' + unicode(resource.id)
                
                # combine the tags into one queryset
                tags =  resource_form.cleaned_data['level_tags'] | \
                        resource_form.cleaned_data['topic_tags'] | \
                        resource_form.cleaned_data['other_tags']
                # save the tags the user has selected
                for tag in tags:
                    resource.tags.add(tag)
                
                resource.save()
                
                # delay saving the relationship model until we're ready
                # to avoid integrity problems
                web = web_form.save(commit=False)
                web.resource = resource
                
                # save the instance
                web.save()
                
                # create board for this resource
                board = Board(resource=resource, title=resource.name)
                board.save() 
                
                # Now show the new materials page
                return HttpResponseRedirect('/resource/'+str(resource.id))
            else:
                # The supplied form contained errors - just print them to the terminal.
                print resource_form.errors
                print web_form.errors
                context_dict['error'] = 'web'
        
    else:
        # If the request was not a POST, display the form to enter details.
        resource_form = EvolveResourceForm(selected_tags)
        file_form = FileForm()
        web_form = WebForm()
    
    # pass data to context dict for template
    context_dict['resource_form'] = resource_form
    context_dict['file_form'] = file_form
    context_dict['web_form'] = web_form
    context_dict['resource_id']= parent_id
    
    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('treasure/evolve.html', context_dict, context)
    
# view to track a resource
@login_required
def track(request, resource_id, timeline=0):
    # Request the context of the request.
    context = RequestContext(request)
    
    #create context dictionary to send back to template
    context_dict = sidebar(request)
    this_resource = get_object_or_404(Resource, id=resource_id)
    this_teacher = Teacher.objects.get(user=request.user)
    teacher_school = School.objects.get(id=this_teacher.school_id)
    context_dict['lat']=teacher_school.latitude
    context_dict['lng']=teacher_school.longitude
    context_dict['timeline']=timeline
    markerCt=0
    animationTimeout=0
    #Track locations
    try:
        downloaded=TeacherDownloadsResource.objects.all().filter(resource=this_resource).order_by('datetime')
        if timeline!=0:
            downloaded=downloaded.filter(used=0)
            markerCt=markerCt+downloaded.count()
        context_dict['downloaded']=downloaded
    except TeacherDownloadsResource.DoesNotExist:
        pass
    try:
        used=TeacherDownloadsResource.objects.all().filter(resource=this_resource, used=1).order_by('datetime')
        if timeline!=0:
            used=used.filter(rated=0)
            markerCt=markerCt+used.count()
        context_dict['used']=used
    except TeacherDownloadsResource.DoesNotExist:
        pass
    try:
        rated=TeacherDownloadsResource.objects.all().filter(resource=this_resource, rated=1).order_by('datetime')
        context_dict['rated']=rated
    except TeacherDownloadsResource.DoesNotExist:
        pass
    try:
        discuss=TeacherWantstoTalkResource.objects.all().filter(resource=this_resource, disable=0).order_by('datetime')
        context_dict['discuss']=discuss
    except TeacherWantstoTalkResource.DoesNotExist:
        pass
    if timeline=='timeline':
        animationTimeout=10000/markerCt
    context_dict['animationTimeout']=animationTimeout
    # Render the template depending on the context.
    return render_to_response('treasure/track.html', context_dict, context)
    
# view to add a resource to a pack
@login_required
def addtopack(request, resource_id):
    # Request the context of the request.
    context = RequestContext(request)
    
    #create context dictionary to send back to template
    context_dict = sidebar(request)
    context_dict['resource_id'] = resource_id
    
    # if user selects button, add resource to pack
    if request.method == 'POST':
        # get packid from request
        packid = request.POST.get("packid", "")
        
        # get this resource
        resources = Resource.objects.all()
        this_resource = resources.get(id=resource_id)

        # get this pack
        packs = Pack.objects.all()
        this_pack = packs.get(id=packid)
        
        # add resource to pack
        this_resource.packs.add(this_pack)
        
        return pack(request, packid)
    
    else:
        # try to get the packs for this user
        try:
            # get user id
            userid = request.user.id
            teacher = Teacher.objects.get(user = userid)
            context_dict['packs'] = Pack.objects.all().filter(author=teacher)
        except:
            pass
    
    # Render the template depending on the context.
    return render_to_response('treasure/addtopack.html', context_dict, context)
    
# view to add a pack to the database
@login_required
def newpack(request):

    # Request the context of the request.
    context = RequestContext(request)
    
    #create context dictionary to send back to template
    context_dict = sidebar(request)
    
    # get tags of resource
    selected_tags = blank_tag_dict()
    
    # A HTTP POST?
    if request.method == 'POST':
        form = PackForm(selected_tags, request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Put off saving to avoid integrity errors.
            this_pack = form.save(commit=False)
            
            # do not feature every pack on treasure/explore/
            this_pack.explore = '0'
            
            # default values for hidden
            this_pack.hidden = 0
            
            # todo: restrict views
            # initially 0 for now
            this_pack.restricted = 0
            
            # add author
            userid = request.user.id
            teacher = Teacher.objects.get(user = userid)
            this_pack.author = Teacher.objects.get(id = teacher.id)
            
            # now save the pack in the database so tags can be added
            this_pack.save()
            
            #add tags
            # combine the tags into one queryset
            tags =  form.cleaned_data['level_tags'] | \
                    form.cleaned_data['topic_tags'] | \
                    form.cleaned_data['other_tags']
            # save the tags the user has selected
            for tag in tags:
                this_pack.tags.add(tag)
                
            # save again
            this_pack.save()
                        
            # Now show the new pack page
            return HttpResponseRedirect('/packs/'+str(this_pack.id))
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = PackForm(selected_tags)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    context_dict['form'] = form
    
    # Render the template depending on the context.
    return render_to_response('treasure/add_pack.html', context_dict, context)
    
# view to add a pack to the database
# initialises the new pack with the resource the new pack button was selected on
@login_required
def newpack_initial(request, resource_id):

    # Request the context of the request.
    context = RequestContext(request)
    
    #create context dictionary to send back to template
    context_dict = sidebar(request)
    
    # get tags of resource
    selected_tags = blank_tag_dict()
    
    # A HTTP POST?
    if request.method == 'POST':
        form = PackForm(selected_tags, request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Put off saving to avoid integrity errors.
            this_pack = form.save(commit=False)
            
            # do not feature every pack on treasure/explore/
            this_pack.explore = '0'
            
            # default values for hidden
            this_pack.hidden = 0
            
            # todo: restrict views
            # initially 0 for now
            this_pack.restricted = 0
            
            # add author
            userid = request.user.id
            teacher = Teacher.objects.get(user = userid)
            this_pack.author = Teacher.objects.get(id = teacher.id)
            
            # now save the pack in the database so tags can be added
            this_pack.save()
            
            #add tags
            # combine the tags into one queryset
            tags =  form.cleaned_data['level_tags'] | \
                    form.cleaned_data['topic_tags'] | \
                    form.cleaned_data['other_tags']
            # save the tags the user has selected
            for tag in tags:
                this_pack.tags.add(tag)
                
            # save again
            this_pack.save()
            
            # get resource
            this_resource = Resource.objects.get(id=resource_id)
        
            # add resource to pack
            this_resource.packs.add(this_pack)
            this_resource.save()
                        
            # Now show the new pack page
            return HttpResponseRedirect('/packs/'+str(this_pack.id))
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = PackForm(selected_tags)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    context_dict['resource_id'] = resource_id
    context_dict['form'] = form
    
    # Render the template depending on the context.
    return render_to_response('treasure/add_pack.html', context_dict, context)

# view for the user's history (list of all actions) page
@login_required
def download(request, resource_id, bypass=0):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)

    try:
        this_teacher = Teacher.objects.get(user=request.user)
        this_resource = get_object_or_404(Resource, id=resource_id)
        teacher_school = School.objects.get(id=this_teacher.school_id)

        # Get resource URL
        try:
            res = WebResource.objects.get(resource = this_resource)
            url=res.url
	except WebResource.DoesNotExist:
            # Not a WebResource
            pass
	try:
            res = FilesResource.objects.get(resource = this_resource)
            url='/../media/'+str(res.path)
	except FilesResource.DoesNotExist:
            # Not a FilesResource
            pass

	# Saving Download Record in the Database
	try:
            downloaded= TeacherDownloadsResource.objects.get(teacher=this_teacher, resource=this_resource)
	except TeacherDownloadsResource.DoesNotExist:
            download_record= TeacherDownloadsResource(teacher=this_teacher, resource=this_resource, datetime=datetime.now(), latitude= teacher_school.latitude, longitude= teacher_school.longitude, used=0, rated=0)
            download_record.save()
            pass

    except Resource.DoesNotExist:
	# No Resource
	pass
    if bypass==0:
        # IfDownload Resource
        return redirect(url)
    else:
        return redirect("/resource/"+resource_id+"/rate/")


@login_required
def newSocialAuthentication(request):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)

    try:
        his = request.user
        new_teacher = Teacher(user_id=his.id, firstname=his.first_name, surname=his.last_name)
        new_teacher.save()
    except Teacher.DoesNotExist:
            # Not a WebResource
            pass

    # Render the template updating the context dictionary.
    return redirect('/profile/edit/soc/')


# View to show a basic homepage to all users
def home(request):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # get if teacher has pending actions
    this_user = request.user.id
    need2rate=TeacherDownloadsResource.objects.all().filter(teacher=this_user, rated=0)
    context_dict['need2rate'] = need2rate.filter(teacher=this_user)
    
    # get newest resources
    context_dict['new_resources'] = Resource.objects.all().order_by('-id')[:5]
    
    # get top resources
    context_dict['top_resources'] = Resource.objects.annotate(num_downloads=Count('teacherdownloadsresource')).order_by('-num_downloads')[:5]
    
    # get top packs
    context_dict['new_packs'] = Pack.objects.all().order_by('-id')[:5]
    
    # get latest ratings
    context_dict['new_ratings'] = TeacherRatesResource.objects.all().order_by('-id')[:5]
    
    # get numbers
    context_dict['num_resources'] = Resource.objects.all().count()
    context_dict['num_packs'] = Pack.objects.all().count()
    context_dict['num_users'] = Teacher.objects.all().count()
    
    # Render the template updating the context dictionary.
    return render_to_response('treasure/index.html', context_dict, context)
    

# View to show a help page
@login_required
def help(request):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # Render the template updating the context dictionary.
    return render_to_response('treasure/help.html', context_dict, context)

# view to show overview of all boards
@login_required
def forum(request):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    boards = Board.objects.all()
    
    # todo:add more detail to dict (number of posts on each board
    # todo: maybe sort the boards in order of last post (show times of last posts?)
    
    context_dict['forum'] = boards
    
    # Render the template updating the context dictionary.
    return render_to_response('treasure/forum.html', context_dict, context)
   
# view to show board
@login_required
def board(request, board_url):
  
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # add url to contextdict
    context_dict['board_url']=board_url
    
    #determine if other or resourceboard
    # check if url is a number
    try: 
        int(board_url)
        isNumber = True
    except ValueError:
        isNumber= False
    
    if isNumber:
        try:
            # check resource has a forum attached
            this_resource = Resource.objects.all().get(id=board_url)
            context_dict['resource'] = this_resource
            print "1"
            this_board = Board.objects.all().get(resource = this_resource)
            try:
                # get the threads on the forum
                board = Thread.objects.all().filter(board = this_board)
                context_dict['board'] = board
            except Thread.DoesNotExist:
                # do not pass a board object to template as there are no threads
                print "no threads", board_url
                pass
        except Resource.DoesNotExist:
             # no board here
            context_dict['invalid'] = True
    else:
        try:
            # check the word has a url attached
            this_board = Board.objects.all().get(title=board_url)
            context_dict['title'] = board_url
            try:
                # get the threads on the forum
                board = Thread.objects.all().filter(board = this_board)
                context_dict['board'] = board
            except Thread.DoesNotExist:
                # do not pass a board object to template as there are no threads
                print "no threads", board_url
                pass
        except Board.DoesNotExist:
            context_dict['invalid'] = True
            
    # todo: maybe sort the threads in created/lastpostedin order?
    
    # Render the template updating the context dictionary.
    return render_to_response('treasure/board.html', context_dict, context)
    
@login_required
def new_thread(request, board_url):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # add board url to dict
    context_dict['board_url'] = board_url
    
    # check board_url coresponds to a board
    try: 
        int(board_url)
        isNumber = True
    except ValueError:
        isNumber= False
    if isNumber:
        try:
            # if url is number, get board relating to that object
            this_board = Board.objects.all().get(resource = Resource.objects.all().get(id=board_url))
        except (Board.DoesNotExist, Resource.DoesNotExist) as e:
            # no board at this url
            context_dict['invalid'] = "invalid"
    else:
        try:
            # otherwise get board associated with the word
            this_board = Board.objects.all().get(title=board_url)
        except Board.DoesNotExist:
            # no board at this url
            context_dict['invalid'] = "invalid"
    
    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # pass in instance of the record to be updated
        form = PostThreadForm(request.POST)

        # If the form is valid...
        if form.is_valid():
            # hold off on saving to avoid integrity errors.
            new_thread = form.save(commit=False)
            
            # get board
            # check if url is a number
            try: 
                int(board_url)
                isNumber = True
            except ValueError:
                isNumber= False
            if isNumber:
                try:
                    # if url is number, get board relating to that object
                    print "1"
                    this_board = Board.objects.all().get(resource = Resource.objects.all().get(id=board_url))
                except Board.DoesNotExist:
                    # no board at this url
                    context_dict['invalid'] = "invalid"
                    print "2"
            else:
                try:
                    # otherwise get board associated with the word
                    this_board = Board.objects.all().get(title=board_url)
                    print "3"
                except Board.DoesNotExist:
                    # no board at this url
                    context_dict['invalid'] = "invalid"
                    print "4"
            new_thread.board = this_board
            
            # set author
            new_thread.author = Teacher.objects.all().get(user = request.user)
            
            # set time of threadposting
            new_thread.datetime = datetime.now()
            
            # set threadtype to 2 (from forum so not rrating, could maybe be question)
            # todo: maybe allow users to choose type of forum to submit
            new_thread.threadtype = 2
                            
            # save the new resource
            new_thread.save()
            
            # show user the updated page
            return HttpResponseRedirect('/forum/'+str(board_url)+'/'+str(new_thread.id))

        # Invalid form or forms print problems to the terminal.
        else:
            print "ERROR", form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    else:
        # pass the current records to initially populate the forms
        form = PostThreadForm()
    
    context_dict['form'] = form
    
    # Render the template updating the context dictionary.
    return render_to_response('treasure/new_thread.html', context_dict, context)

# view to show thread
@login_required
def thread(request, board_url, thread_id):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # pass url to form
    context_dict['board_url'] = board_url
    context_dict['thread_id'] = thread_id
        
    # get thread
    try:
        this_thread = Thread.objects.all().get(id=thread_id)
        context_dict['thread'] = this_thread
    except Thread.DoesNotExist:
        # do not pass a thread object to the template
        pass
    
    # add posts to contextdict
    the_posts = Post.objects.all().filter(thread = this_thread)
    context_dict['posts'] = the_posts
    
    # check url is properly formed
    # (thread id, belongs to the object pointed to by board_url)
    # first get board from url
    try: 
        int(board_url)
        isNumber = True
    except ValueError:
        isNumber= False
    if isNumber:
        try:
            # if url is number, get board relating to that object
            this_board = Board.objects.all().get(resource = Resource.objects.all().get(id=board_url))
        except (Board.DoesNotExist, Resource.DoesNotExist) as e:
            # no board at this url
            context_dict['invalid'] = "invalid"
    else:
        try:
            # otherwise get board associated with the word
            this_board = Board.objects.all().get(title=board_url)
        except Board.DoesNotExist:
            # no board at this url
            context_dict['invalid'] = "invalid"
    # then check that thread is part of this board
    if this_thread.board != this_board:
        context_dict['invalid'] = "invalid"
    
    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # pass in instance of the record to be updated
        form = PostPostForm(request.POST)

        # If the form is valid...
        # and content is not empty
        if form.is_valid() and form.cleaned_data['content'] != "":
            # hold off on saving to avoid integrity errors.
            new_post = form.save(commit=False)  
            
            print form.cleaned_data['content']
            print form.cleaned_data['content'] == ""
            
            new_post.thread = Thread.objects.all().get(id = thread_id)          
            
            # set author
            new_post.author = Teacher.objects.all().get(user = request.user)
            
            # set time of threadposting
            new_post.datetime = datetime.now()
                            
            # save the new resource
            new_post.save()
            
            # show user the updated page
            return HttpResponseRedirect('/forum/'+str(board_url)+'/'+str(thread_id))

        # Invalid form or forms print problems to the terminal.
        else:
            print "ERROR", form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    else:
        # pass the current records to initially populate the forms
        form = PostPostForm()
    
    context_dict['form'] = form
    
    # Render the template updating the context dictionary.
    return render_to_response('treasure/thread.html', context_dict, context)
