from django.db import models
from django.contrib.gis.db import models

class Event(models.Model):
    number = models.CharField("Glide Number",max_length=120)
    event = models.TextField("Event",null=False)
    comment = models.TextField("Comment",null=False)
    the_geom = models.MultiPolygonField()
    
    objects = models.GeoManager()

    def __unicode__(self):
        return self.number

    class Meta:
        verbose_name_plural = "Events"

class Service(models.Model):
    SERVICE_TYPES = (
        ('OSM', 'OpenStreetMap'),
        ('USH', 'Ushahidi'),
        ('TWT', 'Twitter'))
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=3, choices=SERVICE_TYPES)
    url = models.URLField()
    
    def __unicode__(self):
        return self.name


class ServiceRecord(models.Model):
    service = models.ForeignKey(Service)
    identifier = models.IntegerField()
    user = models.CharField(max_length=100)
    title = models.CharField(max_length=140)
    text = models.TextField()
    created = models.DateTimeField()
    modified = models.DateTimeField()
    geom = models.PointField()

    objects = models.GeoManager()

    class Meta:
        abstract = True

class UshahidiCategory(models.Model):
    service = models.ForeignKey(Service) # enforce type?
    category_id = models.IntegerField()
    category_name = models.CharField(max_length=100)

class UshahidiReport(ServiceRecord):
    incident_mode = models.IntegerField(null=True, blank=True)
    incident_active = models.NullBooleanField(null=True, blank=True)
    incident_verified = models.NullBooleanField(null=True, blank=True)
    location_id = models.IntegerField(null=True, blank=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)
    person_first = models.CharField(max_length=100, null=True, blank=True)
    person_last = models.CharField(max_length=100, null=True, blank=True)
    person_email = models.EmailField(null=True, blank=True)
    incident_categories = models.ManyToManyField('UshahidiCategory')
    incident_photo = models.URLField(null=True, blank=True)
    incident_video = models.URLField(null=True, blank=True)
    incident_news = models.URLField(null=True, blank=True)

    def __unicode__(self):
        return str('%i %s' % (self.identifier, self.title))

    @property
    def categories(self):
        return ""
