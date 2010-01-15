import datetime
import unittest

from common import TestCaseWithBalance

import helixcore.mapping.actions as mapping
from helixcore.db.wrapper import EmptyResultSetError
from helixcore.server.exceptions import ActionNotAllowedError

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action


class LockTestCase(TestCaseWithBalance):
    @transaction()
    def setUp(self, curs=None): # IGNORE:W0221
        super(LockTestCase, self).setUp()
        self.balance.available_real_amount = 5000
        self.balance.available_virtual_amount = 1000
        self.balance.overdraft_limit = 6000
        mapping.update(curs, self.balance)

    def test_lock_ok(self):
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': self.balance.client_id,
            'product_id': 'super-light 555',
            'amount': (115, 00),
        }
        handle_action('lock', data)
        balance = self._get_validated_balance(self.test_login, data['client_id'])

        self.assertEquals(balance.available_real_amount, -6000)
        self.assertEquals(balance.available_virtual_amount, 500)
        self.assertEquals(balance.locked_amount, 11500)

        lock = self._get_lock(self.balance.client_id, data['product_id'])
        self.assertEquals(lock.client_id, data['client_id'])
        self.assertEquals(lock.real_amount, 11000)
        self.assertEquals(lock.virtual_amount, 500)
        self.assertTrue(isinstance(lock.locked_date, datetime.datetime))

    def test_lock_overdraft_violation(self):
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': self.balance.client_id,
            'product_id': 'lucky boy',
            'amount': (120, 43),
        }
        self.assertRaises(ActionNotAllowedError, handle_action, 'lock', data)

    def test_unlock_ok(self):
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': self.balance.client_id,
            'product_id': '555',
            'amount': (60, 00),
        }
        handle_action('lock', data)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': self.balance.client_id,
            'product_id': '555',
        }
        handle_action('unlock', data)

        balance = self._get_validated_balance(self.test_login, data['client_id'])
        self.assertEquals(balance.available_real_amount, 5000)
        self.assertEquals(balance.locked_amount, 0)
        self.assertRaises(EmptyResultSetError, self._get_lock, self.balance.client_id, data['product_id']) #IGNORE:E1101

    def test_unlock_inexistent(self):
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': self.balance.client_id,
            'product_id': '555',
            'amount': (60, 00),
        }
        handle_action('lock', data)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': self.balance.client_id,
            'product_id': '999',
        }
        self.assertRaises(ActionNotAllowedError, handle_action, 'unlock', data)

    def test_locking_order(self):
        self.balance.locking_order = ['available_real_amount', 'available_virtual_amount']
        self.balance.available_real_amount = 5000
        self.balance.available_virtual_amount = 2000
        self.balance.overdraft_limit = 0
        self.balance.locked_amount = 0
        self.update_balance(self.balance)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': self.balance.client_id,
            'product_id': '555',
            'amount': (60, 00),
        }
        handle_action('lock', data)
        self.balance = self.reload_balance(self.balance)
        self.assertEqual(0, self.balance.available_real_amount)
        self.assertEqual(1000, self.balance.available_virtual_amount)
        self.assertEqual(6000, self.balance.locked_amount)

        self.balance.locking_order = ['available_virtual_amount', 'available_real_amount']
        self.balance.available_real_amount = 6000
        self.balance.available_virtual_amount = 2000
        self.balance.overdraft_limit = 0
        self.balance.locked_amount = 0
        self.update_balance(self.balance)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': self.balance.client_id,
            'product_id': '556',
            'amount': (60, 00),
        }
        handle_action('lock', data)
        self.balance = self.reload_balance(self.balance)
        self.assertEqual(2000, self.balance.available_real_amount)
        self.assertEqual(0, self.balance.available_virtual_amount)
        self.assertEqual(6000, self.balance.locked_amount)


if __name__ == '__main__':
    unittest.main()