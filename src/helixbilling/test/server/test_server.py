
import unittest
import httplib
import cjson
from threading import Thread

from helixbilling.conf.settings import server_http_addr, server_http_port
from helixbilling.server.http import run

class ServerTestCase(unittest.TestCase):
    
    def test_ping_ok(self):
        t = Thread(target=run)
        t.setDaemon(True)
        t.start()
        
        request_data = {'action': 'ping'}
        
        conn = httplib.HTTPConnection(server_http_addr, server_http_port)
        conn.request('POST', '/', cjson.encode(request_data))
        
        response_obj = conn.getresponse()
        self.assertTrue(response_obj.status, 200)
        
        raw_response = response_obj.read()
        print 'raw response body: %s' % raw_response
        response_data = cjson.decode(raw_response)
        
        self.assertTrue(response_data['status'], 'ok')
