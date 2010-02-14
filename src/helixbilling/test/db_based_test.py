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
from helixbilling.logic.filters import (ReceiptFilter, BonusFilter,
    BalanceLockFilter, ChargeOffFilter, ActionLogFilter)
from helixbilling.error import BalanceNotFound


class DbBasedTestCase(RootTestCase):
    def setUp(self):
        install.execute('reinit', get_connection, patch_table_name, patches_path)


class ServiceTestCase(DbBasedTestCase):
    test_login = 'test_operator'
    test_password = 'qazwsx'

    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.add_operator(self.test_login, self.test_password)
        self.create_fake_currency()

    @transaction()
    def create_fake_currency(self, curs=None):
        code = 'YES'
        currency = Currency(code=code, name='y currency', location='y country',
            cent_factor=100) #IGNORE:W0201
        mapping.insert(curs, currency)
        self.currency = selector.get_currency_by_code(curs, code) #IGNORE:W0201

    @transaction()
    def get_currency_by_balance(self, balance, curs=None):
        return selector.get_currency_by_balance(curs, balance)

    @transaction()
    def get_currency(self, code, curs=None):
        return selector.get_currency_by_code(curs, code)

    def add_operator(self, login, password, custom_operator_info=None):
        self.handle_action('add_operator', {'login': login, 'password': password,
            'custom_operator_info': custom_operator_info})
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
        return ReceiptFilter(operator, {'customer_id': customer_id}, {}).filter_objs(curs)

    @transaction()
    def get_bonuses(self, operator, customer_id, curs=None):
        return BonusFilter(operator, {'customer_id': customer_id}, {}).filter_objs(curs)

    def add_receipt(self, login, password, customer_id, amount):
        d = datetime.datetime.now(pytz.utc)
        operator = self.get_operator_by_login(login)
        try:
            balance_before = self.get_balance(operator, customer_id)
        except BalanceNotFound, e:
            print e.message
        self.handle_action('enroll_receipt', {'login': login, 'password': password,
            'customer_id': customer_id, 'amount': amount})
        balance = self.get_balance(operator, customer_id)
        currency = self.get_currency_by_balance(balance)
        receipt = self.get_reciepits(operator, customer_id)[-1]
        self.assertEqual(balance_before.available_real_amount + receipt.amount, balance.available_real_amount)
        self.assertTrue(d < receipt.creation_date)
        self.assertEqual(operator.id, receipt.operator_id)
        self.assertEqual(customer_id, receipt.customer_id)
        self.assertEqual(decimal_to_cents(currency, Decimal(amount)), receipt.amount)

    def add_bonus(self, login, password, customer_id, amount):
        d = datetime.datetime.now(pytz.utc)
        operator = self.get_operator_by_login(login)
        try:
            balance_before = self.get_balance(operator, customer_id)
        except BalanceNotFound, e:
            print e.message
        self.handle_action('enroll_bonus', {'login': login, 'password': password,
            'customer_id': customer_id, 'amount': amount})
        balance = self.get_balance(operator, customer_id)
        currency = self.get_currency_by_balance(balance)
        bonus = self.get_bonuses(operator, customer_id)[-1]
        self.assertEqual(balance_before.available_virtual_amount + bonus.amount, balance.available_virtual_amount)
        self.assertTrue(d < bonus.creation_date)
        self.assertEqual(operator.id, bonus.operator_id)
        self.assertEqual(customer_id, bonus.customer_id)
        self.assertEqual(decimal_to_cents(currency, Decimal(amount)), bonus.amount)

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

    def modify_balance(self, login, password, customer_id, locking_order, active=None):
        data = {
            'login': login,
            'password': password,
            'customer_id': customer_id,
            'new_locking_order': locking_order,
        }
        if active is not None:
            data['new_active'] = active
        self.handle_action('modify_balance', data)
        operator = self.get_operator_by_login(login)
        balance = self.get_balance(operator, customer_id)
        self.assertEqual(locking_order, balance.locking_order)

    @transaction()
    def get_balance_locks(self, operator, customer_ids, order_id=None, curs=None):
        filter_params = {'customer_ids': customer_ids}
        if order_id is not None:
            filter_params['order_id'] = order_id
        f= BalanceLockFilter(operator, filter_params, {})
        return f.filter_objs(curs)

    @transaction()
    def get_balance_lock(self, operator, customer_id, order_id, curs=None):
        return selector.get_balance_lock(curs, operator, customer_id, order_id)

    @transaction()
    def get_chargeoff(self, operator, customer_id, order_id, curs=None):
        return selector.get_chargeoff(curs, operator, customer_id, order_id)

    @transaction()
    def get_chargeoffs(self, operator, customer_ids, order_id=None, curs=None):
        filter_params = {'customer_ids': customer_ids}
        if order_id is not None:
            filter_params['order_id'] = order_id
        f = ChargeOffFilter(operator, filter_params, {})
        return f.filter_objs(curs)

    @transaction()
    def get_action_logs(self, operator, filter_params, curs=None):
        return ActionLogFilter(operator, filter_params, {}).filter_objs(curs)
