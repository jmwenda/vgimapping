 # -*- coding: iso-8859-15 -*-
import time
from time import mktime
from datetime import datetime

import OsmApi

from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist

from vgimap.services.models import Service, OsmNode, OsmWay, OsmNodeTag

api = OsmApi.OsmApi(api = "www.overpass-api.de")
service = Service.objects.filter(type='OSM')[0]

def save_tags(node, tags):
    for k,v in tags.items():
        tag = OsmNodeTag(node=node, k=k, v=v)
        tag.save()

data  = api._get("/api/interpreter?data=node%5B%22highway%22%3D%22bus%5Fstop%22%5D%5B%22shelter%22%5D%5B%22shelter%22%21%7E%22no%22%5D%2850%2E7%2C7%2E1%2C50%2E8%2C7%2E25%29%3Bout%20meta%3B")
data = api.ParseOsm(data)

for object in data:
    if object['type'] == 'node':
        timestamp = datetime.fromtimestamp(mktime(time.strptime(object['data']['timestamp'], '%Y-%m-%dT%H:%M:%SZ'))) 
        try:
            node = OsmNode.objects.get(identifier = object['data']['id'])
            if node.version == object['data']['version']:
                # latest version already in DB 
                print "already in"
                continue 
        except ObjectDoesNotExist:
            node = OsmNode()
        node.service = service
        node.identifier = object['data']['id']
        node.user = object['data']['user']
        node.text = ""
        node.created = timestamp
        node.modified = timestamp
        node.geom = Point(object['data']['lon'], object['data']['lat'])
        node.version = object['data']['version']
        node.changeset_id = object['data']['changeset']
        #node.visible = object['data']['visible']
        node.save()
        save_tags(node, object['data']['tag']) 
