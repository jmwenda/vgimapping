from django.core.management.base import BaseCommand
from optparse import make_option
from vgimap.services.models import Service
import requests

def get_response(service):
    "This hits the api identified by the service and returns the response"
    try:
	req = requests.get(service.url)
    except requests.exceptions.ConnectionError, e:
        return req 
def fetch_service():
    #we get a list of services  to query
    services = Service.objects.all()
    service_response = []
    for service in services:
       response = get_response(service)
       if response is not None:
           service_response.append(response)
    return service_response

class Command(BaseCommand):
    help = "Fetches the data from the different services provided and push to the database"

    args = '[none]'
    def handle(self, *args, **keywordargs):
        service_response = fetch_service()

