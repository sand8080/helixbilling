import datetime
import cjson
import unittest
from eventlet import api, util

from helixcore.test.util import profile

from helixbilling.test.db_based_test import ServiceTestCase
from helixbilling.conf import settings
from helixbilling.test.wsgi.client import Client
from helixbilling.wsgi.server import Server

util.wrap_socket_with_coroutine_socket()

api.spawn(Server.run)


class ApplicationTestCase(ServiceTestCase):
    def setUp(self):
        super(ApplicationTestCase, self).setUp()
        self.cli = Client(settings.server_host, settings.server_port, '%s' % datetime.datetime.now(), 'qazwsx')
        self.manager = self.cli

    def check_status_ok(self, raw_result):
        self.assertEqual('ok', cjson.decode(raw_result)['status'])

    @profile
    def ping_loading(self, repeats=1): #IGNORE:W0613
        self.cli.ping() #IGNORE:E1101

    def test_ping_ok(self):
        self.check_status_ok(self.cli.ping()) #IGNORE:E1101
        self.ping_loading(repeats=1)
        self.ping_loading(repeats=100)

    def test_invalid_request(self):
        raw_result = self.cli.request({'action': 'fakeaction'})
        result = cjson.decode(raw_result)
        self.assertEqual('error', result['status'])
        self.assertEqual('validation', result['category'])

    def test_add_balance(self):
        client_id = 'client id'
        currency = self.get_currencies()[0]
        self.cli.add_balance( #IGNORE:E1101
            login=self.test_login,
            password=self.test_password,
            client_id=client_id,
            active=True,
            currency=currency.code,
            overdraft_limit='100.00'
        )


if __name__ == '__main__':
    unittest.main()
