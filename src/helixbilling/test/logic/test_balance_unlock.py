import unittest

from helixcore.server.exceptions import ActionNotAllowedError

from helixbilling.test.db_based_test import ServiceTestCase
from helixcore.server.errors import RequestProcessingError
from helixbilling.error import BalanceNotFound, BalanceDisabled


class BalanceUnlockTestCase(ServiceTestCase):
    customer_id = 'unlocker'

    def setUp(self):
        super(BalanceUnlockTestCase, self).setUp()
        self.add_balance(self.test_login, self.test_password, self.customer_id, self.currency,
            overdraft_limit='60.00')
        self.add_receipt(self.test_login, self.test_password, self.customer_id, '50.00')
        self.add_bonus(self.test_login, self.test_password, self.customer_id, '10.00')

    def test_balance_unlock(self):
        order_id = '0'
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
        self.assertEquals(balance.real_amount, -6000)
        self.assertEquals(balance.virtual_amount, 500)
        self.assertEquals(balance.locked_amount, 11500)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'order_id': order_id,
        }
        self.handle_action('balance_unlock', data)
        balance = self.get_balance(operator, self.customer_id)
        self.assertEquals(balance.real_amount, 5000)
        self.assertEquals(balance.virtual_amount, 1000)
        self.assertEquals(balance.locked_amount, 0)

        balance_locks = self.get_balance_locks(operator, [self.customer_id], order_id=order_id)
        self.assertEqual(0, len(balance_locks))

        # unknown customer
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': 'fake',
            'order_id': '1',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'balance_unlock', data)

        # unknown order
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'order_id': 'fake',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'balance_unlock', data)

        # disabled balance
        order_id = '10'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'order_id': order_id,
            'amount': '0.01',
        }
        self.handle_action('balance_lock', data)
        self.modify_balance(self.test_login, self.test_password, self.customer_id, None, active=False)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'order_id': order_id,
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'balance_unlock', data)

    def test_balance_unlock_list(self):
        c_id_0 = 'c0'
        c_id_1 = 'c1'
        self.add_balance(self.test_login, self.test_password, c_id_0, self.currency)
        self.add_balance(self.test_login, self.test_password, c_id_1, self.currency,
            locking_order=['virtual_amount'])
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
        balance_0 = self.get_balance(operator, c_id_0)
        balance_1 = self.get_balance(operator, c_id_1)

        self.assertEquals(balance_0.real_amount, 100)
        self.assertEquals(balance_0.virtual_amount, 0)
        self.assertEquals(balance_0.locked_amount, 900)

        self.assertEquals(balance_1.real_amount, 2000)
        self.assertEquals(balance_1.virtual_amount, 1200)
        self.assertEquals(balance_1.locked_amount, 1800)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'unlocks': [
                {'customer_id': c_id_1, 'order_id': '1'},
                {'customer_id': c_id_0, 'order_id': '2'},
                {'customer_id': c_id_1, 'order_id': '3'},
            ]
        }
        self.handle_action('balance_unlock_list', data)

        balance_locks = self.get_balance_locks(operator, [self.customer_id])
        self.assertEqual(0, len(balance_locks))

        # unknown order
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'unlocks': [
                {'customer_id': c_id_1, 'order_id': 'fake'},
            ]
        }
        self.assertRaises(ActionNotAllowedError, self.handle_action, 'balance_unlock_list', data)

        # unknown customer
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'unlocks': [
                {'customer_id': 'fake', 'order_id': '1'},
            ]
        }
        self.assertRaises(BalanceNotFound, self.handle_action, 'balance_unlock_list', data)

        # disabled balances
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'locks': [
                {'customer_id': c_id_1, 'order_id': '10', 'amount': '0.01'},
                {'customer_id': c_id_0, 'order_id': '20', 'order_type': 'type', 'amount': '0.01'},
            ]
        }
        self.handle_action('balance_lock_list', data)
        self.modify_balance(self.test_login, self.test_password, c_id_0, None, active=False)
        self.modify_balance(self.test_login, self.test_password, c_id_1, None, active=False)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'unlocks': [
                {'customer_id': c_id_1, 'order_id': '10'},
                {'customer_id': c_id_0, 'order_id': '20'},
            ]
        }
        self.assertRaises(BalanceDisabled, self.handle_action, 'balance_unlock_list', data)


if __name__ == '__main__':
    unittest.main()