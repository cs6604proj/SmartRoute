#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import util
import time
import json
import waypoint

class Service():
    def route(self, ori, dest, pois):
        """
        Find the best route between ori and dest 
        pass pois
        """
        #find one route from ori to dest
        departure_time = int(time.time())
        routes = util.query_routes(origin=ori, 
                destination=dest,
                departure_time=departure_time)
        if routes is None or routes['status'] != "OK":
            return None

        route = routes["routes"][0]  #get the first route

        #get the points in the route to search the potential poi
        points = util.extract_points(route)
        
        if points is None or len(points) ==0:
            print "Error in extracting points"
            return None
        
        #get the candiates in the route
        candidates = []
        way_points = pois.split("|")
        for point in points:
            information = {}
            information["location"] = point
            for way_p in way_points:
                response = util.get_nearby_points(location=point, keyword=way_p)
                if response is None or response["status"] != "OK":
                    information[way_p] = []
                    continue
                ps = []
                for result in response["results"]:
                    poi = {"geometry": result["geometry"],
                            "name": result["name"],
                            "price_level": result.get("price_level", None),
                            "rating": result.get("rating", None),
                            "vicinity": result["vicinity"]}
                    ps.append(poi)
                information[way_p] = ps
            candidates.append(information)
       
        cost_matrix = waypoint.find_waypoints([candidates], way_points)
        cost_matrix.sort(key=lambda x:x[1])

        top_candidates = cost_matrix[0:3]

        #todo assume we have get the top K candidates after computing
        winners = candidates[3][way_points[0]][1]["geometry"]
        winners = "%s,%s" % (winners["location"]["lat"], 
                winners["location"]["lng"])
        final_order = [ori, winners, dest]

        final_routes = []
        for i in range(len(final_order) - 1):
            rs = util.query_routes(origin=final_order[i], 
                    destination=final_order[i+1],
                    departure_time=departure_time)
            final_routes.append(rs)

        json.dump(final_routes, open("./test_route_show.json", "w"))

def test():
    service = Service()
    orin = "2266 Pimmit Run Lane #103, Falls Church, VA"
    dest = "500 N Glebe Road, Arlington, VA"
    pois = "starbucks|supermarket"
    service.route(orin, dest, pois)

if __name__ == "__main__":
    test()


