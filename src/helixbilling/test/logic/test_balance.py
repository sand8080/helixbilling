import unittest
from decimal import Decimal

from helixcore.server.errors import RequestProcessingError

from helixbilling.logic.helper import cents_to_decimal
from helixbilling.test.db_based_test import ServiceTestCase
from helixbilling.error import BalanceNotFound


class BalanceTestCase(ServiceTestCase):
    def test_add_balance(self):
        c_id_0 = 'U-23-52'
        c_id_1 = 'U-23-53'
        self.add_balance(self.test_login, self.test_password, c_id_0, self.currency, active=True)
        self.add_balance(self.test_login, self.test_password, c_id_1, self.currency, active=True,
            overdraft_limit='500.60')
        self.assertRaises(RequestProcessingError, self.add_balance, self.test_login, self.test_password,
            c_id_1, self.currency, active=True)

        login = 'another'
        password = 'qazwsx'
        self.add_operator(login, password)
        self.add_balance(login, password, c_id_0, self.currency)

    def test_modify_balance(self):
        c_id='U-23-52'
        self.add_balance(self.test_login, self.test_password, c_id, self.currency, active=True,
            overdraft_limit='999.99', locking_order=['available_real_amount'])
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': c_id,
            'new_active': False,
            'new_overdraft_limit': '5.77',
            'new_locking_order': None,
        }
        self.handle_action('modify_balance', data)
        operator = self.get_operator_by_login(self.test_login)
        balance = self.get_balance(operator, c_id)
        self.assertEqual(operator.id, balance.operator_id)
        self.assertEqual(
            Decimal(data['new_overdraft_limit']),
            cents_to_decimal(self.currency, balance.overdraft_limit)
        )
        self.assertEqual(data['new_active'], balance.active)
        self.assertEqual(data['new_locking_order'], balance.locking_order)

    def test_delete_balance(self):
        c_id = 'c'
        self.add_balance(self.test_login, self.test_password, c_id, self.currency)
        self.handle_action('delete_balance', {'login': self.test_login, 'password': self.test_password,
            'customer_id': c_id})
        operator = self.get_operator_by_login(self.test_login)
        self.assertRaises(BalanceNotFound, self.get_balance, operator, c_id)

    def test_not_owned_balance_access(self):
        c_id = 'client 34'
        self.add_balance(self.test_login, self.test_password, c_id, self.currency)
        login = 'evil operator'
        password = 'lalala'
        self.add_operator(login, password)
        data = {'login': login, 'password': password, 'c_id': c_id, 'new_active': False}
        self.assertRaises(RequestProcessingError, self.handle_action, 'modify_balance', data)
        data = {'login': login, 'password': password, 'c_id': c_id}
        self.assertRaises(RequestProcessingError, self.handle_action, 'get_balance', data)

    def test_get_balance(self):
        c_id = 'cu54'
        self.add_balance(self.test_login, self.test_password, c_id, self.currency)
        response = self.handle_action('get_balance', {
            'login': self.test_login,
            'password': self.test_password,
            'customer_id': c_id
        })
        self.assertEqual(True, response['active'])
        self.assertEqual(c_id, response['customer_id'])
        self.assertEqual(self.currency.code, response['currency_code']) #IGNORE:E1103
        self.assertEqual(Decimal('0.0'), Decimal(response['available_real_amount']))
        self.assertEqual(Decimal('0.0'), Decimal(response['available_virtual_amount']))
        self.assertEqual(Decimal('0.0'), Decimal(response['overdraft_limit']))
        self.assertEqual(Decimal('0.0'), Decimal(response['locked_amount']))
        self.assertEqual(None, response['locking_order'])

    def test_view_balances(self):
        l, p = 't', 'p'
        self.add_operator('t', 'p')
        c_ids = list('abcdef')
        for idx, c_id in enumerate(c_ids):
            self.add_balance(l, p, c_id, self.currency, overdraft_limit='%s' % idx,
                locking_order=['available_real_amount'])
        expected_c_ids = c_ids[:3]
        response = self.handle_action('view_balances', {
            'login': l, 'password': p,
            'filter_params': {'customer_ids': expected_c_ids},
            'paging_params': {},
        })
        b_info = response['balances']
        self.assertEqual(len(expected_c_ids), len(b_info))
        self.assertEqual(response['total'], len(expected_c_ids))
        actual_c_ids = [i['customer_id'] for i in b_info]
        self.assertEqual(sorted(actual_c_ids), sorted(expected_c_ids))

        offset = 2
        expected_c_ids = c_ids[offset:]
        response = self.handle_action('view_balances', {
            'login': l, 'password': p,
            'filter_params': {},
            'paging_params': {'offset': offset},
        })
        b_info = response['balances']
        self.assertEqual(len(expected_c_ids), len(b_info))
        self.assertEqual(response['total'], len(c_ids))
        actual_c_ids = [i['customer_id'] for i in b_info]
        self.assertEqual(sorted(actual_c_ids), sorted(expected_c_ids))

        offset = 1
        limit = 2
        expected_c_ids = c_ids[offset:offset + limit]
        response = self.handle_action('view_balances', {
            'login': l, 'password': p,
            'filter_params': {},
            'paging_params': {'offset': offset, 'limit': 2}
        })
        b_info = response['balances']
        self.assertEqual(len(expected_c_ids), len(b_info))
        self.assertEqual(response['total'], len(c_ids))
        actual_c_ids = [i['customer_id'] for i in b_info]
        self.assertEqual(sorted(actual_c_ids), sorted(expected_c_ids))


if __name__ == '__main__':
    unittest.main()