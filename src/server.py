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

class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        origin = self.get_argument("origin")
        dest = self.get_argument("dest")
        pois = self.get_argument("pois")

        response = {'status': 'OK'}
        response["routes"] = json.load(open('./test_route_show.json'))
        self.write(response)

application = tornado.web.Application([
    (r'/route', SearchHandler)
    ])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, help='port num')
    args = ap.parse_args()

    application.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()

