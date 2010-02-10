import unittest

from helixbilling.test.db_based_test import ServiceTestCase
from helixbilling.validator.validator import ORDER_STATUS_CHARGED_OFF,\
    ORDER_STATUS_LOCKED, ORDER_STATUS_UNKNOWN
from decimal import Decimal


class OrderStatusTestCase(ServiceTestCase):
    def test_order_status(self):
        c_id = 'order_status'
        self.add_balance(self.test_login, self.test_password, c_id, self.currency)
        self.add_receipt(self.test_login, self.test_password, c_id, '15.00')
        self.add_bonus(self.test_login, self.test_password, c_id, '10.00')

        ord_id_locked = '1'
        ord_id_ch_offed = '2'

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'locks': [
                {'customer_id': c_id, 'order_id': ord_id_locked, 'amount': '10.0'},
                {'customer_id': c_id, 'order_id': ord_id_ch_offed, 'amount': '11.0'},
            ]
        }
        self.handle_action('balance_lock_list', data)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'chargeoffs': [
                {'customer_id': c_id, 'order_id': ord_id_ch_offed},
            ]
        }
        self.handle_action('chargeoff_list', data)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': c_id,
            'order_id': ord_id_ch_offed,
        }
        response = self.handle_action('order_status', data)
        self.assertEqual(c_id, response['customer_id'])
        self.assertEqual(ord_id_ch_offed, response['order_id'])
        self.assertEqual(ORDER_STATUS_CHARGED_OFF, response['order_status'])
        self.assertEqual(Decimal('5.00'), Decimal(response['real_amount']))
        self.assertEqual(Decimal('6.00'), Decimal(response['virtual_amount']))
        self.assertNotEqual(None, response['locking_date'])
        self.assertNotEqual(None, response['chargeoff_date'])

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': c_id,
            'order_id': ord_id_locked,
        }
        response = self.handle_action('order_status', data)
        self.assertEqual(c_id, response['customer_id'])
        self.assertEqual(ord_id_locked, response['order_id'])
        self.assertEqual(ORDER_STATUS_LOCKED, response['order_status'])
        self.assertEqual(Decimal('10.00'), Decimal(response['real_amount']))
        self.assertEqual(Decimal('0.00'), Decimal(response['virtual_amount']))
        self.assertNotEqual(None, response['locking_date'])
        self.assertEqual(None, response['chargeoff_date'])

        ord_id = 'fake'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': c_id,
            'order_id': ord_id,
        }
        response = self.handle_action('order_status', data)
        self.assertEqual(c_id, response['customer_id'])
        self.assertEqual(ord_id, response['order_id'])
        self.assertEqual(ORDER_STATUS_UNKNOWN, response['order_status'])
        self.assertEqual(None, response['real_amount'])
        self.assertEqual(None, response['virtual_amount'])
        self.assertEqual(None, response['locking_date'])
        self.assertEqual(None, response['chargeoff_date'])

        c_id = 'fake'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': c_id,
            'order_id': ord_id,
        }
        response = self.handle_action('order_status', data)
        self.assertEqual(c_id, response['customer_id'])
        self.assertEqual(ord_id, response['order_id'])
        self.assertEqual(ORDER_STATUS_UNKNOWN, response['order_status'])
        self.assertEqual(None, response['real_amount'])
        self.assertEqual(None, response['virtual_amount'])
        self.assertEqual(None, response['locking_date'])
        self.assertEqual(None, response['chargeoff_date'])


if __name__ == '__main__':
    unittest.main()