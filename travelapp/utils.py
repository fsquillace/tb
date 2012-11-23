'''
Created on Nov 21, 2012

@author: Filippo Squillace
'''

import requests
import urllib
import json

def api(url, payload_get, payload_post={}, method="GET"):
    """
    enpoint is the url for making the request.
    payload_get is a dict to be attached into the query string.
    payload_post is the post data.
    method is the request type. It can be POST, GET or DELETE.
    """
    if method.upper() == "GET":
        res = requests.get(url, params=payload_get)
    elif method.upper() == "POST":
        qs = urllib.urlencode(payload_get)
        res = requests.post(url+'?'+qs,\
                data=json.dumps(payload_post),\
                headers = {'content-type': 'application/json'})
    elif method.upper() == "DELETE":
        qs = urllib.urlencode(payload_get)
        res = requests.delete(url+'?'+qs)

    return res


