#!/usr/local/bin/python

import argparse  
import requests  
import urlparse
import json
from akamai.edgegrid import EdgeGridAuth, EdgeRc  

  
def papi_get(edgerc_path, path):  
    edgerc = EdgeRc(edgerc_path)  
    section = 'default'  
  
    s = requests.Session()  
    s.auth = EdgeGridAuth.from_edgerc(edgerc, section)  
    baseurl = 'https://%s' % edgerc.get(section, 'host')  
  
    return s.get(urlparse.urljoin(baseurl, path))  
  
  
def ls_groups(args):
    test = json.loads(papi_get(args.edgerc, '/papi/v0/groups/').content)
    groups = list()
    for i in test['groups']['items']:
        if 'contractIds' in i:
            if len(i['contractIds']) == 1:
                groups.append({"groupName" : i['groupName'],
                               "groupId" : i['groupId'],
                               "contractIds" : i['contractIds']})
            elif len(i['contractIds']) == 2:
                groups.append({"groupName" : i['groupName'],
                               "groupId" : i['groupId'],
                               "contractIds" : i['contractIds'][0]})
                groups.append({"groupName" : i['groupName'],
                               "groupId" : i['groupId'],
                               "contractIds" : i['contractIds'][1]})
    #print groups
    ls_properties(groups)


def get_config(properties):
    for i in properties:
        if i['productionVersion'] is not None:
            result = papi_get(args.edgerc, '/papi/v0/properties/%s/versions/%s/rules/?contractId=%s&groupId=%s'
                            % (i['propertyId'], i['productionVersion'], i['contractId'], i['groupId']))

            if result.status_code == 200:
                json_result = json.loads(result.content)
                with open("../akamai_backup/%s.json" % i['propertyName'], "w") as backup_file:
                    backup_file.writelines(json.dumps(json_result, indent=2))

  
def ls_properties(groups):
    properties = list()
    for i in groups:
        #print i
        #print "~" * 25
        result = papi_get(args.edgerc, '/papi/v0/properties/?contractId=%s&groupId=%s'
                          % (i['contractIds'], i['groupId']))

        if result.status_code == 200:
            test = json.loads(result.content)
            for j in test['properties']['items']:
                if j is not None:
                    properties.append(({"contractId" : j['contractId'],
                                        "groupId" : j['groupId'],
                                        "propertyId" : j['propertyId'],
                                        "productionVersion" : j['productionVersion'],
                                        "propertyName" : j['propertyName']}))
        #print properties
    get_config(properties)

##
## MAIN
##

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser.add_argument('--edgerc', default='.edgerc')

# groups listing
sp = subparsers.add_parser('backup')
sp.set_defaults(func=ls_groups)

args = parser.parse_args()
args.func(args)
