#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import tornado.escape
import tornado.ioloop
import tornado.web
import argparse
import service
import json

DEBUG_FLAG = False

class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        global DEBUG_FLAG
        origin = self.get_argument("origin")
        dest = self.get_argument("dest")
        pois = self.get_argument("pois")
        if DEBUG_FLAG:
            response = {'status': 'OK'}
            response["routes"] = json.load(open('./test_route_show.json'))
            self.write(response)
        else:
            #todo fetch actual route
            servi = service.Service()
            routes, best_pois = servi.route(origin, dest, pois)
            if routes is None:
                response = {'status': "ERROR"}
            else:
                response = {'status': "OK",
                        "routes": routes,
                        "pois": best_pois}
            self.write(response)


application = tornado.web.Application([
    (r'/route', SearchHandler)
    ])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, help='port num')
    ap.add_argument('--debug', action='store_true', help='debug flag')
    args = ap.parse_args()
    DEBUG_FLAG = args.debug

    application.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()

