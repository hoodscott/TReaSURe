from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect

# view for the homepage
def index(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = {}
    print "here"
    
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
    
    
# view for the page for each material
def material(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = {}
    
    # return response object
    return render_to_response('treasure/material.html', context_dict, context)
    
    
# view for the add materials page
def add_material(request):
    # get context of request
    context = RequestContext(request)
    
    # create dictionary to pass data to templates
    context_dict = {}
    
    # add name of material to dict
    context_dict['material_name'] = 'Test Material'
    
    # return response object
    return render_to_response('treasure/add_materials.html', context_dict, context)
    
    
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