from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from optparse import make_option
from vgimap.services.models import Service,UshahidiReport,UshahidiCategory
import requests
from urlparse import urljoin
import json
import datetime

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
def fetch_service():
    #we get a list of services  to query,for a start just ushahidi, will add the other services as we progress
    #services = Service.objects.all()
    services = Service.objects.filter(type='USH')
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
    return service_response

class Command(BaseCommand):
    help = "Fetches the data from the different services provided and push to the database"

    args = '[none]'
    def handle(self, *args, **keywordargs):
        service_response = fetch_service()
        print service_response

