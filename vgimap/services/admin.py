from django.contrib import admin
from django.contrib.gis import admin
from vgimap.services.models import Event, Service
from vgimap.services.models import UshahidiCategory, UshahidiReport
from vgimap.services.models import TwitterPlace, TwitterUser, TwitterUrl, TwitterTweet, TwitterHashtag
from vgimap.services.models import OsmNode, OsmNodeTag, OsmWay

admin.site.register(Event,admin.OSMGeoAdmin)
admin.site.register(Service)
admin.site.register(UshahidiCategory)
admin.site.register(UshahidiReport, admin.OSMGeoAdmin)
admin.site.register(TwitterPlace, admin.OSMGeoAdmin)
admin.site.register(TwitterTweet, admin.OSMGeoAdmin)
admin.site.register(TwitterUser)
admin.site.register(TwitterUrl)
admin.site.register(TwitterHashtag)
admin.site.register(OsmNode, admin.OSMGeoAdmin)
admin.site.register(OsmNodeTag)
admin.site.register(OsmWay, admin.OSMGeoAdmin)
admin.site.register(OsmWayTag)
