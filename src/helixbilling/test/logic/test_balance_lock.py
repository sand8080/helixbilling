import datetime
import unittest

from helixcore.server.errors import RequestProcessingError

from helixbilling.test.db_based_test import ServiceTestCase
from helixbilling.error import BalanceNotFound, BalanceDisabled


class BalanceLockTestCase(ServiceTestCase):
    customer_id = 'locker'

    def setUp(self):
        super(BalanceLockTestCase, self).setUp()
        self.add_balance(self.test_login, self.test_password, self.customer_id, self.currency,
            overdraft_limit='60.00')
        self.add_receipt(self.test_login, self.test_password, self.customer_id, '50.00')
        self.add_bonus(self.test_login, self.test_password, self.customer_id, '10.00')

    def test_balance_lock(self):
        order_id = 'super-light 555'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'order_id': order_id,
            'amount': '115.00',
        }
        self.handle_action('balance_lock', data)

        operator = self.get_operator_by_login(self.test_login)
        balance = self.get_balance(operator, self.customer_id)
        self.assertEquals(balance.available_real_amount, -6000)
        self.assertEquals(balance.available_virtual_amount, 500)
        self.assertEquals(balance.locked_amount, 11500)

        locks = self.get_balance_locks(operator, [self.customer_id], order_id=order_id, order_by='id')
        self.assertEqual(1, len(locks))
        lock = locks[-1]
        self.assertEquals(order_id, lock.order_id)
        self.assertEquals(None, lock.order_type)
        self.assertEquals(11000, lock.real_amount)
        self.assertEquals(500, lock.virtual_amount)
        self.assertTrue(isinstance(lock.locking_date, datetime.datetime))

        order_id = 'another %s' % order_id
        order_type = 'hosting'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'order_id': order_id,
            'order_type': order_type,
            'amount': '4',
        }
        self.handle_action('balance_lock', data)
        balance = self.get_balance(operator, self.customer_id)
        self.assertEquals(balance.available_real_amount, -6000)
        self.assertEquals(balance.available_virtual_amount, 100)
        self.assertEquals(balance.locked_amount, 11900)

        locks = self.get_balance_locks(operator, [self.customer_id], order_by='id')
        self.assertEqual(2, len(locks))
        lock = locks[-1]
        self.assertEquals(order_id, lock.order_id)
        self.assertEquals(order_type, lock.order_type)
        self.assertEquals(0, lock.real_amount)
        self.assertEquals(400, lock.virtual_amount)
        self.assertTrue(isinstance(lock.locking_date, datetime.datetime))

        # operator + customer + product is unique
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'order_id': order_id,
            'order_type': 'type',
            'amount': '1',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'balance_lock', data)

        # zero amount locking
        order_id = 'zero amount %s' % order_id
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'order_id': order_id,
            'order_type': 'type',
            'amount': '0',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'balance_lock', data)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'order_id': order_id,
            'order_type': 'type',
            'amount': '0.001',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'balance_lock', data)

        # unknown customer
        order_id = 'unknown customer %s' % order_id
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': 'fake',
            'order_id': order_id,
            'amount': '1.0',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'balance_lock', data)

        # disabled balance
        self.modify_balance(self.test_login, self.test_password, self.customer_id, None, active=False)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'order_id': order_id,
            'amount': '1.0',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'balance_lock', data)
    def test_lock_overdraft_violation(self):
        order_id = 'car wash'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'order_id': order_id,
            'amount': '120.43',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'balance_lock', data)

    def test_locking_order(self):
        operator = self.get_operator_by_login(self.test_login)
        c_id = 'c'
        self.add_balance(self.test_login, self.test_password, c_id, self.currency,
            locking_order=['available_real_amount', 'available_virtual_amount'])
        self.add_receipt(self.test_login, self.test_password, c_id, '50.00')
        self.add_bonus(self.test_login, self.test_password, c_id, '20.00')

        order_id = '0'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': c_id,
            'order_id': order_id,
            'amount': '60.00',
        }
        self.handle_action('balance_lock', data)
        balance = self.get_balance(operator, c_id)
        self.assertEqual(0, balance.available_real_amount)
        self.assertEqual(1000, balance.available_virtual_amount)
        self.assertEqual(6000, balance.locked_amount)

        self.modify_balance(self.test_login, self.test_password, c_id,
            ['available_virtual_amount', 'available_real_amount'])
        self.add_receipt(self.test_login, self.test_password, c_id, '10')

        order_id = '1'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': c_id,
            'order_id': order_id,
            'amount': '16.00',
        }
        self.handle_action('balance_lock', data)
        balance = self.get_balance(operator, c_id)
        self.assertEqual(400, balance.available_real_amount)
        self.assertEqual(0, balance.available_virtual_amount)
        self.assertEqual(7600, balance.locked_amount)

    def test_lock_list(self):
        c_id_0 = 'c0'
        c_id_1 = 'c1'
        self.add_balance(self.test_login, self.test_password, c_id_0, self.currency)
        self.add_balance(self.test_login, self.test_password, c_id_1, self.currency,
            locking_order=['available_virtual_amount'])
        self.add_receipt(self.test_login, self.test_password, c_id_0, '10.0')
        self.add_receipt(self.test_login, self.test_password, c_id_1, '20.0')
        self.add_bonus(self.test_login, self.test_password, c_id_1, '30.0')

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'locks': [
                {'customer_id': c_id_1, 'order_id': '1', 'amount': '8.00'},
                {'customer_id': c_id_0, 'order_id': '2', 'order_type': 'type', 'amount': '9.00'},
                {'customer_id': c_id_1, 'order_id': '3', 'amount': '10.00'},
            ]
        }
        self.handle_action('balance_lock_list', data)

        operator = self.get_operator_by_login(self.test_login)
        balance_locks = self.get_balance_locks(operator, [c_id_0, c_id_1])
        self.assertEqual(3, len(balance_locks))
        lock = balance_locks[0]
        self.assertEqual(0, lock.real_amount, 0)
        self.assertEqual(800, lock.virtual_amount)
        self.assertEqual('1', lock.order_id)
        self.assertEqual(None, lock.order_type)
        lock = balance_locks[1]
        self.assertEqual(900, lock.real_amount)
        self.assertEqual(0, lock.virtual_amount)
        self.assertEqual('2', lock.order_id)
        self.assertEqual('type', lock.order_type)

        lock = balance_locks[2]
        self.assertEqual(0, lock.real_amount)
        self.assertEqual(1000, lock.virtual_amount)
        self.assertEqual('3', lock.order_id)
        self.assertEqual(None, lock.order_type)

        self.modify_balance(self.test_login, self.test_password, c_id_0, None, active=False)
        self.modify_balance(self.test_login, self.test_password, c_id_1, None, active=False)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'locks': [
                {'customer_id': c_id_1, 'order_id': '10', 'amount': '0.01'},
                {'customer_id': c_id_0, 'order_id': '20', 'order_type': 'type', 'amount': '0.01'},
            ]
        }
        self.assertRaises(BalanceDisabled, self.handle_action, 'balance_lock_list', data)

    def test_view_balance_locks(self):
        c_id_0 = 'c0'
        c_id_1 = 'c1'
        self.add_balance(self.test_login, self.test_password, c_id_0, self.currency)
        self.add_balance(self.test_login, self.test_password, c_id_1, self.currency,
            locking_order=['available_virtual_amount'])
        self.add_receipt(self.test_login, self.test_password, c_id_0, '100.0')
        self.add_receipt(self.test_login, self.test_password, c_id_1, '200.0')
        self.add_bonus(self.test_login, self.test_password, c_id_1, '300.0')

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'locks': [
                {'customer_id': c_id_1, 'order_id': '1', 'amount': '80.00'},
                {'customer_id': c_id_0, 'order_id': '1', 'order_type': 'type', 'amount': '90.00'},
                {'customer_id': c_id_1, 'order_id': '3', 'amount': '100.00'},
            ]
        }
        self.handle_action('balance_lock_list', data)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'filter_params': {'customer_ids': [c_id_1]},
            'paging_params': {},
        }
        response = self.handle_action('view_balance_locks', data)
        b_locks = response['balance_locks']
        self.assertEqual(2, len(b_locks))
        for b_l in b_locks:
            self.assertEqual(c_id_1, b_l['customer_id'])

        ord_id = '1'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'filter_params': {'order_id': ord_id},
            'paging_params': {},
        }
        response = self.handle_action('view_balance_locks', data)
        b_locks = response['balance_locks']
        self.assertEqual(2, len(b_locks))
        for b_l in b_locks:
            self.assertEqual(ord_id, b_l['order_id'])

        ord_type = None
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'filter_params': {'order_type': ord_type},
            'paging_params': {},
        }
        response = self.handle_action('view_balance_locks', data)
        b_locks = response['balance_locks']
        self.assertEqual(2, len(b_locks))
        for b_l in b_locks:
            self.assertEqual(ord_type, b_l['order_type'])

        ord_type = 'type'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'filter_params': {'order_type': ord_type},
            'paging_params': {},
        }
        response = self.handle_action('view_balance_locks', data)
        b_locks = response['balance_locks']
        self.assertEqual(1, len(b_locks))
        for b_l in b_locks:
            self.assertEqual(ord_type, b_l['order_type'])

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'locks': [
                {'customer_id': 'fake', 'order_id': '5', 'amount': '1.00'},
            ]
        }
        self.assertRaises(BalanceNotFound, self.handle_action, 'balance_lock_list', data)

        # ordering test
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'filter_params': {'customer_ids': [c_id_1]},
            'paging_params': {},
            'ordering_params': []
        }
        response = self.handle_action('view_balance_locks', data)
        self.assertEqual('ok', response['status'])
        bl_infos = response['balance_locks']
        d = None
        for bl_info in bl_infos:
            cur_d = bl_info['locking_date']
            if d:
                self.assertTrue(d >= cur_d)
            d = cur_d



if __name__ == '__main__':
    unittest.main()