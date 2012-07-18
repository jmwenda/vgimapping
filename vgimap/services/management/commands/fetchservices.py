from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from optparse import make_option
from vgimap.services.models import Service,UshahidiReport,UshahidiCategory
from vgimap.services.models import TwitterPlace,TwitterUser,TwitterTweet
import requests
from urlparse import urljoin
import json
import datetime
import twitter

extract = lambda keys, dict: reduce(lambda x, y: x.update({y[0]:y[1]}) or x,
                                            map(None, keys, map(dict.get, keys)), {})
right_now = datetime.datetime.utcnow()
def get_response(url):
    "This hits the api identified by the service and returns the response"
    try:
	req = requests.get(url)
        return req
    except requests.exceptions.ConnectionError, e:
        return e
def update_categories(categories,service):
    created_categories = []
    for category in categories:
        category,created = UshahidiCategory.objects.get_or_create(service=service,category_id=category['category']['id'],category_name=category['category']['title'])
        created_categories.append(category)
    return created_categories
def update_reports(incident,service,categories):
    incident,created = UshahidiReport.objects.get_or_create(service=service,identifier=incident['incident']['incidentid'],incident_mode = incident['incident']['incidentmode']
       ,created = right_now
       ,incident_active = incident['incident']['incidentactive']
       ,incident_verified = incident['incident']['incidentverified']
       ,location_id = incident['incident']['locationid']
       ,text = incident['incident']['incidentdescription']
       ,title = incident['incident']['incidenttitle']
       ,geom = Point(float(incident['incident']['locationlongitude']), float(incident['incident']['locationlatitude']))
       ,location_name = incident['incident']['locationname']
       ,person_first = None
       ,person_last = None
       ,person_email = None
       ,incident_photo = None
       ,incident_video = None
       ,incident_news = None)
    incident.incident_categories.add(*categories)
    return incident
def store_twitteruser(screen_name):
    api = twitter.Api()
    user = api.GetUser(screen_name)
    #we now create a twitter user for the vgiproject
    twitter_user,created = TwitterUser.objects.get_or_create(identifier=user.id,screen_name=user.screen_name,
    name = user.name,
    location = user.location,
    url = user.url,
    lang = user.lang,
    #time_zone = user.time_zone,
    description = user.description,
    profile_image_url = user.profile_image_url,
    #created_at = user.created_at,
    utc_offset = user.utc_offset,
    followers_count = user.followers_count,
    verified = user.verified,
    geo_enabled = user.geo_enabled,
    #notifications = user.notifications,
    friends_count = user.friends_count,
    statuses_count = user.statuses_count
    )
    return twitter_user
def process_hashtags(hashtags):
    if hashtags is not None:
       for hashtag in hashtags:
           hashtag = TwitterHashtag.objects.get_create(hashtag=hashtag.hashtag)
    return hashtags
def process_urls(urls):
    if urls is not None:
       for url in urls:
           url = TwitterUrl.objects.get_create(orig_url=url.orig_url,short_url=url.short_url)
    return urls
def process_tweet(status,place_id,service):
    place = TwitterPlace.objects.get(identifier=place_id)
    user = TwitterUser.objects.get(screen_name=status.user.screen_name)
    geom = Point(float(status.geo['coordinates'][1]), float(status.geo['coordinates'][0]))
    #import pdb;pdb.set_trace()
    twitter_tweet = TwitterTweet.objects.get_or_create(service=service,place=place,twitter_user=user,
    identifier = status.id,created=right_now,user = user.screen_name,text=status.text,geom = geom
    )
    #import pdb;pdb.set_trace()
    return twitter_tweet
def fetch_service():
    #we get a list of services  to query,for a start just ushahidi, will add the other services as we progress
    #services = Service.objects.all()
    services = Service.objects.filter(type='TWT')
    service_response = []
    for service in services:
        if service.type == 'USH':
            url = urljoin(service.url,'api?task=incidents') 
            response = get_response(url)
            data = response.json
            indicents = data['payload']['incidents']
            for incident in indicents:
               #to get the incident details use the dict 'incident' and categories use 'categories'
               incident_categories = incident['categories']
               categories = update_categories(incident_categories,service)
               update_reports(incident,service,categories)
               
            if response is not None:
                service_response.append(response)
        if service.type == 'TWT':
            #import the twitter functions here
            api = twitter.Api()
            #we get the places from the places we are tracking
            places = TwitterPlace.objects.all()
            for place in places:
                #we perfrom a search using the place id
                place_id = place.identifier
                api = twitter.Api()
                searchresult = api.GetSearch("place:"+place_id)
                for status in searchresult:
                    screen_name = status.user.screen_name
                    user = store_twitteruser(screen_name)
                    #with the new user we inspect the tweet to store hashtags and urls in the tweet
                    process_hashtags(status.hashtags)
                    process_urls(status.urls)
                    process_tweet(status,place_id,service)
            
            
            
    return service_response

class Command(BaseCommand):
    help = "Fetches the data from the different services provided and push to the database"

    args = '[none]'
    def handle(self, *args, **keywordargs):
        service_response = fetch_service()
        print service_response

