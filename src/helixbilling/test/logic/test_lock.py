import datetime
import unittest

from helixcore.server.errors import RequestProcessingError

from helixbilling.test.db_based_test import ServiceTestCase


class BalanceLockTestCase(ServiceTestCase):
    customer_id = 'B2B'

    def setUp(self):
        super(BalanceLockTestCase, self).setUp()
        self.add_balance(self.test_login, self.test_password, self.customer_id, self.currency,
            overdraft_limit='60.00')
        self.add_receipt(self.test_login, self.test_password, self.customer_id, '50.00')
        self.add_bonus(self.test_login, self.test_password, self.customer_id, '10.00')

    def test_lock(self):
        prod_id = 'super-light 555'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'product_id': prod_id,
            'amount': '115.00',
        }
        self.handle_action('lock', data)
        operator = self.get_operator_by_login(self.test_login)
        balance = self.get_balance(operator, self.customer_id)

        self.assertEquals(balance.available_real_amount, -6000)
        self.assertEquals(balance.available_virtual_amount, 500)
        self.assertEquals(balance.locked_amount, 11500)

        locks = self.get_balance_locks(operator, self.customer_id, prod_id)
        self.assertEqual(1, len(locks))
        lock = locks[-1]
        self.assertEquals(lock.product_id, prod_id)
        self.assertEquals(lock.real_amount, 11000)
        self.assertEquals(lock.virtual_amount, 500)
        self.assertTrue(isinstance(lock.locking_date, datetime.datetime))

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'product_id': prod_id,
            'amount': '5',
        }
        self.handle_action('lock', data)
        balance = self.get_balance(operator, self.customer_id)
        self.assertEquals(balance.available_real_amount, -6000)
        self.assertEquals(balance.available_virtual_amount, 0)
        self.assertEquals(balance.locked_amount, 12000)

        locks = self.get_balance_locks(operator, self.customer_id, prod_id)
        self.assertEqual(2, len(locks))
        lock = locks[-1]
        self.assertEquals(lock.product_id, prod_id)
        self.assertEquals(lock.real_amount, 0)
        self.assertEquals(lock.virtual_amount, 500)
        self.assertTrue(isinstance(lock.locking_date, datetime.datetime))

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'product_id': prod_id,
            'amount': '0',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'lock', data)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': 'fake',
            'product_id': prod_id,
            'amount': '1.0',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'lock', data)

    def test_lock_overdraft_violation(self):
        prod_id = 'car wash'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'product_id': prod_id,
            'amount': '120.43',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'lock', data)

    def test_locking_order(self):
        operator = self.get_operator_by_login(self.test_login)
        c_id = 'c'
        self.add_balance(self.test_login, self.test_password, c_id, self.currency,
            locking_order=['available_real_amount', 'available_virtual_amount'])
        self.add_receipt(self.test_login, self.test_password, c_id, '50.00')
        self.add_bonus(self.test_login, self.test_password, c_id, '20.00')

        prod_id = 'tea'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': c_id,
            'product_id': prod_id,
            'amount': '60.00',
        }
        self.handle_action('lock', data)
        balance = self.get_balance(operator, c_id)
        self.assertEqual(0, balance.available_real_amount)
        self.assertEqual(1000, balance.available_virtual_amount)
        self.assertEqual(6000, balance.locked_amount)

        self.modify_balance(self.test_login, self.test_password, c_id,
            ['available_virtual_amount', 'available_real_amount'])
        self.add_receipt(self.test_login, self.test_password, c_id, '10')

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': c_id,
            'product_id': prod_id,
            'amount': '16.00',
        }
        self.handle_action('lock', data)
        balance = self.get_balance(operator, c_id)
        self.assertEqual(400, balance.available_real_amount)
        self.assertEqual(0, balance.available_virtual_amount)
        self.assertEqual(7600, balance.locked_amount)


if __name__ == '__main__':
    unittest.main()