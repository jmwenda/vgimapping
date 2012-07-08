from django.conf.urls import patterns, include, url
from ga_ows.views.wfs import WFS
from vgimapping.myplaces import models as m

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'vgimapping.views.home', name='home'),
    # url(r'^vgimapping/', include('vgimapping.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^wfs/?', WFS.as_view(
        models=[m.event], # everything but this is optional.
    )),
)
