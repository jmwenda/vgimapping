# Create your views here
from django.http import HttpResponse
from django.template import Context, loader
import OsmApi
from lxml import etree

api = OsmApi.OsmApi(api = "www.overpass-api.de")


def opensearch(request):
    response = HttpResponse(mimetype='application/opensearchdescription+xml')
    t = loader.get_template('opensearch.xml')
    c = Context({})
    response.write(t.render(c))
    return response

def open_search(data):
    # need to do the name space map
    NSMAP = {"opensearch" : 'http://a9.com/-/spec/opensearch/1.1/',
         "georss" : 'http://www.georss.org/georss'}
    feed = etree.Element('feed',xmlns='http://www.w3.org/2005/Atom')
    root = etree.ElementTree(element=feed)
    #remember we have a list here from data which returns the properties as a list
    for item in data:
        #we create an  entry for every item
        entry = etree.Element('entry')
        #we create the identifier element
        identifier = etree.Element('id')
        identifier.text = str(item['data']['id'])
        name = etree.Element('title')
        name.text = item['data']['tag']['name']
        entry.append(identifier)
        entry.append(name)
        # having problems with the lxml namespaces. Will deal with this later
        pointNS = { 'georss' : 'georss'}
        point = etree.Element("{georss}point",nsmap = pointNS)
        point.text = str(item['data']['lat']) + ' ' + str(item['data']['lon'])
        entry.append(point)
        feed.append(entry)
    return root
    
def search_osm(search_criteria):
    data  = api._get("/api/interpreter?data=node%5Bname%3D"+ search_criteria['search_term'] +"%5D%3Bout%3B")
    data = api.ParseOsm(data)
    #build the opensearcg geo response object
    open_search_response  = open_search(data) 
    return open_search_response
    

def search(request):
    search_criteria = {}
    search_criteria ['search_term'] = request.GET.get('q', '')
    #perfrom search and return results set from the different services
    osm_results = search_osm(search_criteria)
    #we get a json dataset that needs to be made into opengeosearch capable
    return HttpResponse(etree.tostring(osm_results, pretty_print=True,xml_declaration=True))


