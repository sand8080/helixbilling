import cjson

import helixbilling.test.test_environment #IGNORE:W0611 @UnusedImport

from helixcore.install import install
from helixcore.server.api import Api

from helixbilling.conf.db import get_connection, transaction
from helixbilling.conf.settings import patch_table_name
from helixbilling.test.test_environment import patches_path
from helixbilling.logic.actions import handle_action
from helixbilling.logic import selector
from helixbilling.validator.validator import protocol
from root_test import RootTestCase


class DbBasedTestCase(RootTestCase):
    def setUp(self):
        install.execute('reinit', get_connection, patch_table_name, patches_path)


class ServiceTestCase(DbBasedTestCase):
    test_login = 'test_operator'
    test_password = 'qazwsx'

    def setUp(self):
        super(ServiceTestCase, self).setUp()

    def add_operator(self, login, password):
        self.handle_action('add_operator', {'login': login, 'password': password})
        op = self.get_operator_by_login(login)
        self.assertEqual(login, op.login)

    @transaction()
    def get_operator_by_login(self, login, curs=None):
        return selector.get_operator_by_login(curs, login)

    @transaction()
    def get_currencies(self, curs=None):
        return selector.get_currencies(curs)

    def handle_action(self, action, data):
        api = Api(protocol)
        request = dict(data, action=action)
        action_name, data = api.handle_request(cjson.encode(request))
        response = handle_action(action_name, dict(data))
        api.handle_response(action_name, dict(response))
        return response
