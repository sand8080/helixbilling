import datetime
import unittest

from helixcore.db.wrapper import EmptyResultSetError
from helixcore.server.exceptions import ActionNotAllowedError

from helixbilling.test.db_based_test import ServiceTestCase
from helixcore.server.errors import RequestProcessingError
#from helixbilling.conf.db import transaction


class LockTestCase(ServiceTestCase):
    customer_id = 'B2B'

    def setUp(self):
        super(LockTestCase, self).setUp()
        self.add_balance(self.test_login, self.test_password, self.customer_id, self.currency,
            overdraft_limit='60.00')
        self.add_receipt(self.test_login, self.test_password, self.customer_id, '50.00')
        self.add_bonus(self.test_login, self.test_password, self.customer_id, '10.00')

#    def test_lock(self):
#        prod_id = 'super-light 555'
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'customer_id': self.customer_id,
#            'product_id': prod_id,
#            'amount': '115.00',
#        }
#        self.handle_action('lock', data)
#        operator = self.get_operator_by_login(self.test_login)
#        balance = self.get_balance(operator, self.customer_id)
#
#        self.assertEquals(balance.available_real_amount, -6000)
#        self.assertEquals(balance.available_virtual_amount, 500)
#        self.assertEquals(balance.locked_amount, 11500)
#
#        locks = self.get_balance_locks(operator, self.customer_id, prod_id)
#        self.assertEqual(1, len(locks))
#        lock = locks[-1]
#        self.assertEquals(lock.product_id, prod_id)
#        self.assertEquals(lock.real_amount, 11000)
#        self.assertEquals(lock.virtual_amount, 500)
#        self.assertTrue(isinstance(lock.locking_date, datetime.datetime))
#
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'customer_id': self.customer_id,
#            'product_id': prod_id,
#            'amount': '5',
#        }
#        self.handle_action('lock', data)
#        balance = self.get_balance(operator, self.customer_id)
#        self.assertEquals(balance.available_real_amount, -6000)
#        self.assertEquals(balance.available_virtual_amount, 0)
#        self.assertEquals(balance.locked_amount, 12000)
#
#        locks = self.get_balance_locks(operator, self.customer_id, prod_id)
#        self.assertEqual(2, len(locks))
#        lock = locks[-1]
#        self.assertEquals(lock.product_id, prod_id)
#        self.assertEquals(lock.real_amount, 0)
#        self.assertEquals(lock.virtual_amount, 500)
#        self.assertTrue(isinstance(lock.locking_date, datetime.datetime))
#
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'customer_id': self.customer_id,
#            'product_id': prod_id,
#            'amount': '0',
#        }
#        self.assertRaises(RequestProcessingError, self.handle_action, 'lock', data)
#
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'customer_id': 'fake',
#            'product_id': prod_id,
#            'amount': '1.0',
#        }
#        self.assertRaises(RequestProcessingError, self.handle_action, 'lock', data)
#
#    def test_lock_overdraft_violation(self):
#        prod_id = 'car wash'
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'customer_id': self.customer_id,
#            'product_id': prod_id,
#            'amount': '120.43',
#        }
#        self.assertRaises(RequestProcessingError, self.handle_action, 'lock', data)

#    def test_unlock_ok(self):
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'client_id': self.balance.client_id,
#            'product_id': '555',
#            'amount': (60, 00),
#        }
#        handle_action('lock', data)
#
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'client_id': self.balance.client_id,
#            'product_id': '555',
#        }
#        handle_action('unlock', data)
#
#        balance = self._get_validated_balance(self.test_login, data['client_id'])
#        self.assertEquals(balance.available_real_amount, 5000)
#        self.assertEquals(balance.locked_amount, 0)
#        self.assertRaises(EmptyResultSetError, self._get_lock, self.balance.client_id, data['product_id']) #IGNORE:E1101
#
#    def test_unlock_inexistent(self):
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'client_id': self.balance.client_id,
#            'product_id': '555',
#            'amount': (60, 00),
#        }
#        handle_action('lock', data)
#
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'client_id': self.balance.client_id,
#            'product_id': '999',
#        }
#        self.assertRaises(ActionNotAllowedError, handle_action, 'unlock', data)
#
#    def test_locking_order(self):
#        self.balance.locking_order = ['available_real_amount', 'available_virtual_amount']
#        self.balance.available_real_amount = 5000
#        self.balance.available_virtual_amount = 2000
#        self.balance.overdraft_limit = 0
#        self.balance.locked_amount = 0
#        self.update_balance(self.balance)
#
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'client_id': self.balance.client_id,
#            'product_id': '555',
#            'amount': (60, 00),
#        }
#        handle_action('lock', data)
#        self.balance = self.reload_balance(self.balance)
#        self.assertEqual(0, self.balance.available_real_amount)
#        self.assertEqual(1000, self.balance.available_virtual_amount)
#        self.assertEqual(6000, self.balance.locked_amount)
#
#        self.balance.locking_order = ['available_virtual_amount', 'available_real_amount']
#        self.balance.available_real_amount = 6000
#        self.balance.available_virtual_amount = 2000
#        self.balance.overdraft_limit = 0
#        self.balance.locked_amount = 0
#        self.update_balance(self.balance)
#
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'client_id': self.balance.client_id,
#            'product_id': '556',
#            'amount': (60, 00),
#        }
#        handle_action('lock', data)
#        self.balance = self.reload_balance(self.balance)
#        self.assertEqual(2000, self.balance.available_real_amount)
#        self.assertEqual(0, self.balance.available_virtual_amount)
#        self.assertEqual(6000, self.balance.locked_amount)


if __name__ == '__main__':
    unittest.main()