# -*- coding: utf-8 -*-
import datetime
import unittest

from common import LogicTestCase

from helixcore.mapping.actions import insert

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.domain.objects import Currency


class BalanceTestCase(LogicTestCase):

    def setUp(self):
        LogicTestCase.setUp(self)
        self._fixture()

    @transaction()
    def _fixture(self, curs=None):
        insert(curs, Currency(name='USD', designation='$'))

    def test_create_balance(self):
        data = {
            'client_id': 23,
            'active': 1,
            'currency_name': 'USD',
            'overdraft_limit': (500, 50), # $ 500.00
        }
        handle_action('create_balance', data)
        balance = self._get_balance(data['client_id'])

        self.assertTrue(balance.id > 0)
        self.assertEquals(balance.client_id, data['client_id'])
        self.assertTrue(isinstance(balance.created_date, datetime.datetime))
        self.assertEquals(balance.available_amount, 0)
        self.assertEquals(balance.locked_amount, 0)
        self.assertEquals(balance.overdraft_limit, 50050) #500.50
        self.assertEquals(balance.currency_id, self._get_currency('USD').id)

    def test_modify_balance(self):
        data = {
            'client_id': 23,
            'active': 1,
            'currency_name': 'USD',
            'overdraft_limit': (500, 0),
        }
        handle_action('create_balance', data)

        data = {
            'client_id': 23,
            'active': 0,
            'overdraft_limit': (999, 99),
        }
        handle_action('modify_balance', data)
        balance = self._get_balance(data['client_id'])

        self.assertEquals(balance.overdraft_limit, 99999)
        self.assertEquals(balance.active, data['active'])

if __name__ == '__main__':
    unittest.main()