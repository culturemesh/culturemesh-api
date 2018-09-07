#!/home/culturp7/python/bin/python3.6

from flup.server.fcgi import WSGIServer
from run import api

WSGIServer(api).run()
