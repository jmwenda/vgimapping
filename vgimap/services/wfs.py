from ga_ows.views.wfs import WFSAdapter, FeatureDescription

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
        pass
