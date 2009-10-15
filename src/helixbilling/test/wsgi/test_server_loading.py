import unittest
from eventlet import api, util

from helixbilling.test.root_test import RootTestCase
from helixbilling.wsgi.server import Server

util.wrap_socket_with_coroutine_socket()

api.spawn(Server.run)

class ServerLoadingTestCase(RootTestCase):
    pass
#    def test_ping_ok(self):
#        t = Thread(target=run)
#        t.setDaemon(True)
#        t.start()
#
#        request_data = {'action': 'ping'}
#        conn = httplib.HTTPConnection(server_http_addr, server_http_port)
#        conn.request('POST', '/', cjson.encode(request_data))
#
#        response_obj = conn.getresponse()
#        self.assertTrue(response_obj.status, 200)
#
#        raw_response = response_obj.read()
#        response_data = cjson.decode(raw_response)
#
#        self.assertTrue(response_data['status'], 'ok')


if __name__ == '__main__':
    unittest.main()
