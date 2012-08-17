# Create your views here
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from vgimap.services.models import Service
import OsmApi
import math
from lxml import etree
import urllib
import requests
from urlparse import urljoin
import re
import json

api = OsmApi.OsmApi(api = "www.overpass-api.de")

DOCTYPE = '<?xml version="1.0" encoding="UTF-8"?>'
XMLNS = 'http://docs.openstack.org/identity/api/v2.0'

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
    #open_search_response  = open_search(data) 
    #return open_search_response
    return data

def get_response(url):
    "This hits the api identified by the service and returns the response"
    try:
        req = requests.get(url)
        return req
    except requests.exceptions.ConnectionError, e:
        return e

def serialize(d):
    """Serialize a dictionary to XML, this is mainly for Ushahidi that is proving troublesome"""
    #assert len(d.keys()) == 1, 'Cannot encode more than one root element'
    # name the root dom element
    name = d.keys()[0]

    # only the root dom element gets an xlmns, TODO(dolph): ... I think?
    root = etree.Element(name)

    populate_element(root, d[name])

    # TODO(dolph): we don't actually need to pretty print for real clients
    # TODO(dolph): i think there's a way to get a doctype from lxml?
    return '%s\n%s' % (DOCTYPE, etree.tostring(root, pretty_print=True))

def populate_element(element, d):
    """Populates an etree with the given dictionary"""
    for k, v in d.iteritems():
        if type(v) is dict:
            # serialize the child dictionary
            child = etree.Element(k)
            populate_element(child, v)
            element.append(child)
        elif type(v) is list:
            # serialize the child list
            # TODO(dolph): this is where the spec has a LOT of inconsistency, but this covers 80% of it
            if k[-1] == 's':
                name = k[:-1]
            else:
                name = k

            for item in v:
                child = etree.Element(name)
                populate_element(child, item)
                element.append(child)
        else:
            # add attributes to the current element
            element.set(k, unicode(v))

def search_ushahidi(search_criteria):
    #we perform the search to the ushahidi api
    #todo confirm if we are searching against all ushahidi instances registered as services
    service = Service.objects.get(type='USH')
    if search_criteria['bbox'] is not None:
        #bbox_list = re.sub(r'\s', '', search_criteria['bbox']).split(',')
        sw = bbox_list[1]+','+bbox_list[0]
        ne = bbox_list[3]+','+bbox_list[2] 
        url = urljoin(service.url,'api?task=incidents&by=bounds&sw='+ sw + '&ne='+ne+'&c')
    else:
        url = urljoin(service.url,'api?task=incidents')

    response = get_response(url) #put this all into one method once i confirm a couple of things
    data = response.json
    #indicents = data['payload']['incidents']
    return data
 

def search(request):
    search_criteria = {}
    search_criteria ['search_term'] = request.GET.get('q', '')
    search_criteria ['bbox'] = request.GET.get('bbox')
    search_criteria ['radius'] = request.GET.get('radius')
    search_criteria ['lat'] = request.GET.get('lat')
    search_criteria ['lon'] = request.GET.get('lon')
    if 'format' in request.GET:
        format = request.GET.get('format')
    else:
        format = None
    #perfrom search and return results set from the different services
    osm_results = search_osm(search_criteria)
    #perform search results for ushahidi
    #ushahidi_results = search_ushahidi(search_criteria)
    #serialized_results = serialize(ushahidi_results)
    #serialized_results = etree.fromstring(serialized_results)
    #we get a json dataset that needs to be made into opengeosearch capable
    #return HttpResponse(etree.tostring(osm_results, pretty_print=True,xml_declaration=True))
    #return HttpResponse(etree.tostring(serialized_results, pretty_print=True,xml_declaration=True),content_type='application/xml')
    #return HttpResponse(etree.tostring(osm_results, pretty_print=True,xml_declaration=True),content_type='text/html')
    if format == 'rss':
        return HttpResponse(etree.tostring(open_search(osm_results), pretty_print=True,xml_declaration=True),content_type='application/xml')
    else:
    	return render_to_response('search.html', {"data": osm_results},
        	mimetype="text/html")
