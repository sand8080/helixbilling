import unittest

from helixcore.server.exceptions import ActionNotAllowedError
from helixcore.server.errors import RequestProcessingError
from helixcore.db.wrapper import ObjectNotFound

from helixbilling.test.db_based_test import ServiceTestCase
from helixbilling.error import BalanceNotFound, BalanceDisabled


class ChargeOffTestCase(ServiceTestCase):
    customer_id = 'chargeoff'

    def setUp(self):
        super(ChargeOffTestCase, self).setUp()
        self.add_balance(self.test_login, self.test_password, self.customer_id, self.currency,
            overdraft_limit='60.00')
        self.add_receipt(self.test_login, self.test_password, self.customer_id, '50.00')
        self.add_bonus(self.test_login, self.test_password, self.customer_id, '10.00')

    def test_chargeoff(self):
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
        self.assertEquals(-6000, balance.available_real_amount)
        self.assertEquals(500, balance.available_virtual_amount)
        self.assertEquals(11500, balance.locked_amount)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'order_id': order_id,
        }
        self.handle_action('chargeoff', data)
        balance = self.get_balance(operator, self.customer_id)
        self.assertEquals(-6000, balance.available_real_amount)
        self.assertEquals(500, balance.available_virtual_amount)
        self.assertEquals(0, balance.locked_amount)
        self.assertRaises(ObjectNotFound, self.get_balance_lock, operator, self.customer_id, order_id)

        chargeoff = self.get_chargeoff(operator, self.customer_id, order_id)
        self.assertEqual(self.customer_id, chargeoff.customer_id)
        self.assertEqual(order_id, chargeoff.order_id)
        self.assertEqual(11000, chargeoff.real_amount)
        self.assertEqual(500, chargeoff.virtual_amount)

        # unknown order
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': self.customer_id,
            'order_id': 'fake',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'chargeoff', data)

        # unknown customer
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': 'fake',
            'order_id': '1',
        }
        self.assertRaises(RequestProcessingError, self.handle_action, 'chargeoff', data)

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
        self.assertRaises(RequestProcessingError, self.handle_action, 'chargeoff', data)

    def test_chargeoff_list(self):
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
        balance_0 = self.get_balance(operator, c_id_0)
        balance_1 = self.get_balance(operator, c_id_1)

        self.assertEquals(balance_0.available_real_amount, 100)
        self.assertEquals(balance_0.available_virtual_amount, 0)
        self.assertEquals(balance_0.locked_amount, 900)

        self.assertEquals(balance_1.available_real_amount, 2000)
        self.assertEquals(balance_1.available_virtual_amount, 1200)
        self.assertEquals(balance_1.locked_amount, 1800)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'chargeoffs': [
                {'customer_id': c_id_1, 'order_id': '1'},
                {'customer_id': c_id_0, 'order_id': '2'},
            ]
        }
        self.handle_action('chargeoff_list', data)

        balance_locks = self.get_balance_locks(operator, [c_id_1, c_id_0])
        self.assertEqual(1, len(balance_locks))

        chargeoffs = self.get_chargeoffs(operator, [c_id_1, c_id_0])
        self.assertEqual(2, len(chargeoffs))

        chargeoff_0 = chargeoffs[0]
        self.assertEqual(c_id_1, chargeoff_0.customer_id)
        self.assertEqual('1', chargeoff_0.order_id)
        self.assertEqual(None, chargeoff_0.order_type)
        self.assertEqual(0, chargeoff_0.real_amount)
        self.assertEqual(800, chargeoff_0.virtual_amount)

        chargeoff_1 = chargeoffs[1]
        self.assertEqual(c_id_0, chargeoff_1.customer_id)
        self.assertEqual('2', chargeoff_1.order_id)
        self.assertEqual('type', chargeoff_1.order_type)
        self.assertEqual(900, chargeoff_1.real_amount)
        self.assertEqual(0, chargeoff_1.virtual_amount)

        # unknown order
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'chargeoffs': [
                {'customer_id': c_id_1, 'order_id': 'fake'},
            ]
        }
        self.assertRaises(ActionNotAllowedError, self.handle_action, 'chargeoff_list', data)

        # unknown customer
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'chargeoffs': [
                {'customer_id': 'fake', 'order_id': '1'},
            ]
        }
        self.assertRaises(BalanceNotFound, self.handle_action, 'chargeoff_list', data)

        # disabled balance
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
            'chargeoffs': [
                {'customer_id': c_id_1, 'order_id': '10'},
                {'customer_id': c_id_0, 'order_id': '20'},
            ]
        }
        self.assertRaises(BalanceDisabled, self.handle_action, 'chargeoff_list', data)

    def test_view_chargeoffs(self):
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
                {'customer_id': c_id_1, 'order_id': '4', 'order_type': 'type', 'amount': '100.00'},
            ]
        }
        self.handle_action('balance_lock_list', data)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'chargeoffs': [
                {'customer_id': c_id_1, 'order_id': '1'},
                {'customer_id': c_id_0, 'order_id': '1'},
                {'customer_id': c_id_1, 'order_id': '4'},
            ]
        }
        self.handle_action('chargeoff_list', data)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'filter_params': {'customer_ids': [c_id_1]},
            'paging_params': {},
        }
        response = self.handle_action('view_chargeoffs', data)
        ch_offs = response['chargeoffs']
        self.assertEqual(2, len(ch_offs))
        for ch in ch_offs:
            self.assertEqual(c_id_1, ch['customer_id'])

        ord_id = '1'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'filter_params': {'order_id': ord_id},
            'paging_params': {},
        }
        response = self.handle_action('view_chargeoffs', data)
        ch_offs = response['chargeoffs']
        self.assertEqual(2, len(ch_offs))
        for ch in ch_offs:
            self.assertEqual(ord_id, ch['order_id'])

        ord_type = None
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'filter_params': {'order_type': ord_type},
            'paging_params': {},
        }
        response = self.handle_action('view_chargeoffs', data)
        ch_offs = response['chargeoffs']
        self.assertEqual(1, len(ch_offs))
        for ch in ch_offs:
            self.assertEqual(ord_type, ch['order_type'])

        ord_type = 'type'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'filter_params': {'order_type': ord_type},
            'paging_params': {},
        }
        response = self.handle_action('view_chargeoffs', data)
        ch_offs = response['chargeoffs']
        self.assertEqual(2, len(ch_offs))
        for ch in ch_offs:
            self.assertEqual(ord_type, ch['order_type'])

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'filter_params': {'customer_ids': ['fake0', 'fake1']},
            'paging_params': {},
        }
        response = self.handle_action('view_chargeoffs', data)
        self.assertEqual(0, len(response['chargeoffs']))

        # checking ordering
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'filter_params': {},
            'paging_params': {},
            'ordering_params': [],
        }
        response = self.handle_action('view_chargeoffs', data)
        self.assertEqual('ok', response['status'])
        ch_infos = response['chargeoffs']
        d = None
        for ch_info in ch_infos:
            cur_d = ch_info['chargeoff_date']
            if d:
                self.assertTrue(d >= cur_d)
            d = cur_d


if __name__ == '__main__':
    unittest.main()