from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from treasure.forms import *
from treasure.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# get the users firstname, surname and school for the sidebar
def sidebar(request):
    context_dict = {}
    
    try:
        userid = request.user.id
        teacher = Teacher.objects.get(user = userid)
        
        # get users name
        context_dict['user_firstname'] = teacher.firstname
        context_dict['user_surname'] = teacher.surname
        
        # get a school from the user, if they have any
        context_dict['user_school'] = teacher.school
            
    except Teacher.DoesNotExist:
        context_dict['user_firstname'] = ""
        context_dict['user_surname'] = ""
        context_dict['school'] = ""
    
    return context_dict
    
# function to convert many to many relation list of objects
def get_list(relation):
    objects = [relation[0]]
    i = 1
    while i < len(relation):
        objects += [relation[i]]
        i += 1
    return objects

# view for the homepage
def index(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # return response object
    return render_to_response('treasure/index.html', context_dict, context)
    

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
            tags = form.cleaned_data['tags']
            
            # initalise search results
            all_resources = Resource.objects.all()
            found_resources = all_resources.filter(tags__name=tags[0])
            
            # filter to get the matching resources
            for tag in tags:
                # logical AND the queryset fro each tag together
                found_resources = found_resources & all_resources.filter(tags__name=tag)
            
            context_dict['resources'] = found_resources
            
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
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
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
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
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
    
    # A HTTP POST?
    if request.method == 'POST':
        resource_form = ResourceForm(request.POST)
        web_form = WebForm(request.POST)

        # Have we been provided with a valid form?
        if resource_form.is_valid() and web_form.is_valid():
            # delay saving the model until we're ready to avoid integrity problems
            resource = resource_form.save(commit=False)
            
            # set foreign key of the author of the resource
            userid = request.user.id
            teacher = Teacher.objects.get(user = userid)
            resource.author = Teacher.objects.get(id = teacher.id)
            resource.save()
            
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
    else:
        # If the request was not a POST, display the form to enter details.
        resource_form = ResourceForm()
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
    
    # A HTTP POST?
    if request.method == 'POST':
        resource_form = ResourceForm(request.POST)
        file_form = FileForm(request.POST, request.FILES)

        # Have we been provided with a valid form?
        if resource_form.is_valid() and file_form.is_valid():
            # delay saving the model until we're ready to avoid integrity problems
            resource = resource_form.save(commit=False)
            
            # set foreign key of the author of the resource
            userid = request.user.id
            teacher = Teacher.objects.get(user = userid)
            resource.author = Teacher.objects.get(id = teacher.id)
            resource.save()
            
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
    else:
        # If the request was not a POST, display the form to enter details.
        resource_form = ResourceForm()
        file_form = FileForm()
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    context_dict['resource_form'] = resource_form
    context_dict['file_form'] = file_form
    
    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('treasure/add_file_resource.html', context_dict, context)
    
# view for the add hub page
@login_required
def add_hub(request):
    # get context of request
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = HubForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            hub = form.save(commit=True)     
            
            # show user the new hub page
            return hub_view(request, hub.id)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = HubForm()
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    context_dict['form']  = form
    
    # Render the form depending on context
    return render_to_response('treasure/add_hub.html', context_dict, context)
    
# view for the add users page
@login_required
def add_school(request):
    # get context of request
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = SchoolForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            school = form.save(commit=True)     
            
            # show user new school page
            return school_view(request, school.id)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = SchoolForm()
    
    # create dictionary to pass data to templates
    context_dict = sidebar(request)
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
        context_dict['level'] = this_resource.level
        
        # get authors name
        context_dict['author'] = this_resource.author.firstname + " " + this_resource.author.surname
        
        # get tags from the user, if they have any
        if len(this_resource.tags.all()) >= 1:
            # get list of school objects
            context_dict['tags'] = get_list(this_resource.tags.all())
        
        try:
            # can we find a web resource with the given resource?
            web_resource = WebResource.objects.get(resource = this_resource)
            
            # add fields to dict
            context_dict['web_resource'] = web_resource.url
            
        except WebResource.DoesNotExist:
            # do nothing
            pass
            
        try:
            # can we find a file resource with the given resource?
            files_resource = FilesResource.objects.get(resource = this_resource)
            
            # add fields to dict
            context_dict['files_resource'] = files_resource.path
            
        except FilesResource.DoesNotExist:
            # do nothing
            pass

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
    context_dict['tags'] = tag_list
    
    # Render the template depending on the context.
    return render_to_response('treasure/tags.html', context_dict, context)
    

# view to see all packs in the database
@login_required
def packs(request):
    # Request the context of the request.
    context = RequestContext(request)

    #create context dictionary to send back to template
    context_dict = sidebar(request)

    # get list of all tags
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
        
        # get resources
        context_dict['tagged_resources'] = Resource.objects.filter(tags__id=tag_id)

        # used to verify it exists
        context_dict['tag'] = this_tag
    except Hub.DoesNotExist:
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
        context_dict['Pack_Resources'] = Resource.objects.filter(packs__id=pack_id)

        # get tags from the user, if they have any
        if len(this_pack.tags.all()) >= 1:
            # get list of tag objects
            context_dict['tags'] = get_list(this_pack.tags.all())

        # used to verify it exists
        context_dict['pack'] = this_pack
    except Hub.DoesNotExist:
        # We get here if we didn't find the specified tag.
        # Don't do anything - the template displays the "no tag" message for us.
        pass
    
    # return response object
    return render_to_response('treasure/pack.html', context_dict, context)



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
