from django.contrib import admin
from django.contrib.gis import admin
from vgimap.services.models import Event, Service, UshahidiCategory, UshahidiReport

admin.site.register(Event,admin.OSMGeoAdmin)
admin.site.register(Service)
admin.site.register(UshahidiCategory)
admin.site.register(UshahidiReport, admin.OSMGeoAdmin)
