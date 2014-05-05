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
    
    def get_direction(self, ori, dest, pois):
        middle_points = pois[0]
        start = ori
        departure_time = int(time.time())
        final_routes = []
        for p in middle_points:
            location = "%s,%s" % (p["geometry"]["location"]["lat"], p["geometry"]["location"]["lng"])
            next_stop = location
            routes = util.query_routes(origin=start,
                    destination=next_stop,
                    departure_time=departure_time)
            if routes is not None and routes["status"] == "OK":
                final_routes.append(routes["routes"][0])
            start = location
        last_routes = util.query_routes(origin=start,
                destination=dest,
                departure_time=departure_time)
        if last_routes is not None and last_routes["status"] == "OK":
            final_routes.append(last_routes["routes"][0])

        return final_routes

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

        top_candidate = cost_matrix[0]
        json.dump(top_candidate, open('./top_candidate.json','w'))
        final_route = self.get_direction(ori, dest, top_candidate)
        json.dump(final_route, open("./real_route.json", "w"))

        return final_route

def test():
    service = Service()
    orin = "2266 Pimmit Run Lane #103, Falls Church, VA"
    dest = "900 N Glebe Road, Arlington, VA"
    pois = "The greene turtle"
    service.route(orin, dest, pois)

if __name__ == "__main__":
    test()


