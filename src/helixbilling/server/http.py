
from eventlet import api, httpd, util

from helixbilling.conf.settings import server_http_addr, server_http_port

from helixbilling.api.api import handle_request as api_handle_request
from helixbilling.api.api import handle_response as api_handle_response
from helixbilling.logic.actions import handle_action
from helixbilling.logic.response import response_error, response_app_error
from helixbilling.error.errors import RequestProcessingError

util.wrap_socket_with_coroutine_socket()

class Handler(object):
    def handle_request(self, req):
        
        raw_data = req.read_body()
        
        try:
            action_name, data = api_handle_request(raw_data)
            response = handle_action(action_name, data)
        except RequestProcessingError, e:
            response = response_error(e)
        except e:
            response = response_app_error(e.message)
        
        raw_response = api_handle_response(response)
        
        req.response(200, body=raw_response)
        
    def adapt(self, obj, req):
        'Convert obj to bytes'
        req.write(str(obj))

def run():
    class ServerLog(object):
        def write(self, s, l=0): #IGNORE:W0613
            print 'log: %s' % s
    
    #blocking
    httpd.server(api.tcp_listener((server_http_addr, server_http_port)), Handler(), max_size=5000, log=ServerLog())
