#! /usr/bin/env python

import os
import sys
import json
import itertools
import util


wrate = 1.0
trate = 0.1
rwd_rate = 1
stp_penalty = 1


def calculate_1waypoint_cost(i, a_poi, src_loc, dest_loc, i_loc, len_bs):
    a_loc = str(a_poi['geometry']['location']['lat']) + "," + str(a_poi['geometry']['location']['lng'])
    a2i_walk_cost = util.helper_dis(a_loc, i_loc)
    src2i_transit_cost = util.helper_dis(src_loc, i_loc)
    i2dest_transit_cost = util.helper_dis(i_loc, dest_loc)
    cost = 0 
    if a_poi['rating'] is None:
        a_poi['rating'] = 0 
    cost = (src2i_transit_cost + i2dest_transit_cost)*trate + 2*(a2i_walk_cost)*wrate - float(a_poi['rating'])*rwd_rate
    if ((i != 0) and (i != len_bs -1)):
        cost = cost + stp_penalty
    
    cost_list = []
    cost_list = [[a_poi], cost]
    return cost_list


def calculate_2waypoint_cost(i, j, a_poi, b_poi, src_loc, dest_loc, i_loc, j_loc, len_bs):
    a_loc = str(a_poi['geometry']['location']['lat']) + "," + str(a_poi['geometry']['location']['lng'])
    b_loc = str(b_poi['geometry']['location']['lat']) + "," + str(b_poi['geometry']['location']['lng'])
    a2i_walk_cost = util.helper_dis(a_loc, i_loc)
    b2j_walk_cost = util.helper_dis(b_loc, j_loc)
    cost = 0
    if a_poi['rating'] is None:
        a_poi['rating'] = 0
    if b_poi['rating'] is None:
        b_poi['rating'] = 0

    cost_list = []

    if (i < j):
        src2i_transit_cost = util.helper_dis(src_loc, i_loc)
        i2j_transit_cost = util.helper_dis(i_loc, j_loc)
        j2dest_transit_cost = util.helper_dis(j_loc, dest_loc)
        cost = (src2i_transit_cost + i2j_transit_cost + j2dest_transit_cost)*trate + 2*(a2i_walk_cost + b2j_walk_cost)*wrate - (float(a_poi['rating']) + float(b_poi['rating']))*rwd_rate
        if ((i == 0) and (j == len_bs - 1)):
            cost = cost
        elif ((i == 0) or (j == len_bs - 1)):
            cost = cost + stp_penalty
        else:
            cost = cost + 2*stp_penalty
    elif (i == j):
        src2i_transit_cost = util.helper_dis(src_loc, i_loc)
        a2b_walk_cost = util.helper_dis(a_loc, b_loc)
        i2dest_transit_cost = util.helper_dis(i_loc, dest_loc)
        cost = (src2i_transit_cost + i2dest_transit_cost)*trate + (a2i_walk_cost + b2j_walk_cost + a2b_walk_cost)*wrate - (float(a_poi['rating']) + float(b_poi['rating']))*rwd_rate
        if ((i != 0) and (i != len_bs - 1)):
            cost = cost + stp_penalty
    else:
        src2j_transit_cost = util.helper_dis(src_loc, j_loc)
        j2i_transit_cost = util.helper_dis(j_loc, i_loc)
        i2dest_transit_cost = util.helper_dis(i_loc, dest_loc)
        cost = (src2j_transit_cost + j2i_transit_cost + i2dest_transit_cost)*trate + 2*(a2i_walk_cost + b2j_walk_cost)*wrate - (float(a_poi['rating']) + float(b_poi['rating']))*rwd_rate
        if ((j == 0) and (i == len_bs - 1)):
            cost = cost
        elif ((j == 0) or (i == len_bs - 1)):
            cost = cost + stp_penalty
        else:
            cost = cost + 2*stp_penalty
    
    cost_list = [[a_poi, b_poi], cost]
    return cost_list


def find_waypoints(pois, keys):
    cost_matrix = []
    if len(keys) == 1:
        cost_matrix = find_one_waypoint(pois, keys)
    elif len(keys) == 2:
        cost_matrix = find_two_waypoints(pois, keys)
    else:
        return cost_matrix

    return cost_matrix


def find_one_waypoint(pois, keys):
    all_pois = pois[0]
    len_bs = len(all_pois)
    cost_matrix = []
    
    for i in range(0, len_bs):
        for a_poi in all_pois[i].get(keys[0], []):
            if len(a_poi) == 0:
                continue
            cost = calculate_1waypoint_cost(i, a_poi, all_pois[0]['location'], all_pois[len_bs-1]['location'], all_pois[i]['location'], len_bs)
            cost_matrix.append(cost)

    return cost_matrix


def find_two_waypoints(pois, keys):
    all_pois = pois[0]
    len_bs = len(all_pois)

    cost_matrix = []
    for i in range(0, len_bs):
        for a_poi in all_pois[i].get(keys[0], []):
            if len(a_poi) == 0:
                continue
            for j in range(0, len_bs):
                for b_poi in all_pois[j].get(keys[1], []):
                    if len(b_poi) == 0:
                        continue
                    cost = calculate_2waypoint_cost(i, j, a_poi, b_poi, all_pois[0]['location'], all_pois[len_bs-1]['location'], all_pois[i]['location'], all_pois[j]['location'], len_bs)
                    cost_matrix.append(cost)

    return cost_matrix


if __name__ == "__main__":
    pois = [json.loads(e) for e in open("sample_pois.json", 'r').readlines()]
    cost_matrix = find_waypoints(pois, ['startbucks', 'supermarket'])
    print cost_matrix[0]
    print cost_matrix[1]
    print "\n******************\n"
    cost_matrix = find_waypoints(pois, ['startbucks'])
    print cost_matrix[0]
    print cost_matrix[1]
    print "\n****************\n"
    cost_matrix = find_waypoints(pois, ['supermarket'])
    print cost_matrix[0]
    print cost_matrix[1]
    print "\n*********************\n"
    cost_matrix = find_waypoints(pois, [])
    print cost_matrix


