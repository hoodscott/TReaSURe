from django.conf.urls import patterns, url
from treasure import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^about/', views.about, name='about'),
        
        url(r'^register/$', views.register, name='register'),
        url(r'^login/$', views.user_login, name='login'),
        url(r'^logout/$', views.user_logout, name='logout'),
        
        url(r'^profile/$', views.profile, name='profile'),
        url(r'^profile/(?P<user_id>\w+)/$', views.profile, name='profile'),
        url(r'^profile/(?P<user_id>\w+)/history/$', views.user_history, name='user_history'),
        
        url(r'^add_web_resource/$', views.add_web_resource, name='add_web_resource'),
        url(r'^add_file_resource/$', views.add_file_resource, name='add_file_resource'),
        url(r'^add_hub/$', views.add_hub, name='add_hub'),
        url(r'^add_school/$', views.add_school, name='add_school'),
        
        url(r'^resources/$', views.resources, name='resources'),
        url(r'^hubs/$', views.hubs, name='hubs'),
        url(r'^schools/$', views.schools, name='schools'),
       
        url(r'^resource/(?P<resource_id>\w+)/$', views.resource, name='resource'),
        
        url(r'^search/$', views.search, name='search'),
        )
