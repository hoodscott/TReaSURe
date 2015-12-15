from django.conf.urls import patterns, url
from treasure import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^about/', views.about, name='about'),
        
        url(r'^register/$', views.register, name='register'),
        url(r'^login/$', views.user_login, name='login'),
        url(r'^logout/$', views.user_logout, name='logout'),
        
        url(r'^profile/$', views.profile, name='profile'),
        url(r'^profile/edit/$', views.edit_profile, name='edit_profile'),
        
        url(r'^add_web_resource/$', views.add_web_resource, name='add_web_resource'),
        url(r'^add_file_resource/$', views.add_file_resource, name='add_file_resource'),
        url(r'^add_hub/$', views.add_hub, name='add_hub'),
        url(r'^add_school/$', views.add_school, name='add_school'),
        
        url(r'^resources/$', views.resources, name='resources'),
        url(r'^hubs/$', views.hubs, name='hubs'),
        url(r'^schools/$', views.schools, name='schools'),
       
        url(r'^resource/(?P<resource_id>\w+)/$', views.resource_view, name='resource_view'),
        url(r'^resource/(?P<resource_id>\w+)/versions/$', views.versions, name='versions'),
        url(r'^resource/(?P<resource_id>\w+)/evolve/$', views.evolve, name='evolve'),
        url(r'^resource/(?P<resource_id>\w+)/track/$', views.track, name='track'),
        url(r'^resource/(?P<resource_id>\w+)/addtopack/$', views.addtopack, name='addtopack'),
        
        url(r'^hub/(?P<hub_id>\w+)/$', views.hub_view, name='hub_view'),
        url(r'^school/(?P<school_id>\w+)/$', views.school_view, name='school_view'),
        
        url(r'^tags/$', views.tags, name='tags'),
        url(r'^tags/new/$', views.add_tag, name='add_tag'),
        url(r'^tags/(?P<tag_id>\w+)/$', views.tag, name='tag'),
        
        url(r'^packs/$', views.packs, name='packs'),
        url(r'^packs/new/$', views.newpack, name='newpack'),
        url(r'^packs/(?P<pack_id>\w+)/$', views.pack, name='pack'),
        
        url(r'^explore/$', views.explore, name='explore'),
                
        url(r'^search/$', views.search, name='search'),
        
        #url(r'^profile/(?P<user_id>\w+)/$', views.profile, name='profile'),
        #url(r'^profile/(?P<user_id>\w+)/history/$', views.user_history, name='user_history'),
        
        )
