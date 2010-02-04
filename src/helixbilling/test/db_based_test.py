import cjson
import datetime
import pytz
from decimal import Decimal

import helixbilling.test.test_environment #IGNORE:W0611 @UnusedImport

from helixcore.install import install
from helixcore.server.api import Api
import helixcore.mapping.actions as mapping

from helixbilling.test.root_test import RootTestCase
from helixbilling.conf.db import get_connection, transaction
from helixbilling.conf.settings import patch_table_name
from helixbilling.test.test_environment import patches_path
from helixbilling.logic.actions import handle_action
from helixbilling.logic import selector
from helixbilling.validator.validator import protocol
from helixbilling.logic.helper import decimal_to_cents, cents_to_decimal
from helixbilling.domain.objects import Currency


class DbBasedTestCase(RootTestCase):
    def setUp(self):
        install.execute('reinit', get_connection, patch_table_name, patches_path)


class ServiceTestCase(DbBasedTestCase):
    test_login = 'test_operator'
    test_password = 'qazwsx'

    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.add_operator(self.test_login, self.test_password)

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

    @transaction()
    def get_reciepits(self, operator, customer_id, curs=None):
        return selector.get_receipts(curs, operator, {'customer_ids': [customer_id]})


    def add_receipt(self, login, password, customer_id, amount):
        d = datetime.datetime.now(pytz.utc)
        self.handle_action('add_receipt', {'login': login, 'password': password,
            'customer_id': customer_id, 'amount': amount})
        operator = self.get_operator_by_login(login)
        receipt = self.get_reciepits(operator, customer_id)[-1]
        self.assertTrue(d < receipt.created_date)
        self.assertEqual(operator.id, receipt.operator_id)
        self.assertEqual(customer_id, receipt.customer_id)
        self.assertEqual(decimal_to_cents(amount), receipt.amount)

    @transaction()
    def get_balance(self, operator, customer_id, curs=None):
        return selector.get_balance(curs, operator, customer_id)

    def add_balance(self, login, password, customer_id, currency, active=True, overdraft_limit=None,
        locking_order=None):
        data = {
            'login': login,
            'password': password,
            'customer_id': customer_id,
            'currency': currency.code,
            'active': active,
            'locking_order': locking_order,
        }
        if overdraft_limit is not None:
            data['overdraft_limit'] = overdraft_limit

        self.handle_action('add_balance', data)
        operator = self.get_operator_by_login(login)
        balance = self.get_balance(operator, customer_id)
        self.assertTrue(balance.id > 0)
        self.assertEquals(operator.id, balance.operator_id)
        self.assertEquals(customer_id, balance.customer_id)
        self.assertTrue(isinstance(balance.creation_date, datetime.datetime))
        self.assertEquals(0, balance.available_real_amount)
        self.assertEquals(0, balance.locked_amount)
        if overdraft_limit is None:
            self.assertEquals(Decimal(0), cents_to_decimal(currency, balance.overdraft_limit))
        else:
            self.assertEquals(Decimal(overdraft_limit), cents_to_decimal(currency, balance.overdraft_limit))
        self.assertEquals(currency.id, balance.currency_id)
        self.assertEquals(locking_order, balance.locking_order)
        return balance


class TestCaseWithCurrency(ServiceTestCase):
    def setUp(self):
        super(TestCaseWithCurrency, self).setUp()
        self._fixture()

    @transaction()
    def _fixture(self, curs=None):
        code = 'YES'
        currency = Currency(code=code, name='y currency', location='y country',
            cent_factor=100) #IGNORE:W0201
        mapping.insert(curs, currency)
        self.currency = selector.get_currency_by_code(curs, code) #IGNORE:W0201

    @transaction()
    def get_currency_by_balance(self, balance, curs=None):
        return selector.get_currency_by_balance(curs, balance)
