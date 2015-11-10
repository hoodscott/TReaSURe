from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from treasure.forms import ResourceForm, TeacherForm, SchoolForm, HubForm
from treasure.models import *

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

# view for the add teacher page
def add_teacher(request):
    # get context of request
    context = RequestContext(request)

    
    # A HTTP POST?
    if request.method == 'POST':
        form = TeacherForm(request.POST)

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
        form = TeacherForm()
    
    # create dictionary to pass data to templates
    context_dict = {'form': form}
    
    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('treasure/add_teacher.html', context_dict, context)
    
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
