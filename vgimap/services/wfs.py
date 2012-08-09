from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Point
from ga_ows.views.wfs import WFSAdapter, FeatureDescription
from vgimap.services.models import TwitterTweet,UshahidiReport
import twitter
import json
from urlparse import urljoin
import requests
import datetime

right_now = datetime.datetime.utcnow()

def get_response(url):
    "This hits the api identified by the service and returns the response"
    try:
        req = requests.get(url)
        return req
    except requests.exceptions.ConnectionError, e:
        return e

class TwitterWFSAdapter(WFSAdapter):
    def __init__(self):
        pass

    def get_feature_descriptions(self, request, **params):
        namespace = request.build_absolute_uri().split('?')[0] + "/schema"
        extent = (-180,-90,180,90)

        return [FeatureDescription(
                ns=namespace,
                ns_name="tweets",
                name="tweets",
                abstract="twitter tweets",
                title="twitter tweets",
                keywords=[],
                srs="EPSG:4326",
                bbox=[-180,-90,180,90],
                schema=namespace
            )]     

    def list_stored_queries(self, request):
        pass

    def get_features(self, request, params):
        # Can eventually support stored queries here
        return self.AdHocQuery(request, params)

    def AdHocQuery(self, request, params):
        type_names = params.cleaned_data['type_names'] # only support one type-name at a time (model) for now
        flt = params.cleaned_data['filter'] # filter should be in JSON 
        bbox = params.cleaned_data['bbox'] 
        sort_by = params.cleaned_data['sort_by']
        count = params.cleaned_data['count']
        if not count:
            count = params.cleand_data['max_features'] 
        start_index = params.cleaned_data['start_index']
        srs_name = params.cleaned_data['srs_name'] # assume bbox is in this
        srs_format = params.cleaned_data['srs_format'] # this can be proj, None (srid), srid, or wkt.
        
        if flt:
            flt_dict = json.loads(flt)
        
            api = twitter.Api()
            if 'user' in flt_dict:
                statuses = api.GetUserTimeline(flt_dict['user'])
            else:
                statuses = api.GetPublicTimeline() 
            status_ids = []
            # Cache to the Database
            for s in statuses:
                try:
                    tweet = TwitterTweet.objects.get(identifier=s.id)
                except ObjectDoesNotExist:
                    tweet = TwitterTweet()
                    tweet.save_tweet(s)
                status_ids.append(tweet.identifier)

            # Look back up in the DB and return the results
            return TwitterTweet.objects.filter(identifier__in=status_ids) # TODO Slice for paging
        else:
            return TwitterTweet.objects.all() # TODO slice for paginl
class UshahidiWFSAdapter(WFSAdapter):
    def __init__(self):
        pass

    def get_feature_descriptions(self, request, **params):
        namespace = request.build_absolute_uri().split('?')[0] + "/schema"
        extent = (-180,-90,180,90)

        return [FeatureDescription(
                ns=namespace,
                ns_name="tweets",
                name="tweets",
                abstract="twitter tweets",
                title="twitter tweets",
                keywords=[],
                srs="EPSG:4326",
                bbox=[-180,-90,180,90],
                schema=namespace
            )]

    def list_stored_queries(self, request):
        pass

    def get_features(self, request, params):
        # Can eventually support stored queries here
        return self.AdHocQuery(request, params)
    

    def AdHocQuery(self, request, params):
        type_names = params.cleaned_data['type_names'] # only support one type-name at a time (model) for now
        flt = params.cleaned_data['filter'] # filter should be in JSON 
        bbox = params.cleaned_data['bbox']
        sort_by = params.cleaned_data['sort_by']
        count = params.cleaned_data['count']
        if not count:
            count = params.cleand_data['max_features']
        start_index = params.cleaned_data['start_index']
        srs_name = params.cleaned_data['srs_name'] # assume bbox is in this
        srs_format = params.cleaned_data['srs_format'] # this can be proj, None (srid), srid, or wkt.

        if flt:
            flt_dict = json.loads(flt)

            if 'service' in flt_dict:
                #we get the service from the db, create it if it does not exists
                ushahidireport = UshahidiReport.objects.get(service__name=flt_dict['service']) #todo create when the service does not exist
                service = ushahidireport.service
                #we now fetch the reports into a dictionary
                url = urljoin(service.url,'api?task=incidents')
                response = get_response(url)
                data = response.json
                reports = data['payload']['incidents']
            reports_ids = []
            # Cache to the Database
            for incident in reports:
                try:
                    report = UshahidiReport.objects.get(identifier=incident['incident']['incidentid'])
                except ObjectDoesNotExist:
                    report = UshahidiReport(service=service,identifier=incident['incident']['incidentid'],incident_mode = incident['incident']['incidentmode']
                             ,created = right_now,incident_active = incident['incident']['incidentactive']
                             ,incident_verified = incident['incident']['incidentverified'],location_id = incident['incident']['locationid']
                             ,text = incident['incident']['incidentdescription'],title = incident['incident']['incidenttitle']
                             ,geom = Point(float(incident['incident']['locationlongitude']), float(incident['incident']['locationlatitude']))
                             ,location_name = incident['incident']['locationname'],person_first = None,person_last = None,person_email = None
                             ,incident_photo = None,incident_video = None,incident_news = None)
                    report.save(report)
                reports_ids.append(incident['incident']['incidentid'])

            # Look back up in the DB and return the results
            return UshahidiReport.objects.filter(identifier__in=reports_ids) # TODO Slice for paging
        else:
            return UshahidiReport.objects.all() # TODO slice for paging

