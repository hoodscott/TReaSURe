from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from treasure.forms import *
from treasure.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from string import split
from datetime import datetime
from django.utils.html import escape, escapejs

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
    
    level_tags = object_type.objects.get(id=resource_id).tags.filter(type='0')   
    for tag in level_tags:
        selected_tags['level'] += [tag.id]
    
    topic_tags = object_type.objects.get(id=resource_id).tags.filter(type='1')   
    for tag in topic_tags:
        selected_tags['topic'] += [tag.id]
    
    other_tags = object_type.objects.get(id=resource_id).tags.filter(type='2')   
    for tag in other_tags:
        selected_tags['other'] += [tag.id]
    
    return selected_tags
    
# view for the homepage
def index(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # get user
    this_user = request.user.id

    # get resources to show on homepage
    allresources = Resource.objects.all()
    context_dict['MyResources'] = allresources.filter(author=this_user)
    
    allpacks = Pack.objects.all()
    context_dict['MyPacks'] = allpacks.filter(author=this_user)
    
    want2talk=TeacherWantstoTalkResource.objects.all()
    context_dict['want2talk'] = want2talk.filter(resource__author=this_user)
    
    need2rate=TeacherDownloadsResource.objects.all()
    context_dict['need2rate'] = need2rate.filter(teacher=this_user)

    
    # return response object
    return render_to_response('treasure/index.html', context_dict, context)
   
# view for the homepage
def history(request):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)


    downloads=TeacherDownloadsResource.objects.all()
    context_dict['downloads'] = downloads.filter(teacher=request.user.id)


    # return response object
    return render_to_response('treasure/history.html', context_dict, context)


# view for the about page
def about(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # return response object
    return render_to_response('treasure/about.html', context_dict, context)
    
    
# view for the search page
@login_required
def search(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    searched = False

    # A HTTP POST?
    if request.method == 'POST':
        form = SearchForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # get tags from form
            level_tags = form.cleaned_data['level_tags']
            topic_tags = form.cleaned_data['topic_tags']
            other_tags = form.cleaned_data['other_tags']
                    
            search_type = form.cleaned_data['searchtype']
            
            # if search type is 'resources'
            if search_type == '0':
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
                        found_resources = level_resources       
                                                     
                    context_dict['results'] = found_resources
                    
                    # set flag so template knows which url to use
                    context_dict['resource'] = True
                else:
                    # if no tags are entered, do nothing
                    # template handles error message
                    pass
            
            # if search type is 'packs'
            if search_type == '1':
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
                        found_packs = level_packs       
                                                     
                    context_dict['results'] = found_packs
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
    context_dict['searched'] = searched
    
    # return response object
    return render_to_response('treasure/search.html', context_dict, context)
    
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
def edit_profile(request):
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
        user_form = UserForm(data=request.POST, instance=my_user_record)
        teacher_form = TeacherForm(data=request.POST, instance=my_teacher_record)

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
            updated = True

        # Invalid form or forms print problems to the terminal.
        else:
            print "ERROR", user_form.errors, teacher_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    else: 
        # pass the current records to initially populate the forms
        user_form = UserForm(instance = my_user_record)
        teacher_form = TeacherForm(instance = my_teacher_record)
    
    # create context dictionary
    context_dict = sidebar(request)
    context_dict['user_form'] = user_form
    context_dict['teacher_form'] = teacher_form
    context_dict['updated'] = updated
    
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
                return resource_view(request, new_resource.id)

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
    return render_to_response('treasure/user_history.html', context_dict, context)
    
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
                return HttpResponseRedirect('/treasure/')
            else:
                # An inactive account was used - no logging in!
                context_dict['disabled_account'] = "aye"
        else:
            # Bad login details were provided. So we can't log the user in.
            context_dict['bad_details'] = "aye"


    return render_to_response('treasure/login.html', context_dict, context)

# log the user out
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/treasure/')
    
    
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
            resource.evolution_type = "creation"
            
            # default values for hidden
            resource.hidden = 0
            
            # todo: restrict views
            # initially 0 for now
            resource.restricted = 0
            
            # this is a web resource
            resource.resource_type = "web"

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
            
            # Now show the new materials page
            return resource_view(request, resource.id)
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
            resource.evolution_type = "creation"
            
            # default values for hidden
            resource.hidden = 0
            
            # todo: restrict views
            # initially 0 for now
            resource.restricted = 0
            
            # this is a file resource
            resource.resource_type = "file"
            
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
            
            # show user the new materials page
            return resource_view(request, resource.id)
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
    
    # check if form is in a popup
    if ('_popup' in request.GET):
        context_dict['popup'] = True    

    # A HTTP POST?
    if request.method == 'POST':
        form = HubForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            hub = form.save(commit=True)     
            
            # if addition was in a popup
            ## This will fire the script to close the popup and update the list
            if "_popup" in request.POST:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                    (escape(hub.pk), escapejs(hub)))
            ## No popup, so return the normal response            
            return hub_view(request, hub.id)
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
    
    # check if form is in a popup
    if ('_popup' in request.GET):
        context_dict['popup'] = True

    # A HTTP POST?
    if request.method == 'POST':
        form = SchoolForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            school = form.save(commit=True)     
            
            # if addition was in a popup
            ## This will fire the script to close the popup and update the list
            if "_popup" in request.POST:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                    (escape(school.pk), escapejs(school)))
            ## No popup, so return the normal response
            return school_view(request, school.id)
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
    try:
        # Can we find a resource with the given id?
        this_resource = Resource.objects.get(id=resource_id)
        
        # get fields
        context_dict['resource_name'] = this_resource.name
        context_dict['description'] = this_resource.description
        
        # get authors name
        context_dict['author'] = this_resource.author.firstname + " " + this_resource.author.surname
        
        # check if user owns this resource
        if this_resource.author == request.user.teacher:
            context_dict['owned'] = True
            
        # get tags
        filtered_tags = this_resource.tags.filter(type='0')
        if filtered_tags:
            context_dict['level_tags'] = get_list(filtered_tags)
        
        filtered_tags = this_resource.tags.filter(type='1')
        if filtered_tags:
            context_dict['topic_tags'] = get_list(filtered_tags)
        
        filtered_tags = this_resource.tags.filter(type='2')
        if filtered_tags:
            context_dict['other_tags'] = get_list(filtered_tags)
                    
        try:
            # can we find a web resource with the given resource?
            web_resource = WebResource.objects.get(resource = this_resource)
            
            # add fields to dict
            context_dict['label'] = 'Link to Resource'
            context_dict['web_resource'] = True
            
        except WebResource.DoesNotExist:
            # do nothing
            pass
            
        try:
            # can we find a file resource with the given resource?
            files_resource = FilesResource.objects.get(resource = this_resource)
            
            # add label to dict
            context_dict['label'] = 'Download Resource'
            context_dict['files_resource'] = True
            
        except FilesResource.DoesNotExist:
            # do nothing
            pass
            
        # get packs
        context_dict['partofpacks'] = this_resource.packs.filter(name__isnull=False)

        # get interactions            
        want2talk=TeacherWantstoTalkResource.objects.all()
        context_dict['want2talk'] = want2talk.filter(resource_id=resource_id)

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
    filtered_tags = tag_list.filter(type='0')
    if filtered_tags:
        context_dict['level_tags'] = get_list(filtered_tags)
    
    filtered_tags = tag_list.filter(type='1')
    if filtered_tags:
        context_dict['topic_tags'] = get_list(filtered_tags)
    
    filtered_tags = tag_list.filter(type='2')
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
    
    # check if form is in a popup
    if ('_popup' in request.GET):
        context_dict['popup'] = True
    
    # A HTTP POST?
    if request.method == 'POST':
        form = TagForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Put off saving to avoid integrity errors.
            tag = form.save(commit=False)
            
            # only allow 'other tags' to be created using the form
            # 'levels' and 'topics' should be predefined by admins
            tag.type = '2'
            
            # now save the tag in the database
            tag.save()
                        
            # if addition was in a popup
            ## This will fire the script to close the popup and update the list
            if "_popup" in request.POST:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                    (escape(tag.pk), escapejs(tag)))
            ## No popup, so return the normal response
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
        filtered_tags = this_pack.tags.filter(type='0')
        if filtered_tags:
            context_dict['level_tags'] = get_list(filtered_tags)
        
        filtered_tags = this_pack.tags.filter(type='1')
        if filtered_tags:
            context_dict['topic_tags'] = get_list(filtered_tags)
        
        filtered_tags = this_pack.tags.filter(type='2')
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
                return pack(request, new_pack.id)

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
        
        resource_form = ResourceForm(selected_tags,request.POST)
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
                
                # todo: elaborate
                # simply 'evolution' for now
                resource.evolution_type = "evolution"
                
                #default hidden
                resource.hidden = 0
                
                # todo: implement restrictions
                # initially 0 for now
                resource.restricted = 0
                
                # set type of resource
                resource.resource_type = 'file'                
                
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
                
                # show user the new materials page
                return resource_view(request, resource.id)
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
                
                # todo: elaborate
                # simply 'evolution' for now
                resource.evolution_type = "evolution"
                
                #default hidden
                resource.hidden = 0
                
                # todo: implement restrictions
                # initially 0 for now
                resource.restricted = 0
                
                # set type of resource
                resource.resource_type = 'web'
                
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
                
                # Now show the new materials page
                return resource_view(request, resource.id)
            else:
                # The supplied form contained errors - just print them to the terminal.
                print resource_form.errors
                print web_form.errors
                context_dict['error'] = 'web'
        
    else:
        # If the request was not a POST, display the form to enter details.
        resource_form = ResourceForm(selected_tags)
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
def track(request, resource_id):
    # Request the context of the request.
    context = RequestContext(request)
    
    #create context dictionary to send back to template
    context_dict = sidebar(request)

    #todo: implement tracking
    
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
            return pack(request, this_pack.id)
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

# view for the user's history (list of all actions) page
@login_required
def download(request, resource_id):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)

    try:
        this_teacher = Teacher.objects.get(id=request.user.id)
        this_resource = get_object_or_404(Resource, id=resource_id)

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
	download_record= TeacherDownloadsResource(teacher=this_teacher, resource=this_resource, datetime=datetime.now())
	download_record.save()
    except Resource.DoesNotExist:
	# No Resource
	pass

    # Render the template updating the context dictionary.
    return redirect(url)
