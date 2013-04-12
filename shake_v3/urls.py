from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from termsheetrater.models import TermFields, TermChoices
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),
    (r'^$', 'termsheetrater.views.upload'),
    (r'^termsheet/$', 'termsheetrater.views.index'),
    (r'^result/$', 'termsheetrater.views.result'),
    (r'^reset/$', 'termsheetrater.views.reset_tables'),
    (r'^upload/$', 'termsheetrater.views.upload'),
    (r'^demo/$', 'termsheetrater.views.demo'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.STATIC_ROOT}),
   

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
)
