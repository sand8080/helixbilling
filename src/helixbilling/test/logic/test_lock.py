# -*- coding: utf-8 -*-
import datetime
import unittest

from common import LogicTestCase

from helixcore.mapping.actions import insert

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.logic.exceptions import ActionNotAllowedError
from helixbilling.domain.objects import Currency, Balance


class LockTestCase(LogicTestCase):

    def setUp(self):
        LogicTestCase.setUp(self)
        self._fixture()

    @transaction()
    def _fixture(self, curs=None):
        self.currency = Currency(name='USD', designation='$') #IGNORE:W0201
        insert(curs, self.currency)

        balance = Balance(client_id=123, active=1, currency_id=self.currency.id, available_amount=5000, overdraft_limit=7000) #IGNORE:E1101
        self.balance = balance #IGNORE:W0201
        insert(curs, self.balance)

    def test_lock_ok(self):
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': 555,
            'amount': (60, 00),
        }
        handle_action('lock', data)
        balance = self._get_balance(data['client_id'])

        self.assertEquals(balance.available_amount, -1000)
        self.assertEquals(balance.locked_amount, 6000)

        lock = self._get_lock(self.balance.client_id, data['product_id']) #IGNORE:E1101
        self.assertEquals(lock.client_id, data['client_id'])
        self.assertEquals(lock.amount, 6000)
        self.assertTrue(isinstance(lock.locked_date, datetime.datetime))

    def test_lock_overdraft_violation(self):
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': 555,
            'amount': (120, 43),
        }
        self.assertRaises(ActionNotAllowedError, handle_action, 'lock', data)

    def test_check_locked_yes(self):
        lock_amount = (60, 00)
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': 555,
            'amount': lock_amount,
        }
        handle_action('lock', data)
        lock = self._get_lock(self.balance.client_id, data['product_id']) #IGNORE:E1101

        del data['amount']
        response = handle_action('check_locked', data)
        self.assertEquals(1, response['locked'])
        self.assertEquals(lock.locked_date, response['locked_date'])
        self.assertEquals(lock_amount, response['amount'])

    def test_check_locked_no(self):
        lock_amount = (60, 00)
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': 555,
            'amount': lock_amount,
        }
        handle_action('lock', data)

        del data['amount']
        data['product_id'] = 556
        response = handle_action('check_locked', data)
        self.assertEquals(0, response['locked'])


if __name__ == '__main__':
    unittest.main()