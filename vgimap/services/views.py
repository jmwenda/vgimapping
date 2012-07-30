# Create your views here
from django.http import HttpResponse
from django.template import Context, loader
import OsmApi

api = OsmApi.OsmApi(api = "www.overpass-api.de")


def opensearch(request):
    response = HttpResponse(mimetype='application/opensearchdescription+xml')
    t = loader.get_template('opensearch.xml')
    c = Context({})
    response.write(t.render(c))
    return response

def search_osm(search_term):
    data  = api._get("/api/interpreter?data=node%5Bname%3DGielgen%5D%3Bout%3B")
    data = api.ParseOsm(data)
    return data
    

def search(request):
    search_term = request.GET.get('q', '')
    #perfrom search and return results set from the different services
    osm_results = search_osm(search_term)
    #we get a json dataset that needs to be made into opengeosearch capable
    response.write(osm_results)
    return response


