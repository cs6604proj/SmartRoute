#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import urllib2
import urllib
import json
import config

class Google(object):
    """
    Google Map API    
    """
    def __init__(self, api_key=config.GOOGLE_API):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api"

    def _request(self, method, params= {}):
        params["key"] = self.api_key
        request_url = "%s/%s/json?%s" % (self.base_url, 
                method,
                urllib.urlencode(params))
        try:
            response = json.load(urllib2.urlopen(request_url))
            return response
        except:
            print "Error in url [%s]" % request_url
            print "Error info ", sys.exc_info()

    def __getattr__(self, method):
        def handler(params):
            return self._request(method, params)
        return handler

class Places(Google):
    """
    Google places api
    """
    def __init__(self):
        super(Places, self).__init__()
        self.base_url = "https://maps.googleapis.com/maps/api/place"

def test():
    import time
    google = Google()
    start = (38.9015690,-77.2087140)
    end = (38.8760750,-77.1084090)
    departure_time = int(time.time())

    dir_param1 = {"origin": ",".join(map(str,start)), "destination": ",".join(map(str,end)), 
            "sensor": "false", "mode":"transit",
            "departure_time":departure_time}
    result = google.directions(dir_param1)
    print result

if __name__ == "__main__":
    test()

