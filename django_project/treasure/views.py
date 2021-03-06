# import python functions
from datetime import datetime
from string import split, upper


# import django functions
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse,resolve
from django.db.models import Count, Min, Max, Q
from django.db.models.signals import post_save
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.utils.html import escape, escapejs
from django.utils.translation import ugettext as _
from django.utils.datastructures import MultiValueDictKeyError

# import signals from django-notifications
from notifications.signals import notify

# import forms and models of this project
from treasure.forms import *
from treasure.models import *

''' helper functions '''
# get the users teacher entry and school for the sidebar
def sidebar(request):
    context_dict = {}
    
    # this is not needed, but removing it is a pain; it is very coupled :/
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
        
    # add help table to dictionary for every page
    context_dict['all_help'] = Help.objects.all()
    
    # count up pending notifiactions for the admin
    admin_notifications = pendingVerification.objects.filter(reviewed=None).count()
    context_dict['admin_notifications'] = admin_notifications
    
    return context_dict

# convert a postcode to a lat,lon co-ordinate, returns -1 if not a valid postcode
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

# convert a many to many relationship to a list of objects
def get_list(relation):
    objects = [relation[0]]
    i = 1
    while i < len(relation):
        objects += [relation[i]]
        i += 1
    return objects
    
# initialise a blank dictionary to pass into forms
# used to preset the tags in the forms
def blank_tag_dict():
    return {'level':[], 'topic':[], 'other':[]}
    
# return a list of the current tags
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
    
# return a string of the evolution type from an integer
def convert_to_evotype(number):
    print number
    number = int(number)
    EVOLUTIONS = ['Creation', 'Amendments', 'Style', 'Translation', 'Recontext', 'New Difficulty', 'New Format']
    return EVOLUTIONS[number]
    
# get the boards of a specific type given the type
def getSubForum(board_type):
    # get all boards of this type
    boards = Board.objects.all().filter(boardtype = board_type)
    
    # adds an attribute to each board that holds the count of threads on a board
    boards = boards.annotate(num_threads = Count('thread'))
    
    # adds an attribute to each board that holds the time of the last thread creation on a board
    boards = boards.annotate(last_thread = Max('thread__datetime'))

    # adds an attribute to each board that holds the time of the last post on a board
    boards = boards.annotate(last_post = Max('thread__post__datetime'))
    
    # sort boards in reverse post order
    boards = boards.order_by('-last_post')
    
    return boards

# get a sorted list of threads on a board
# this_reousrce is the object corresponding the the board
# resource is a boolean - true if the object is a resource, false if it is a pack
def getThreads(this_resource, resource):
    if resource:
        # get the board corresponding to the resource
        this_board = Board.objects.get(resource = this_resource)
    else:
        # get the board corresponding to the pack
        this_board = Board.objects.get(pack = this_resource)
    
    # get the threads on this board
    threads = Thread.objects.filter(board = this_board)
    
    # add an attribute to each thread to hold the number of posts of each thread
    threads = threads.annotate(num_posts = Count('post'))
    
    # add an attribute to each thread to hold the time of the last post
    threads = threads.annotate(last_post = Max('post__datetime'))
    
    # sort in reverse order
    threads = threads.order_by('-datetime')
    
    return threads
    
''' end of helper functions '''

''' notification threads '''

# notification are of the form
# notify.send(object, recipient=user, verb='created', action_object=resource, description=u'', level='')

# send a "evolve" notification
def evolve_notify(resource, user, target):
    notify.send(resource, recipient=user, verb='evolved', action_object=resource, target=target)
    
# send a "download" notification
def download_notify(resource, user, level):
    notify.send(resource, recipient=user, verb='downloaded', action_object=resource, level=level)
    
# send a want2talk notification
def want2talk_notify(resource, user):
    #todo: send a user in the target field once profile pages are made
    notify.send(resource, recipient=user, verb='want2talk', action_object=resource)
    
# send a rated notification
def rated_notify(thread, user):
    #todo: send a user in the target field once profile pages are made
    notify.send(thread, recipient=user, verb='rated', action_object=thread)
    
# send a question notification
def question_notify(thread, user):
    #todo: notify when quesiton is posted
    #todo: send a user in the target field once profile pages are made
    notify.send(thread, recipient=user, verb='questioned', action_object=thread)
    
# send a discussion notification
def discussion_notify(thread, user):
    #todo: notify when a disc is started
    #todo: send a user in the target field once profile pages are made
    notify.send(thread, recipient=user, verb='discussed', action_object=thread)
    
# send a question notification
def reply_notify(thread, user):
    #todo: notify when there is a post on a thread
    #todo: send a user in the target field once profile pages are made
    notify.send(thread, recipient=user, verb='replied', action_object=thread)

# send a want2talk about a pack notification
def want2talkpack_notify(pack, user):
    #todo: send a user in the target field once profile pages are made
    notify.send(pack, recipient=user, verb='want2talkpack', action_object=pack)

''' end of notification threads '''


''' start of view funtions '''
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
    context_dict['want2talkMine'] = want2talkMine.filter(resource__author=this_teacher).filter(~Q(teacher_id = this_teacher))

    want2talkMyPacks=TeacherWantstoTalkPack.objects.all()
    context_dict['want2talkMyPacks'] = want2talkMyPacks.filter(pack__author=this_teacher).filter(~Q(teacher_id = this_teacher))
 
    want2talk=TeacherWantstoTalkResource.objects.all()
    context_dict['want2talk'] = want2talk.filter(teacher_id=this_teacher)

    want2talkPack=TeacherWantstoTalkPack.objects.all()
    context_dict['want2talkPack'] = want2talkPack.filter(teacher_id=this_teacher)
    
    iDownload=TeacherDownloadsResource.objects.all().filter(teacher=this_teacher)
    context_dict['iDownload'] = iDownload
    context_dict['need2rate'] = TeacherDownloadsResource.objects.all().filter(teacher=this_teacher, used=0)|TeacherDownloadsResource.objects.all().filter(teacher=this_teacher, rated=0)
    
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
            if teacher_form.cleaned_data['scottishTeacher']:
                pending_verification= pendingVerification(teacher=teacher, datetimeOfRequest=datetime.now())
                pending_verification.save()

            teacher.save()
            
            # return user to updated profile page
            return redirect(reverse('profile'))

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
    
    try:
        context_dict['inlist'] = pendingVerification.objects.get(teacher = my_teacher_record)
    except pendingVerification.DoesNotExist:
        # not in list
        pass
    
    context_dict['editingProfile']='yes'
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
            if teacher.verified == 0:
                form = EditResourceForm(selected_tags, data=request.POST, instance=this_resource)
            else:
                form = VerifiedEditResourceForm(selected_tags, data=request.POST, instance=this_resource)
            
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
                
                # update board related to this resource
                try:
                    this_board = Board.objects.get(resource=new_resource)
                    this_board.restricted = new_resource.restricted
                    this_board.save()
                except BoardDoesNotExistError:
                    # every resource should have a board associated
                    pass
                
                # show user the updated page
                return redirect(reverse('resource_view', args=[str(new_resource.id)]))

            # Invalid form or forms print problems to the terminal.
            else:
                print "ERROR", form.errors

        # Not a HTTP POST, so we render our form using two ModelForm instances.
        else:
            # pass the current records to initially populate the forms
            if teacher.verified == 0:
                form = EditResourceForm(selected_tags, instance=this_resource)
            else:
                form = VerifiedEditResourceForm(selected_tags, instance=this_resource)
        
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
            
            teacher.verified = 0
            teacher.datetime = datetime.now()

            # Now we save the UserProfile model instance.
            teacher.save()
            if teacher_form.cleaned_data['scottishTeacher']:
                evidence = teacher_form.cleaned_data['evidence']
                pending_verification= pendingVerification(teacher=teacher, datetimeOfRequest=datetime.now(), evidence=evidence)
                pending_verification.save()

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
def ratePack(request, pack_id):
    # get the context of request
    context = RequestContext(request)
    context_dict = sidebar(request)
    this_teacher = Teacher.objects.get(user=request.user)
    this_pack = Pack.objects.get(id=pack_id)
    try:
        condition = TeacherRatesPack.objects.get(teacher_id=this_teacher.id, pack_id=this_pack.id)
        context_dict['condition'] = condition
    except TeacherRatesPack.DoesNotExist:
            # do nothing
            pass
  
    rated = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        rating_form = PackRatingForm(request.POST)
        # If the form is valid..
        if rating_form.is_valid():
            # Save the rating to the database.
            rating=TeacherRatesPack(teacher_id=this_teacher.id,pack_id=this_pack.id,measure1=rating_form.cleaned_data['measure1'],measure2=rating_form.cleaned_data['measure2'],measure3=rating_form.cleaned_data['measure3'],comment=rating_form.cleaned_data['comment'],datetime=datetime.now())
            rating.save()
            
            # create a thread on the pack board
            this_board = Board.objects.all().get(pack=this_pack)
            thread = Thread(board = this_board, datetime = datetime.now(), author= this_teacher, title=this_teacher.firstname+' '+this_teacher.surname+' rated this pack', content=rating.comment, threadtype=0, rating_pack=rating, restricted=this_pack.restricted)
            thread.save()
            
            # update subscribers of the board
            subscribers = TeacherSubbedToBoard.objects.filter(board = this_board)
            for sub in subscribers:
                rated_notify(thread, sub.teacher.user)
                
            # sub creator to the new thread
            new_sub = TeacherSubbedToThread(teacher = this_teacher, thread = thread)
            new_sub.save()
            
            # Update our variable to tell the template registration was successful.
            rated = True

        # Invalid form or forms print problems to the terminal.
        else:
            print "ERROR", rating_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    else:
        rating_form=PackRatingForm()
    
    # create context dictionary
    context_dict['this_pack'] = this_pack
    context_dict['this_teacher'] = this_teacher
    context_dict['rating_form'] = rating_form
    context_dict['rated'] = rated

    # Render the template depending on the context.
    return render_to_response('treasure/rate_pack.html', context_dict, context)
            

         
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
            rating=TeacherRatesResource(teacher_id=this_teacher.id,resource_id=this_resource.id,measure1=rating_form.cleaned_data['measure1'],measure2=rating_form.cleaned_data['measure2'],measure3=rating_form.cleaned_data['measure3'],comment=rating_form.cleaned_data['comment'],datetime=datetime.now())
            rating.save()
            download.rated='1'
            download.save()
            
            # create a thread on the resources board
            this_board = Board.objects.all().get(resource=this_resource)
            thread = Thread(board = this_board, datetime = datetime.now(), author= this_teacher, title=this_teacher.firstname+' '+this_teacher.surname+' rated this resource', content=rating.comment, threadtype=0, rating=rating, restricted=this_resource.restricted)
            thread.save()
            
            # update subscribers of the board
            subscribers = TeacherSubbedToBoard.objects.filter(board = this_board)
            for sub in subscribers:
                rated_notify(thread, sub.teacher.user)
                
            # sub creator to the new thread
            new_sub = TeacherSubbedToThread(teacher = this_teacher, thread = thread)
            new_sub.save()
            
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

    if red=='res':
        return redirect(reverse('resource_view', args=[this_resource.id]))
    else:
        # link='/me/'
        return redirect(reverse('my_homepage'))


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
        
        # notify other users that someone wants to talk
        talking_resource = TeacherWantstoTalkResource.objects.filter(resource=this_resource)
        for relation in talking_resource:
            want2talk_notify(this_resource, relation.teacher.user)

    elif var=="no":
        try:
            wanted = TeacherWantstoTalkResource.objects.get(teacher_id=this_teacher.id, resource_id=this_resource.id)
            wanted.delete()
        except TeacherWantstoTalkResource.DoesNotExist:
            # This could never happen
            pass

    if red=='res':
        return redirect(reverse('resource_view', args=[this_resource.id]))
    else:
        # link='/me/'
        return redirect(reverse('my_homepage'))
        
def talkPack(request, pack_id, var,red="pack"):
    # get the context of request
    context = RequestContext(request)
    context_dict = sidebar(request)
    this_teacher = Teacher.objects.get(user=request.user)
    this_pack = Pack.objects.get(id=pack_id)
    teacher_school = School.objects.get(id=this_teacher.school_id)

    if var=="yes":
        talk=TeacherWantstoTalkPack(pack=this_pack, teacher=this_teacher,datetime=datetime.now(), latitude= teacher_school.latitude, longitude= teacher_school.longitude, disable=0)
        talk.save()
        
        # notify other users that someone wants to talk about this pack
        talking_pack = TeacherWantstoTalkPack.objects.filter(pack=this_pack)
        for relation in talking_pack:
            want2talkpack_notify(this_pack, relation.teacher.user)

    elif var=="no":
        try:
            wanted = TeacherWantstoTalkPack.objects.get(teacher_id=this_teacher.id, pack_id=this_pack.id)
            wanted.delete()
        except TeacherWantstoTalkResource.DoesNotExist:
            # This should never happen
            pass

    if red=='pack':
        return redirect(reverse('pack', args=[this_pack.id]))
    else:
        # link='/me/'
        return redirect(reverse('my_homepage'))

def verify(request, request_id, var):
    # get the context of request
    context = RequestContext(request)
    context_dict = sidebar(request)
    this_reviewer = Teacher.objects.get(user=request.user)
    this_request=pendingVerification.objects.get(id=request_id)
    this_requestor=this_request.teacher
    
    if request.user.is_superuser:

      if var=="yes":
          this_requestor.verified=1
          this_request.reviewer=this_reviewer.id
          this_request.reviewed=1
          this_request.datetimeOfReview=datetime.now()
          this_request.save()
          this_requestor.save()

      elif var=="no":
          this_requestor.verified=0
          this_request.reviewer=this_reviewer.id
          this_request.reviewed=1
          this_request.datetimeOfReview=datetime.now()
          this_request.save()
          this_requestor.save()

    return redirect(reverse('review_list'))
    
def review_list(request):
    context = RequestContext(request)
    context_dict = sidebar(request)
    context_dict['reviews'] = pendingVerification.objects.filter(reviewed = None)
    
    # todo check admin
    context_dict['admin'] = request.user.is_superuser
    
    return render_to_response('treasure/review_list.html', context_dict, context)
    

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
    return redirect(reverse('my_homepage'))

def talkHidePack(request, var):
    # get the context of request
    context = RequestContext(request)
    context_dict = sidebar(request)
    this_teacher = Teacher.objects.get(user=request.user)
    discuss=TeacherWantstoTalkPack.objects.all().filter(teacher=this_teacher)
    if var=="yes":
        discuss.update(disable=0)
    elif var=="no":
        discuss.update(disable=1)
    return redirect(reverse('my_homepage'))


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
                return redirect(reverse('home'))
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
    return redirect(reverse('home'))
    
    
# view for the add materials page
@login_required
def add_web_resource(request):
    # get context of request
    context = RequestContext(request)
    
    selected_tags = blank_tag_dict()
    
    userid = request.user.id
    teacher = Teacher.objects.get(user = userid)
    
    # A HTTP POST?
    if request.method == 'POST':
        if teacher.verified == 0:
            resource_form = ResourceForm(selected_tags, request.POST)
        else:
            resource_form = VerifiedResourceForm(selected_tags, request.POST)
        web_form = WebForm(request.POST)

        # Have we been provided with a valid form?
        if resource_form.is_valid() and web_form.is_valid():
            # delay saving the model until we're ready to avoid integrity problems
            resource = resource_form.save(commit=False)
            
            # set foreign key of the author of the resource
            userid = request.user.id
            teacher = Teacher.objects.get(user = userid)
            resource.author = teacher
            
            # this is a creation
            resource.evolution_type = "0"
            
            # default values for hidden
            resource.hidden = 0
            
            if teacher.verified == 0:
                # unverified teachers resources are always unrestricted
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
            board = Board(resource=resource, title=resource.name, boardtype='resource', restricted=resource.restricted)
            board.save()
            
            # sub creator to the new board
            new_sub = TeacherSubbedToBoard(teacher = teacher, board = board)
            new_sub.save()
            
            # Now show the new materials page
            return redirect(reverse('resource_view', args=[resource.id]))
        else:
            # The supplied form contained errors - just print them to the terminal.
            print resource_form.errors
            print web_form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        if teacher.verified == 0:
            resource_form = ResourceForm(selected_tags)
        else:
            resource_form = VerifiedResourceForm(selected_tags)
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
    
    userid = request.user.id
    teacher = Teacher.objects.get(user = userid)

    # A HTTP POST?
    if request.method == 'POST':
        print teacher.verified
        if teacher.verified == 0:
            resource_form = ResourceForm(selected_tags, request.POST)
        else:
            resource_form = VerifiedResourceForm(selected_tags, request.POST)
            print "verified"
        file_form = FileForm(request.POST, request.FILES)

        # Have we been provided with a valid form?
        if resource_form.is_valid() and file_form.is_valid():
            # delay saving the model until we're ready to avoid integrity problems
            resource = resource_form.save(commit=False)
            
            # set foreign key of the author of the resource
            userid = request.user.id
            teacher = Teacher.objects.get(user = userid)
            resource.author = teacher
                        
            # this is a creation
            resource.evolution_type = "0"
            
            # default values for hidden
            resource.hidden = 0
            
            if teacher.verified == 0:
                # unverified teachers resources are always unrestricted
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
            files = FilesResource(path = request.FILES['path'])
            
            # associate file resource with parent resource
            files.resource = resource
            
            # save the resource
            files.save()
            
            # create board for this resource
            board = Board(resource=resource, title=resource.name, boardtype='resource', restricted=resource.restricted)
            board.save()
            
            # sub creator to the new board
            new_sub = TeacherSubbedToBoard(teacher = teacher, board = board)
            new_sub.save()
            
            # show user the new materials page
            return redirect(reverse('resource_view', args=[resource.id]))
        else:
            # The supplied form contained errors - just print them to the terminal.
            print resource_form.errors
            print file_form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        if teacher.verified == 0:
            resource_form = ResourceForm(selected_tags)
        else:
            resource_form = VerifiedResourceForm(selected_tags)
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

                # if user came from registration page
                query = request.META['QUERY_STRING']
                if query == 'register':
                    # redirect usr back to registration page
                    return redirect(reverse('register'))
                elif query == 'editprofile':
                    # redirect usser to edit profile page
                    return redirect(reverse('edit_profile'))
                else:
                    # redirect user to new schoolpage
                    return redirect(reverse('hub_view', args=[hub.id]))
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
                
                # if user came from registration page
                query = request.META['QUERY_STRING']
                if query == 'register':
                    # redirect usr back to registration page
                    return redirect(reverse('register'))
                elif query == 'editprofile':
                    # redirect user to edit profile page
                    return redirect(reverse('edit_profile'))
                else:
                    # redirect user to new schoolpage
                    return redirect(reverse('school_view', args=[school.id]))
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
        
        # get previous versions
        changelog = []
        this_tree = this_resource.tree
        previous_versions = this_tree.split()[0].split(",")# unicode (ew)

        prev_count = 0
        
        # loop through previous versions, and pull the required data from the database
        while prev_count<len(previous_versions)-1:
            prev_resource = Resource.objects.get(id = previous_versions[prev_count])
            next_resource = Resource.objects.get(id = previous_versions[prev_count+1])
            evo_type = convert_to_evotype(next_resource.evolution_type)
            changelog += [[previous_versions[prev_count], prev_resource.name, prev_resource.summary, evo_type, next_resource.evolution_explanation]]
            prev_count += 1
        changelog += [[previous_versions[-1]]]
        
        context_dict['changelog'] = changelog
        
        # get direct evolutions
        future = []
        
        # get all future objects of this resource
        fut_objects = Resource.objects.filter(tree__startswith = this_tree).extra(select={'length':'Length(tree)'}).order_by('length')
        
        # count up all future resource (-1 aa fut objects contains this resource)
        fut_count = len(fut_objects) - 1
        
        # loop through objects and only return the direct descendants
        for i in fut_objects:
          print i.name, len(i.tree.split(',')), len(this_tree.split(','))
          print i.tree, this_tree
          if len(i.tree.split(','))==len(this_tree.split(','))+1:#only store direct descendants
            i.evo = convert_to_evotype(i.evolution_type) #duck typing (yay")
            # get count of evolutions after each descendant
            i.num_evos = Resource.objects.filter(tree__startswith = i.tree).count() - 1 # -1 removes this resouce from count
            future += [i]
        
        context_dict['future'] = future
        
        # count up occurences
        context_dict['download_count'] = TeacherDownloadsResource.objects.filter(resource = this_resource).count()
        context_dict['rating_count'] = TeacherRatesResource.objects.filter(resource = this_resource).count()
        context_dict['pack_count'] = this_resource.packs.count()
        context_dict['2talk_count'] = TeacherWantstoTalkResource.objects.filter(resource = this_resource).count()
        context_dict['version_count'] = prev_count + fut_count
        
        this_board = Board.objects.get(resource=this_resource)
        context_dict['forum_count'] = Thread.objects.filter(board = this_board).count()
        
        # get last five forum posts
        context_dict['threads'] = getThreads(this_resource, True)[:5]
        
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
                        
            # find where user came from
            query = request.META['QUERY_STRING'].split(',')
            if query[0] == 'file':
                # redirect usr back to add file page
                return redirect(reverse('add_file_resource'))
            elif query[0] == 'web':
                # redirect usser to add web page
                return redirect(reverse('add_web_resource'))
            elif query[0] == 'editresource':
                # redirect back to edit resource page for this resource
                return redirect(reverse('edit_resource', args=[query[1]]))
            elif query[0] == 'evolve':
                # redirect back to evolve page for this resource
                return redirect(reverse('evolve', args=[query[1]]))
            elif query[0] == 'pack':
                #redirect back to newpack page
                return redirect(reverse('newpack'))
            elif query[0] == 'initpack':
                #redirect back to newpackinitial page
                return redirect(reverse('newpack_initial', args=[query[1]]))
            elif query[0] == 'editpack':
                # redirect back to edit pack page
                return redirect(reverse('edit_pack', args=[query[1]]))
            else:
                # redirect user to new tag page
                return redirect(reverse('tag', args=[tag.id]))
            
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

        try:
            feedback= TeacherRatesPack.objects.all().filter(pack_id=this_pack.id)
            context_dict['feedback']=feedback
        except TeacherRatesPack.DoesNotExist:
            pass
          
        try:
            rating_exists = TeacherRatesPack.objects.get(teacher_id=request.user.teacher.id, pack_id=this_pack.id)
            context_dict['rating_exists'] = rating_exists
        except TeacherRatesPack.DoesNotExist:
            # do nothing
            pass
        try:
            iWant2Talk = TeacherWantstoTalkPack.objects.get(teacher_id=request.user.teacher.id, pack_id=this_pack.id)
            context_dict['iWant2Talk'] = iWant2Talk
        except TeacherWantstoTalkPack.DoesNotExist:
            # do nothing
            pass
        try:
            Want2Talk = TeacherWantstoTalkPack.objects.all().filter(pack_id=this_pack.id)
            context_dict['want2talk'] = Want2Talk
        except TeacherWantstoTalkPack.DoesNotExist:
            # do nothing
            pass
          
        # get last five forum posts
        context_dict['threads'] = getThreads(this_pack, False)[:5]

        # used to verify it exists
        context_dict['pack'] = this_pack
    except Pack.DoesNotExist:
        # We get here if we didn't find the specified pack.
        # Don't do anything - the template displays the "no pack" message for us.
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
            if teacher.verified == 0:
                form = EditPackForm(selected_tags, request.POST, request.FILES, instance=this_pack)
            else:
                form = VerifiedEditPackForm(selected_tags, request.POST, request.FILES, instance=this_pack)

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
                return redirect(reverse('pack', args=[new_pack.id]))

            # Invalid form or forms print problems to the terminal.
            else:
                print "ERROR", form.errors

        # Not a HTTP POST, so we render our form using two ModelForm instances.
        else:
            # pass the current records to initially populate the forms
            if teacher.verified == 0:
                form = EditPackForm(selected_tags, instance = this_pack)
            else:
                form = VerifiedEditPackForm(selected_tags, instance = this_pack)
        
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
    
    userid = request.user.id
    teacher = Teacher.objects.get(user = userid)
    
    # A HTTP POST?
    if request.method == 'POST':
        if teacher.verified == 0:
            resource_form = EvolveResourceForm(selected_tags, request.POST)
        else:
            resource_form = VerifiedEvolveResourceForm(selected_tags, request.POST)
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
                resource.author = teacher
                
                #not hidden by default
                resource.hidden = 0
                
                if teacher.verified == 0:
                    # unverified teachers resources are always unrestricted
                    resource.restricted = 0
                
                # set type of resource
                resource.resource_type = 'file'
                
                # set the time the resource was created
                resource.datetime = datetime.now()
                
                # save the resource before we add tags / set tree
                resource.save()
                
                # append new id to parents tree
                parent_resource = Resource.objects.get(id=parent_id)
                resource.tree = parent_resource.tree + u',' + unicode(resource.id)
                
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
                
                # send evolve notification
                evolve_notify(resource, parent_resource.author.user, parent_resource)
                
                # create board for this resource
                board = Board(resource=resource, title=resource.name, boardtype='resource', restricted = resource.restricted)
                board.save()
                
                # sub creator to the new board
                new_sub = TeacherSubbedToBoard(teacher = teacher, board = board)
                new_sub.save()
                
                # show user the new materials page
                return redirect(reverse('resource_view', args=[resource.id]))
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
                resource.author = teacher
                
                #not hidden by default
                resource.hidden = 0
                
                if teacher.verified == 0:
                    # unverified teachers resources are always unrestricted
                    resource.restricted = 0
                
                # set type of resource
                resource.resource_type = 'web'
                
                # set the time the resource was created
                resource.datetime = datetime.now()
                
                # save resource so that tree / tags can be set
                resource.save()
                
                # append new id to parents tree
                parent_resource = Resource.objects.get(id=parent_id)
                resource.tree = parent_resource.tree + u',' + unicode(resource.id)
                
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
                  
                # send evolve notification
                evolve_notify(resource, parent_resource.author.user, parent_resource)
                
                # create board for this resource
                board = Board(resource=resource, title=resource.name, boardtype='resource', restricted=resource.restricted)
                board.save()
                
                # sub creator to the new board
                new_sub = TeacherSubbedToBoard(teacher = teacher, board = board)
                new_sub.save()
                
                # Now show the new materials page
                return redirect(reverse('resource_view', args=[resource.id]))
            else:
                # The supplied form contained errors - just print them to the terminal.
                print resource_form.errors
                print web_form.errors
                context_dict['error'] = 'web'
        
    else:
        # If the request was not a POST, display the form to enter details.
        if teacher.verified == 0:
            resource_form = EvolveResourceForm(selected_tags)
        else:
            resource_form = VerifiedEvolveResourceForm(selected_tags)

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
    this_resource = get_object_or_404(Resource, id=resource_id)
    this_teacher = Teacher.objects.get(user=request.user)
    teacher_school = School.objects.get(id=this_teacher.school_id)
    context_dict['lat']=teacher_school.latitude
    context_dict['lng']=teacher_school.longitude
    context_dict['this_resource']=this_resource
    #Track locations
    try:
        downloaded=TeacherDownloadsResource.objects.all().filter(resource=this_resource).order_by('datetime')
        context_dict['downloaded']=downloaded
    except TeacherDownloadsResource.DoesNotExist:
        pass
    try:
        used=TeacherDownloadsResource.objects.all().filter(resource=this_resource, used=1).order_by('datetime')
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
    
    teacher = request.user.teacher
    
    # A HTTP POST?
    if request.method == 'POST':
        if teacher.verified == 0:
            form = PackForm(selected_tags, request.POST, request.FILES)
        else:
            form = VerifiedPackForm(selected_tags, request.POST, request.FILES)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Put off saving to avoid integrity errors.
            this_pack = form.save(commit=False)
            
            # do not feature every pack on treasure/explore/
            this_pack.explore = '0'
            
            # default values for hidden
            this_pack.hidden = 0
            
            if teacher.verified == 0:
                # unverified teachers packs are always unrestricted
                this_pack.restricted = 0
            
            # if this is null, choose a default image
            try:
              this_pack.image = request.FILES['image']
            except MultiValueDictKeyError:
              pass #default image TODO
            
            # add author
            this_pack.author = teacher
            this_pack.datetime = datetime.now()
            
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
            
            # create board for this pack
            board = Board(pack=this_pack, title=this_pack.name, boardtype='pack', restricted=this_pack.restricted)
            board.save()
            
            # sub creator to the new board
            new_sub = TeacherSubbedToBoard(teacher = teacher, board = board)
            new_sub.save()
                        
            # Now show the new pack page
            return redirect(reverse('pack', args=[this_pack.id]))
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        if teacher.verified == 0:
            form = PackForm(selected_tags)
        else:
            form = VerifiedPackForm(selected_tags)
    
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
    
    teacher = request.user.teacher
    
    # A HTTP POST?
    if request.method == 'POST':
        if teacher.verified == 0:
            form = PackForm(selected_tags, request.POST, request.FILES)
        else:
            form = VerifiedPackForm(selected_tags, request.POST, request.FILES)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Put off saving to avoid integrity errors.
            this_pack = form.save(commit=False)
            
            # do not feature every pack on treasure/explore/
            this_pack.explore = '0'
            
            # default values for hidden
            this_pack.hidden = 0
            
            if teacher.verified == 0:
                # unverified teachers packs are always unrestricted
                this_pack.restricted = 0
            
            # if this is null, choose a default image
            try:
              this_pack.image = request.FILES['image']
            except MultiValueDictKeyError:
              pass #default image TODO
            
            # add author
            this_pack.author = teacher
            this_pack.datetime = datetime.now()
            
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
            
            # create board for this pack
            board = Board(pack=this_pack, title=this_pack.name, boardtype='pack', restricted=this_pack.restricted)
            board.save()
            
            # sub creator to the new board
            new_sub = TeacherSubbedToBoard(teacher = teacher, board = board)
            new_sub.save()
                        
            # Now show the new pack page
            return redirect(reverse('pack', args=[this_pack.id]))
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        if teacher.verified == 0:
            form = PackForm(selected_tags)
        else:
            form = VerifiedPackForm(selected_tags)
    
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
            url='/plancsharing/secret/'+str(res.path)
        except FilesResource.DoesNotExist:
            # Not a FilesResource
            pass
        
        # Saving Download Record in the Database
        try:
            downloaded= TeacherDownloadsResource.objects.get(teacher=this_teacher, resource=this_resource)
        except TeacherDownloadsResource.DoesNotExist:
            download_record= TeacherDownloadsResource(teacher=this_teacher, resource=this_resource, datetime=datetime.now(), latitude= teacher_school.latitude, longitude= teacher_school.longitude, used=0, rated=0)
            download_record.save()
        
        
        # notify creator that there has been a download
        num_downloads = TeacherDownloadsResource.objects.filter(resource=this_resource).count()
        if num_downloads == 1:
            download_notify(this_resource, this_resource.author.user, '.')
        elif num_downloads % 10 == 0:
            download_notify(this_resource, this_resource.author.user, ' '+str(num_downloads)+'times.')
    
    except Resource.DoesNotExist:
        # No Resource
        pass
    
    print url
    if bypass==0:
        # IfDownload Resource
        return redirect(url)
    else:
        return redirect(reverse('rate', args=[resource_id]))

@login_required
def newSocialAuthentication(request):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)

    try:
        his = request.user
        new_teacher = Teacher(user_id=his.id, firstname=his.first_name, surname=his.last_name)
        new_teacher.datetime = datetime.now()
        new_teacher.verified = 0
        new_teacher.save()
    except Teacher.DoesNotExist:
            # Not a WebResource
            pass

    # Render the template updating the context dictionary.
    return redirect(reverse('edit_profile', args=['soc']))


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
    records=Help.objects.all()
    context_dict['help']=records
    
    # Render the template updating the context dictionary.
    return render_to_response('treasure/help.html', context_dict, context)

# view to show overview of all boards
@login_required
def forum(request):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # get the boards, separated by type (only last 10)
    context_dict['level_boards'] = getSubForum('level')[:10][::-1]
    context_dict['general_boards'] = getSubForum('general')[:10][::-1]
    context_dict['resource_boards'] = getSubForum('resource')[:10][::-1]
    context_dict['pack_boards'] = getSubForum('pack')[:10][::-1]
    
    # set main forum flag so we can reuse the template
    context_dict['main_forum'] = True
    
    # Render the template updating the context dictionary.
    return render_to_response('treasure/forum.html', context_dict, context)
    
# view to show overview of all boards
@login_required
def forum_type(request, board_type):
    # get context of request
    context = RequestContext(request)
    
    print board_type

    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # concatenate the type of board and the string _boards
    string_for_template = board_type + '_boards'
    
    # put some boards in the dict with the above key
    context_dict[string_for_template] = getSubForum(board_type)
    print string_for_template
    
    # concatenate the type of board with
    datatable_string = board_type + 'BoardTable'
    
    # add this to the datatable key in the dict
    context_dict['datatable'] = datatable_string
    
    # Render the template updating the context dictionary.
    return render_to_response('treasure/forum.html', context_dict, context)
   
# view to show board
@login_required
def board(request, board_type, board_url):
  
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # add url to contextdict
    context_dict['board_url']=board_url
    context_dict['board_type']=board_type
    
    userid = request.user.id
    teacher = Teacher.objects.get(user = userid)
    
    #determine if other or resourceboard or pack board
    if board_type == 'resource':
        try:
            # check resource has a forum attached
            this_resource = Resource.objects.get(id=board_url)
            context_dict['resource'] = this_resource
            this_board = Board.objects.all().get(resource = this_resource)
            context_dict['board'] = this_board
            if TeacherSubbedToBoard.objects.filter(board=this_board, teacher = teacher).first():
                context_dict['subscribed'] = True
            try:
                # get the threads on the forum, along with the count of posts and time of last post for each thread
                board = Thread.objects.filter(board = this_board).annotate(num_posts = Count('post'), last_post = Max('post__datetime'))
                context_dict['threads'] = board

            except Thread.DoesNotExist:
                # do not pass a board object to template as there are no threads
                print "no threads", board_url
                pass
        except Resource.DoesNotExist:
             # no board here
            context_dict['invalid'] = True
    elif board_type == 'pack':
        try:
            # check board has a forum attached
            this_pack = Pack.objects.get(id=board_url)
            context_dict['pack'] = this_pack
            this_board = Board.objects.all().get(pack = this_pack)
            context_dict['board'] = this_board
            if TeacherSubbedToBoard.objects.filter(board=this_board, teacher = teacher).first():
                context_dict['subscribed'] = True
            try:
                # get the threads on the forum, along with the count of posts and time of last post for each thread
                board = Thread.objects.all().filter(board = this_board).annotate(num_posts = Count('post'), last_post = Max('post__datetime'))
                context_dict['threads'] = board

            except Thread.DoesNotExist:
                # do not pass a board object to template as there are no threads
                print "no threads", board_url
                pass
        except Pack.DoesNotExist:
             # no board here
            context_dict['invalid'] = True
    else:
        try:
            # check the word has a url attached
            this_board = Board.objects.all().get(id=board_url)
            context_dict['board'] = this_board
            context_dict['title'] = this_board.title
            if TeacherSubbedToBoard.objects.filter(board=this_board, teacher = teacher).first():
                context_dict['subscribed'] = True
            try:
                # get the threads on the forum, along with the count of posts and time of last post for each thread
                board = Thread.objects.all().filter(board = this_board).annotate(num_posts = Count('post'), last_post = Max('post__datetime'))
                context_dict['threads'] = board
            except Thread.DoesNotExist:
                # do not pass a board object to template as there are no threads
                print "no threads", board_url
                pass
        except Board.DoesNotExist:
            context_dict['invalid'] = True
    
    # Render the template updating the context dictionary.
    return render_to_response('treasure/board.html', context_dict, context)

# view to create a new thread
@login_required
def new_thread(request, board_type, board_url):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # add board url to dict
    context_dict['board_url'] = board_url
    context_dict['board_type'] = board_type
    
    teacher = request.user.teacher
    
    # check board_url coresponds to a board
    if board_type == "resource":
        try:
            # if url is number, get board relating to that object
            this_board = Board.objects.all().get(resource = Resource.objects.all().get(id=board_url))
        except (Board.DoesNotExist, Resource.DoesNotExist) as e:
            # no board at this url
            context_dict['invalid'] = "invalid"
    elif board_type == 'pack':
        try:
            # if url is number, get board relating to that object
            this_board = Board.objects.all().get(pack = Pack.objects.all().get(id=board_url))
        except (Board.DoesNotExist, Pack.DoesNotExist) as e:
            # no board at this url
            context_dict['invalid'] = "invalid"
    else:
        try:
            # otherwise get board associated with the word
            this_board = Board.objects.all().get(id=board_url)
        except Board.DoesNotExist:
            # no board at this url
            context_dict['invalid'] = "invalid"
    
    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # pass in instance of the record to be updated
        if teacher.verified == 0:
            form = PostThreadForm(request.POST)
        else:
            form = VerifiedPostThreadForm(request.POST)

        # If the form is valid...
        if form.is_valid():
            # hold off on saving to avoid integrity errors.
            new_thread = form.save(commit=False)
            
            # get board
            # check if url is a number
            if board_type == 'resource':
                try:
                    # if url is number, get board relating to that object
                    this_board = Board.objects.all().get(resource = Resource.objects.all().get(id=board_url))
                except Board.DoesNotExist:
                    # no board at this url
                    context_dict['invalid'] = 'invalid'
            if board_type == 'pack':
                try:
                    # if url is number, get board relating to that object
                    this_board = Board.objects.all().get(pack = Pack.objects.all().get(id=board_url))
                except Board.DoesNotExist:
                    # no board at this url
                    context_dict['invalid'] = 'invalid'
            else:
                try:
                    # otherwise get board associated with the id
                    this_board = Board.objects.all().get(id=board_url)
                except Board.DoesNotExist:
                    # no board at this url
                    context_dict['invalid'] = 'invalid'
            new_thread.board = this_board
            
            # set author
            new_thread.author = teacher
            
            # set time of threadposting
            new_thread.datetime = datetime.now()
            
            if teacher.verified == 0:
                # unverified teachers resources are always unrestricted
                new_thread.restricted = 0
            
            # save the new resource
            new_thread.save()
            
            # sub creator to the new thread
            new_sub = TeacherSubbedToThread(teacher = teacher, thread = new_thread)
            new_sub.save()
            
            # update subscribers of the board
            subscribers = TeacherSubbedToBoard.objects.filter(board = this_board)
            if new_thread.threadtype == '1':#question
                for sub in subscribers:
                    question_notify(new_thread, sub.teacher.user)
            elif new_thread.threadtype == '2':#discussion
                for sub in subscribers:
                    discussion_notify(new_thread, sub.teacher.user)
            
            # show user the updated page
            return redirect(reverse('thread', args=[board_type, board_url, new_thread.id]))

        # Invalid form or forms print problems to the terminal.
        else:
            print "ERROR", form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    else:
        # pass the current records to initially populate the forms
        if teacher.verified == 0:
            form = PostThreadForm()
        else:
            form = VerifiedPostThreadForm()
    
    context_dict['form'] = form
    
    # Render the template updating the context dictionary.
    return render_to_response('treasure/new_thread.html', context_dict, context)

# view to show thread
@login_required
def thread(request, board_type, board_url, thread_id):
    # get context of request
    context = RequestContext(request)

    # create dictionary to pass data to templates
    context_dict = sidebar(request)
    
    # pass url to form
    # add board url to dict
    context_dict['board_url'] = board_url
    context_dict['board_type'] = board_type
    context_dict['thread_id'] = thread_id
    
    teacher = Teacher.objects.all().get(user = request.user)
        
    # get thread
    try:
        this_thread = Thread.objects.all().get(id=thread_id)
        context_dict['thread'] = this_thread
        
        # check if user is subbed
        if TeacherSubbedToThread.objects.filter(thread=this_thread, teacher = teacher).first():
            context_dict['subscribed'] = True
            
        # add posts to contextdict
        the_posts = Post.objects.all().filter(thread = this_thread)
        context_dict['posts'] = the_posts
        
        # check url is properly formed
        # (thread id belongs to the object pointed to by board_url)
        # first get board from url
        if board_type == "resource":
            try:
                # if url is number, get board relating to that object
                this_board = Board.objects.all().get(resource = Resource.objects.get(id=board_url))
            except (Board.DoesNotExist, Resource.DoesNotExist) as e:
                # no board at this url
                context_dict['invalid'] = "invalid"
        elif board_type == "pack":
            try:
                # if url is number, get board relating to that object
                this_board = Board.objects.all().get(pack = Pack.objects.get(id=board_url))
            except (Board.DoesNotExist, Pack.DoesNotExist) as e:
                # no board at this url
                context_dict['invalid'] = "invalid"
        else:
            try:
                # otherwise get board associated with the id
                this_board = Board.objects.all().get(id=board_url)
            except Board.DoesNotExist:
                # no board at this url
                context_dict['invalid'] = "invalid"
        # then check that thread is part of this board
        if this_thread.board != this_board:
            context_dict['invalid'] = "invalid"
            
        # get title of board for breadcrumbs
        context_dict['board_title'] = this_board.title
    except Thread.DoesNotExist:
        # do not pass a thread object to the template
        context_dict['board_title'] = "this"
        
    
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
            
            this_thread = Thread.objects.all().get(id = thread_id)
            new_post.thread = this_thread
            
            # set author
            new_post.author = teacher
            
            # set time of threadposting
            new_post.datetime = datetime.now()
                            
            # save the new resource
            new_post.save()
            
            # update subscribers of the new post
            subscribers = TeacherSubbedToThread.objects.filter(thread = this_thread)
            for sub in subscribers:
                reply_notify(this_thread, sub.teacher.user)
                
            # check if poster is already subbed
            if not TeacherSubbedToThread.objects.filter(thread=this_thread, teacher = teacher).first():
                # sub poster to the thread
                new_sub = TeacherSubbedToThread(teacher = teacher, thread = this_thread)
                new_sub.save()

            # show user the updated page
            return redirect(reverse('thread', args=[board_type, board_url, this_thread.id]))

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
    
# view to subscribe user to board
@login_required
def sub_board(request, board_type, board_url):
    
    userid = request.user.id
    teacher = Teacher.objects.get(user = userid)
    
    #determine if other or resourceboard or packboard
    if board_type == 'resource':
        try:
            # check resource has a forum attached
            this_resource = Resource.objects.all().get(id=board_url)
            this_board = Board.objects.all().get(resource = this_resource)
            
            # check if poster is already subbed
            if not TeacherSubbedToBoard.objects.filter(board=this_board, teacher = teacher).first():
                # sub user to the board
                new_sub = TeacherSubbedToBoard(teacher = teacher, board = this_board)
                new_sub.save()
            else:
                print 'already subbed error'
            
        except Resource.DoesNotExist:
            # no board to sub to
            print "no board to sub to"
    elif board_type == 'pack':
        try:
            # check pack has a forum attached
            this_pack = Pack.objects.all().get(id=board_url)
            this_board = Board.objects.all().get(pack = this_pack)
            
            # check if poster is already subbed
            if not TeacherSubbedToBoard.objects.filter(board=this_board, teacher = teacher).first():
                # sub user to the board
                new_sub = TeacherSubbedToBoard(teacher = teacher, board = this_board)
                new_sub.save()
            else:
                print 'already subbed error'
            
        except Pack.DoesNotExist:
            # no board to sub to
            print "no board to sub to"
    else:
        try:
            # check the word has a url attached
            this_board = Board.objects.all().get(id=board_url)
            
            # check if poster is already subbed
            if not TeacherSubbedToBoard.objects.filter(board=this_board, teacher = teacher).first():
                # sub user to the board
                new_sub = TeacherSubbedToBoard(teacher = teacher, board = this_board)
                new_sub.save()
            else:
                print 'already subbed error'
            
        except Board.DoesNotExist:
            context_dict['invalid'] = True
    
    # return user to whence they came
    return redirect(reverse('board', args=[board_type, board_url]))
    
# view to unsubscribe user to board
@login_required
def unsub_board(request, board_type, board_url):
    
    userid = request.user.id
    teacher = Teacher.objects.get(user = userid)
    
    #determine if other or resourceboard or packboard
    if board_type == 'resource':
        try:
            # check resource has a forum attached
            this_resource = Resource.objects.all().get(id=board_url)
            this_board = Board.objects.all().get(resource = this_resource)
            
            old_sub = TeacherSubbedToBoard.objects.filter(teacher = teacher, board = this_board).first()
            if old_sub:
                old_sub.delete()
            
        except Resource.DoesNotExist:
            # no board to sub to
            print "noboard to sub to"
    elif board_type == 'pack':
        try:
            # check pack has a forum attached
            this_pack = Pack.objects.all().get(id=board_url)
            this_board = Board.objects.all().get(pack = this_pack)
            
            old_sub = TeacherSubbedToBoard.objects.filter(teacher = teacher, board = this_board).first()
            if old_sub:
                old_sub.delete()
            
        except Pack.DoesNotExist:
            # no board to sub to
            print "noboard to sub to"
    else:
        try:
            # check the word has a url attached
            this_board = Board.objects.all().get(id=board_url)
            
            old_sub = TeacherSubbedToBoard.objects.filter(teacher = teacher, board = this_board).first()
            if old_sub:
                old_sub.delete()
            
        except Board.DoesNotExist:
            context_dict['invalid'] = True
    
    # return user to whence they came
    return redirect(reverse('board', args=[board_type, board_url]))

# view to sub user to a thread
@login_required
def sub_thread(request, board_type, board_url, thread_id):
    
    teacher = Teacher.objects.all().get(user = request.user)
    
    # get thread
    try:
        this_thread = Thread.objects.all().get(id=thread_id)

        # check if poster is already subbed
        if not TeacherSubbedToThread.objects.filter(thread=this_thread, teacher = teacher).first():
            # sub user to the board
            new_sub = TeacherSubbedToThread(teacher = teacher, thread = this_thread)
            new_sub.save()
        else:
            print 'already subbed error'
    except Thread.DoesNotExist:
        # can't sub to nothing
        pass
      
    # show user the updated page
    return redirect(reverse('thread', args=[board_type, board_url, this_thread.id]))
    
# view to un sub a teacher from a thread
# view to sub user to a thread
@login_required
def unsub_thread(request, board_type, board_url, thread_id):
    
    teacher = Teacher.objects.all().get(user = request.user)
    
    # get thread
    try:
        this_thread = Thread.objects.all().get(id=thread_id)
        # unsub user to thread
        old_sub = TeacherSubbedToThread.objects.filter(teacher = teacher, thread = this_thread).first()
        if old_sub:
            old_sub.delete()
    except Thread.DoesNotExist:
        # can't sub to nothing
        pass
      
    # show user the updated page
    return redirect(reverse('thread', args=[board_type, board_url, this_thread.id]))
    
    

''' end of view functions '''