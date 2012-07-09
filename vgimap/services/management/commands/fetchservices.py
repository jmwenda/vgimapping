from django.core.management.base import BaseCommand
from optparse import make_option
from vgimap.services.models import Service,UshahidiReport,UshahidiCategory
import requests
from urlparse import urljoin
import json

extract = lambda keys, dict: reduce(lambda x, y: x.update({y[0]:y[1]}) or x,
                                            map(None, keys, map(dict.get, keys)), {})

def get_response(url):
    "This hits the api identified by the service and returns the response"
    try:
	req = requests.get(url)
        return req
    except requests.exceptions.ConnectionError, e:
        return e 
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
               print incident
               
            if response is not None:
                service_response.append(response)
    return service_response

class Command(BaseCommand):
    help = "Fetches the data from the different services provided and push to the database"

    args = '[none]'
    def handle(self, *args, **keywordargs):
        service_response = fetch_service()
        print service_response

