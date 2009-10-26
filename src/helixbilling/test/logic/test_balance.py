from helixcore.server.exceptions import DataIntegrityError
from helixcore.db.wrapper import EmptyResultSetError
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

    def create_balance(self, data):
        handle_action('create_balance', data)
        return self._get_balance(data['client_id'])

    def test_create_balance(self):
        data = {
            'client_id': 'U-23-52',
            'active': 1,
            'currency_name': 'USD',
            'overdraft_limit': (500, 50), # $ 500.00
        }
        balance = self.create_balance(data)
        self.assertTrue(balance.id > 0)
        self.assertEquals(balance.client_id, data['client_id'])
        self.assertTrue(isinstance(balance.created_date, datetime.datetime))
        self.assertEquals(balance.available_real_amount, 0)
        self.assertEquals(balance.locked_amount, 0)
        self.assertEquals(balance.overdraft_limit, 50050) #500.50
        self.assertEquals(balance.currency_id, self._get_currency('USD').id)
        self.assertEquals(None, balance.locking_order)

    def test_modify_balance(self):
        data = {
            'client_id': 'U-23-52',
            'active': 1,
            'currency_name': 'USD',
            'overdraft_limit': (500, 0),
            'locking_order': ['available_real_amount'],
        }
        balance = self.create_balance(data)
        self.assertEquals(balance.locking_order, ['available_real_amount'])

        data = {
            'client_id': 'U-23-52',
            'active': 0,
            'overdraft_limit': (999, 99),
            'locking_order': None,
        }
        handle_action('modify_balance', data)
        balance = self._get_balance(data['client_id'])

        self.assertEquals(balance.overdraft_limit, 99999)
        self.assertEquals(balance.active, data['active'])
        self.assertEquals(balance.locking_order, None)

    def test_delete_balance(self):
        client_id = 'cli 54'
        data = {
            'client_id': client_id,
            'active': 1,
            'currency_name': 'USD',
            'overdraft_limit': (500, 0),
            'locking_order': ['available_real_amount'],
        }
        self.create_balance(data)

        data = {'client_id': client_id}
        handle_action('delete_balance', data)
        self.assertRaises(EmptyResultSetError, self._get_balance, client_id)

    def test_create_balance_failure(self):
        data = {
            'client_id': 52,
            'active': 1,
            'currency_name': 'USD',
            'overdraft_limit': (500, 0),
            'locking_order': ['available_real_amount'],
            'FAKE': 'ERROR',
        }
        self.assertRaises(TypeError, handle_action, 'create_balance', data)


if __name__ == '__main__':
    unittest.main()