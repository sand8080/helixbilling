
from eventlet import api, httpd, util
import logging

from helixbilling.conf.settings import server_http_addr, server_http_port

from helixbilling.api.api import handle_request as api_handle_request
from helixbilling.api.api import handle_response as api_handle_response
from helixbilling.logic.actions import handle_action
from helixbilling.logic.response import response_error, response_app_error
from helixbilling.error.errors import RequestProcessingError
from helixbilling.conf.log import logger

util.wrap_socket_with_coroutine_socket()

class Handler(object):
    def handle_request(self, req):

        raw_data = req.read_body()
        logger.info('HTTP req from %s: %s' % (str(req.socket().getpeername()), raw_data))

        response_ok = False
        try:
            action_name, data = api_handle_request(raw_data)
            response = handle_action(action_name, data)
            response_ok = True
        except RequestProcessingError, e:
            response = response_error(e)
        except e:
            response = response_app_error(e.message)

        raw_response = api_handle_response(response)
        self.log_response(req, response_ok, raw_response)
        req.response(200, body=raw_response)

    def log_response(self, req, response_ok, raw_response):
        level = response_ok and logging.INFO or logging.ERROR
        logger.log(level, 'HTTP response to %s: %s' % (str(req.socket().getpeername()), raw_response))

    def adapt(self, obj, req):
        'Convert obj to bytes'
        req.write(str(obj))

def run():
    class ServerLog(object):
        def write(self, s, l=0): #IGNORE:W0613
            logger.info('server: %s' % s)

    #blocking
    httpd.server(api.tcp_listener((server_http_addr, server_http_port)), Handler(), max_size=5000, log=ServerLog())
