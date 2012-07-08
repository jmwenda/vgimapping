from django.contrib import admin
from django.contrib.gis import admin
from vgimap.myplaces.models import event

admin.site.register(event,admin.GeoModelAdmin)
