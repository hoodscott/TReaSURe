from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
import notifications

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_project.views.home', name='home'),
    # url(r'^django_project/', include('django_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url('', include('treasure.urls')),
    
    url('^notifications/', include('notifications.urls', namespace='notifications')),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
