from ga_ows.views.wfs import WFSAdapter, FeatureDescription
from vgimap.services.models import TwitterTweet
import twitter

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

        # Just a test
        # TODO use the specified filter rather than this hard-code
        api = twitter.Api()
        statuses = api.GetUserTimeline('ortelius')
        status_ids = []
        
        # Cache to the Database
        for s in statuses:
            tweet = TwitterTweet.objects.get(identifier=s.id)
            if tweet == None: 
                tweet = TwitterTweet()
                tweet.save_tweet(s)
            status_ids.append(tweet.identifier)

        # Look back up in the DB and return the results
        return TwitterTweet.objects.filter(identifier__in=status_ids)
