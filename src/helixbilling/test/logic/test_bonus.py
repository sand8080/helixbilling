import unittest
from decimal import Decimal

from helixbilling.test.db_based_test import ServiceTestCase
from helixcore.server.errors import RequestProcessingError
from helixcore.utils import filter_dict


class BonusTestCase(ServiceTestCase):
    def test_enroll_bonus(self):
        c_id = 'U0'
        self.add_balance(self.test_login, self.test_password, c_id, self.currency)
        self.add_bonus(self.test_login, self.test_password, c_id, '109.01')
        self.assertRaises(RequestProcessingError, self.add_receipt, self.test_login,
            self.test_password, 'fake customer', '109.01')
        self.assertRaises(RequestProcessingError, self.add_receipt, self.test_login,
            self.test_password, c_id, '0.0')
        self.assertRaises(RequestProcessingError, self.add_receipt, self.test_login,
            self.test_password, c_id, '0.001')

    def test_view_receipts(self):
        c_ids = {'U0': 5, 'U1': 1, 'U2': 3, 'U3': 0}
        for c_id, rec_num in c_ids.items():
            self.add_balance(self.test_login, self.test_password, c_id, self.currency)
            for i in xrange(rec_num):
                self.add_bonus(self.test_login, self.test_password, c_id, '%s' % (i + 1))
        response = self.handle_action('view_bonuses', {'login': self.test_login, 'password': self.test_password,
            'filter_params': {}, 'paging_params': {}})
        self.assertEqual(sum(c_ids.values()), response['total'])

        c_ids_slice = filter_dict(c_ids.keys()[2:], c_ids)
        response = self.handle_action('view_bonuses', {'login': self.test_login, 'password': self.test_password,
            'filter_params': {'customer_ids': c_ids_slice.keys()}, 'paging_params': {}})
        self.assertEqual(sum(c_ids_slice.values()), response['total'])
        b_info = response['bonuses']
        for b in b_info:
            self.assertTrue(b['customer_id'] in c_ids_slice.keys())
            self.assertEqual(self.currency.code, b['currency'])

        c_id = 'A0'
        currency = self.get_currencies()[0]
        amount = '15.09'
        self.add_balance(self.test_login, self.test_password, c_id, currency)
        self.add_bonus(self.test_login, self.test_password, c_id, amount)
        response = self.handle_action('view_bonuses', {'login': self.test_login, 'password': self.test_password,
            'filter_params': {'customer_ids': [c_id]}, 'paging_params': {}})
        self.assertEqual(1, response['total'])
        b = response['bonuses'][0]
        self.assertEqual(c_id, b['customer_id'])
        self.assertEqual(currency.code, b['currency'])
        self.assertEqual(Decimal(amount), Decimal(b['amount']))


if __name__ == '__main__':
    unittest.main()