from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from treasure.forms import *
from treasure.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# view for the homepage
def index(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = {}
    
    # return response object
    return render_to_response('treasure/index.html', context_dict, context)
    

# view for the about page
def about(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = {}
    
    # return response object
    return render_to_response('treasure/about.html', context_dict, context)
    
    
# view for the search page
def search(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = {}
    
    # return response object
    return render_to_response('treasure/search.html', context_dict, context)
    
    
# view for the page for each resource
def resource(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = {}
    
    # return response object
    return render_to_response('treasure/resource.html', context_dict, context)
    
    
# view for the add materials page
def add_resource(request):
    # get context of request
    context = RequestContext(request)
    
    # A HTTP POST?
    if request.method == 'POST':
        form = ResourceForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)     
            
            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = ResourceForm()
    
    # create dictionary to pass data to templates
    context_dict = {'form': form}
    
    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('treasure/add_resource.html', context_dict, context)
    
# view for the user's profile page
def profile(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = {}
    
    # return response object
    return render_to_response('treasure/profile.html', context_dict, context)
    
    
# view for the user's history (list of all actions) page
def user_history(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = {}
    
    # return response object
    return render_to_response('treasure/user_history.html', context_dict, context)
    
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
            form.save(commit=True)     
            
            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = HubForm()
    
    # create dictionary to pass data to templates
    context_dict = {'form': form}
    
    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
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
            form.save(commit=True)     
            
            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = SchoolForm()
    
    # create dictionary to pass data to templates
    context_dict = {'form': form}
    
    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('treasure/add_school.html', context_dict, context)
    
# register user
def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and teacherForm.
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

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            teacher = teacher_form.save(commit=False)
            teacher.user = user

            # Now we save the UserProfile model instance.
            teacher.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, teacher_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        teacher_form = TeacherForm()
        

    # Render the template depending on the context.
    return render_to_response(
            'treasure/register.html',
            {'user_form': user_form, 'teacher_form': teacher_form, 'registered': registered},
            context)
            
         
def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

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
        return render_to_response('treasure/login.html', {}, context)

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/treasure/')
