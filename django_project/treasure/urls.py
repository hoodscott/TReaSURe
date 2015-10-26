from django.conf.urls import patterns, url
from treasure import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
		url(r'^about/', views.about, name='about'),
        url(r'^search/$', views.search, name='search'),
        url(r'^material/(?P<material_id>\w+)/$', views.material, name='material'),
        url(r'^add_material/$', views.add_material, name='add_material'),
        url(r'^profile/(?P<user_id>\w+)/$', views.profile, name='profile'),
        url(r'^profile/(?P<user_id>\w+)/history/$', views.user_history, name='user_history'),
        )