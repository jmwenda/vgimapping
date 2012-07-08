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
    identifier = models.BigIntegerField()
    user = models.CharField(max_length=100)
    title = models.CharField(max_length=140, null=True, blank=True)
    text = models.TextField()
    created = models.DateTimeField()
    modified = models.DateTimeField(null=True, blank=True)
    geom = models.PointField(null=True, blank=True)

    objects = models.GeoManager()

    class Meta:
        abstract = True

# Ushahidi Classes

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


# Twitter Classes

class TwitterPlace(models.Model):
    # https://dev.twitter.com/docs/api/1/get/geo/id/%3Aplace_id
    identifier = models.CharField(max_length=100)
    bounding_box = models.PolygonField(null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    geom = models.PolygonField(null=True, blank=True)
    place_type = models.CharField(max_length=20, null=True, blank=True)
    polylines = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=2, null=True, blank=True)
    attributes = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    contained_within = models.ForeignKey('TwitterPlace', null=True, blank=True)
    
    objects = models.GeoManager()
    
    def __unicode__(self):
        return str('%s %s' % (self.identifier, self.name))


class TwitterUser(models.Model):
    identifier = models.IntegerField()
    screen_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    lang = models.CharField(max_length=20, null=True, blank=True)
    time_zone = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    profile_image_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    utc_offset = models.IntegerField(null=True, blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    verified = models.BooleanField(default=False)
    geo_enabled = models.BooleanField(default=False)
    notifications = models.BooleanField(default=False)
    friends_count = models.PositiveIntegerField(default=0)
    statuses_count = models.PositiveIntegerField(default=0)
    # Much More
   
    def __unicode__(self):
        return str(self.screen_name)

class TwitterHashtag(models.Model):
    hashtag = models.CharField(max_length=140) 

    def __unicode__(self):
        return self.hashtag 


class TwitterUrl(models.Model):
    orig_url = models.URLField(max_length=1000)
    short_url = models.URLField(max_length=140, null=True, blank=True)

    def __unicode__(self):
        return self.orig_url


class TwitterTweet(ServiceRecord):
    place = models.ForeignKey(TwitterPlace, null=True, blank=True)
    twitter_user = models.ForeignKey(TwitterUser, null=True, blank=True, related_name='twitter_user')
    hashtags = models.ManyToManyField(TwitterHashtag, null=True, blank=True)
    mentions = models.ManyToManyField(TwitterUser, null=True, blank=True, related_name='mentions')
    urls = models.ManyToManyField(TwitterUrl, null=True, blank=True)
    contributors = models.ManyToManyField(TwitterUser, null=True, blank=True, related_name='contributors')
    favorited = models.NullBooleanField()
    possibly_sensitive = models.NullBooleanField()
    retweeted = models.NullBooleanField()
    retweet_count = models.PositiveIntegerField(null=True, blank=True)
    source = models.ForeignKey(TwitterUser, null=True, blank=True, related_name='source')
    truncated = models.NullBooleanField()
    annotations = models.TextField(null=True, blank=True)
    in_reply_to = models.ForeignKey(TwitterUser, null=True, blank=True, related_name='in_reply_to')
    in_reply_to_status_id = models.ForeignKey('TwitterTweet', null=True, blank=True)

    def __unicode__(self):
        return str("%s : %s" % (self.user, self.text))
