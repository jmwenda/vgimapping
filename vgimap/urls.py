from django.conf.urls import patterns, include, url
from ga_ows.views.wfs import WFS
from vgimap.services.wfs import TwitterWFSAdapter
from vgimap.services import models as m
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'vgimap.views.home', name='home'),
    # url(r'^vgimap/', include('vgimap.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^wfs/?', WFS.as_view(
        models=[m.Event, m.UshahidiReport, m.TwitterTweet, m.TwitterPlace], # everything but this is optional.
    )),
    url(r'^twitter_wfs/?', WFS.as_view(adapter=TwitterWFSAdapter())),
    #url(r'^search/', include('haystack.urls')),
    url(r'^search/','vgimap.services.views.search'),
    url(r'^opensearch/','vgimap.services.views.opensearch')
)
