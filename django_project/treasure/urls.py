from django.conf.urls import patterns, url
from treasure import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
		url(r'^about/', views.about, name='about'),
        url(r'^search/$', views.search, name='search'),
        url(r'^resource/(?P<mresource_id>\w+)/$', views.resource, name='resource'),
        url(r'^add_resource/$', views.add_resource, name='add_resource'),
        url(r'^add_teacher/$', views.add_teacher, name='add_teacher'),
        url(r'^profile/(?P<user_id>\w+)/$', views.profile, name='profile'),
        url(r'^profile/(?P<user_id>\w+)/history/$', views.user_history, name='user_history'),
        )
