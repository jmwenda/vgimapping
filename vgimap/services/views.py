# Create your views here
from django.http import HttpResponse
from django.template import Context, loader
import OsmApi
import math
from lxml import etree
import urllib

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

def deg2rad(degrees):
    pi = math.pi
    radians = pi * degrees / 180
    return radians

def rad2deg(radians):
    pi = math.pi
    degrees = 180 * radians / pi
    return degrees

def get_boundingbox(lat,lon,radius):
    earth_radius = 6371;
    maxLat = lat + rad2deg(float(radius)/float(earth_radius));
    minLat = lat - rad2deg(radius/earth_radius);
    maxLon = lon + rad2deg(radius/earth_radius/math.cos(deg2rad(lat)));
    minLon = lon - rad2deg(radius/earth_radius/math.cos(deg2rad(lat)));
    return bbox

def search_osm(search_criteria):
    #we do need to have some bbox validation
    if search_criteria['bbox'] is not None:
        fetch_path = "/api/interpreter?data=node[name~'"+ search_criteria['search_term']+"']("+ search_criteria['bbox']+");out;"
    elif search_criteria['radius'] is not None:
        #need to confirm a coulpe of aspects about this,especially radius querying
        fetch_path = "/api/interpreter?data=node[name~'"+ search_criteria['search_term']+"'](around:"+ search_criteria['radius']+");out;"
        if search_criteria['lat'] and search_criteria['lon'] is not None:
            bbox = get_boundingbox(search_criteria['lat'],search_criteria['lon'],search_criteria['radius']) 
            fetch_path = "/api/interpreter?data=node[name~'"+ search_criteria['search_term']+"'](around:"+ bbox +");out;"
    else:
        fetch_path = "/api/interpreter?data=node[name~'"+ search_criteria['search_term']+"'];out;"
    url = urllib.quote(fetch_path,'?/=')
    data = api._get(url)
    data = api.ParseOsm(data)
    #build the opensearcg geo response object
    open_search_response  = open_search(data) 
    return open_search_response
    

def search(request):
    search_criteria = {}
    search_criteria ['search_term'] = request.GET.get('q', '')
    search_criteria ['bbox'] = request.GET.get('bbox')
    search_criteria ['radius'] = request.GET.get('radius')
    search_criteria ['lat'] = request.GET.get('lat')
    search_criteria ['lon'] = request.GET.get('lon')
    #perfrom search and return results set from the different services
    osm_results = search_osm(search_criteria)
    #we get a json dataset that needs to be made into opengeosearch capable
    return HttpResponse(etree.tostring(osm_results, pretty_print=True,xml_declaration=True))


