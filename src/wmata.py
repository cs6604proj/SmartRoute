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

class WmataException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Wmata(object):
    """
    Wmata API
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.wmata.com"
        self.api_type = None

    def _request(self,method, params={}):
        params["api_key"] = self.api_key
        request_url = "%s/%s/json/%s?%s" % (self.base_url,
                self.api_type,
                method,
                urllib.urlencode(params))
        try:
            response = urllib2.urlopen(request_url)
            result = json.load(response)
            return result
        except:
            print "Error in url [%s]" % request_url
            print "Error Info ", sys.exc_info()
        return None

    def __getattr__(self, method):
        
        def handler(kwargs):
            return self._request(method, kwargs)
        handler.method = method
        return handler

class Bus(Wmata):
    def __init__(self, api_key=config.WMATA_API):
        super(Bus, self).__init__(api_key)
        self.api_type = "Bus.svc"

class Rail(Wmata):
    def __init__(self, api_key=config.WMATA_API):
        super(Rail, self).__init__(api_key)
        self.api_type = "Rail.svc"

def test():
    bus = Bus()
    rail = Rail()

    p = {
            "routeId": "28X", 
            "date": "2014-05-02",
            "includingVariations": "false"
            }
    result = bus.jRouteSchedule(p)
    print result

    p2 = {"LineCode": "OR"}
    result2 = rail.jStations(p2)
    print result2

if __name__ == "__main__":
    test()

