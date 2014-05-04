#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import json
import math
import wmata
from datetime import datetime
import time
from google import Google, Places

def ll_distance(lat1, lon1, lat2, lon2):
    if ((lat1 == lat2) and (lon1 == lon2)):
        return 0
    try:
        delta = lon2 - lon1
        a = math.radians(lat1)
        b = math.radians(lat2)
        C = math.radians(delta)
        x = math.sin(a) * math.sin(b) + math.cos(a) * math.cos(b) * math.cos(C)
        distance = math.acos(x) # in radians
        distance  = math.degrees(distance) # in degrees
        distance  = distance * 60 # 60 nautical miles / lat degree
        distance = distance * 1852 # conversion to meters
        distance  = round(distance)
        return distance;
    except:
        print sys.exc_info()
        return 0

def helper_dis(x, y):
    x_lat, x_lng = map(float, x.split(","))
    y_lat, y_lng = map(float, y.split(","))
    return ll_distance(x_lat, x_lng, y_lat, y_lng)

def filter_points(points, threshold=2500):
    if len(points) == 0 or points is None:
        return []
    start = points[0]
    result = []
    result.append(start)
    curr = 0
    next_p = curr + 1
    while next_p < len(points):
        dis = helper_dis(points[curr], points[next_p])
        if dis <= threshold:
            next_p += 1
        else:
            curr = next_p
            next_p += 1
            result.append(points[curr])
    return result

def match_by_geo(location1, location2):
    if helper_dis(location1, location2) < 300:
        return True
    return False

def get_stops(v_type, v_name, v_head_sign, start_stop, end_stop):
    ranges = []
    if v_type == "Bus":
        api = wmata.Bus()
        p = {"routeId": v_name, "date": datetime.strftime(datetime.now(), "%Y-%m-%d")}
        result = api.jRouteDetails(p)
        if result is None:
            return None
        for key, detail in result.items():
            if key in ['Name', 'RouteID']:
                continue
            if detail["TripHeadsign"].lower() == v_head_sign.lower():
                stops = detail["Stops"]
                found = False
                for stop in stops:
                    stop_geo = "%s,%s" % (stop["Lat"], stop["Lon"])
                    if match_by_geo(start_stop, stop_geo):
                        found = True
                    if found:
                        ranges.append(stop_geo)
                    if match_by_geo(end_stop, stop_geo):
                        ranges.append(stop_geo)
                        break

    elif v_type == "Subway":
        api = wmata.Rail()
        p = {"LineCode": v_name}
        result = api.jStations(p)
        stations = result['Stations']
        found = False
        start = 0
        end = 0
        for i, stop in enumerate(stations):
            name = stop["Name"]
            stop_geo = "%s,%s" % (stop["Lat"], stop["Lon"])
            if match_by_geo(start_stop, stop_geo):
                start = i
                found = not found
                ranges.append(stop_geo)
                continue
            if match_by_geo(end_stop, stop_geo):
                end = i
                found = not found
                ranges.append(stop_geo)
                continue
            if found:
                ranges.append(stop_geo)
        if start > end:
            ranges.reverse()

    return ranges

def extract_points(route):
    """
    Extract the intermediate points in the route 
    to query the nearby point of interest
    """
    SUBWAYS = {"Orange": "OR",
            "Red": "RD",
            "Green": "GR",
            "Yellow": "YL",
            "Blue": "BL"}
    points = []
    steps = route["legs"][0]["steps"]
    start_location = route["legs"][0]["start_location"]
    points.append("%s,%s" % (start_location["lat"],
        start_location["lng"])) 
    for step in steps:
        travel_mode = step["travel_mode"]
        if travel_mode.lower() != "transit":
            points.append("%s,%s" % (step["end_location"]["lat"],
                step["end_location"]["lng"]))
        else:
            #to do add stops of the route in consideration
            #now we just use the start and end
            details = step["transit_details"]
            v_type = details["line"]["vehicle"]["name"]
            v_name = details["line"]["short_name"]
            if v_name in SUBWAYS:
                v_name = SUBWAYS[v_name]
            v_headsign = details["headsign"]
            start_stop = "%s,%s" % (details["departure_stop"]["location"]["lat"],
                    details["departure_stop"]["location"]["lng"])
            end_stop = "%s,%s" % (details["arrival_stop"]["location"]["lat"],
                    details["arrival_stop"]["location"]["lng"])
            mid_stops = get_stops(v_type, v_name, v_headsign, start_stop, end_stop)
            points.extend(mid_stops)
    #to do the cluster
    return points


def query_routes(sensor='false', mode='transit', 
        **kwargs):
    gmap = Google()
    params = {}
    params["sensor"] = sensor
    params["mode"] = mode
    params.update(kwargs)
    response = gmap.directions(params)
    return response


def get_nearby_points(sensor='false', radious='3200', rankby='prominence', 
        **kwargs):
    gmap = Places()
    params = {}
    params["sensor"] = sensor
    params["radius"] = radious
    params["rankby"] = rankby
    params.update(kwargs)
    reponse = gmap.nearbysearch(params)
    return reponse

if __name__ == "__main__":
    pass

