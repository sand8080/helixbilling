from decimal import Decimal
from helixbilling.error import BalanceNotFound
import unittest

from helixcore.db.wrapper import EmptyResultSetError

from common import TestCaseWithBalance
from helixbilling.logic.helper import decompose_amount, decimal_to_cents, cents_to_decimal
from helixcore.server.errors import RequestProcessingError


class BalanceTestCase(TestCaseWithBalance):
#    def test_add_balance(self):
#        self.add_balance('U-23-52', self.currency, active=True)
#        self.add_balance('U-23-53', self.currency, active=True, overdraft_limit='500.60')
#        self.assertRaises(RequestProcessingError, self.add_balance, 'U-23-53', self.currency,
#            active=True)
#
#    def test_modify_balance(self):
#        customer_id='U-23-52'
#        self.add_balance(customer_id, self.currency, active=True, overdraft_limit='999.99',
#            locking_order=['available_real_amount'])
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'customer_id': customer_id,
#            'new_active': False,
#            'new_overdraft_limit': '5.77',
#            'new_locking_order': None,
#        }
#        self.handle_action('modify_balance', data)
#        operator = self.get_operator_by_login(self.test_login)
#        balance = self._get_balance(customer_id)
#        currency = self._get_currency_by_balance(balance)
#        self.assertEqual(operator.id, balance.operator_id)
#        self.assertEqual(
#            Decimal(data['new_overdraft_limit']),
#            cents_to_decimal(currency, balance.overdraft_limit)
#        )
#        self.assertEqual(data['new_active'], balance.active)
#        self.assertEqual(data['new_locking_order'], balance.locking_order)
#
#    def test_delete_balance(self):
#        customer_id = 'c'
#        self.add_balance(customer_id, self.currency)
#        self.handle_action('delete_balance', {'login': self.test_login, 'password': self.test_password,
#            'customer_id': customer_id})
#        self.assertRaises(EmptyResultSetError, self._get_balance, customer_id)
#
#    def test_get_balance(self):
#        c_id = 'cu54'
#        self.add_balance(c_id, self.currency)
#        response = self.handle_action('get_balance', {
#            'login': self.test_login,
#            'password': self.test_password,
#            'customer_id': c_id
#        })
#        self.assertEqual('ok', response['status'])
#        self.assertEqual(True, response['active'])
#        self.assertEqual(c_id, response['customer_id'])
#        self.assertEqual(self.currency.code, response['currency_code']) #IGNORE:E1103
#        self.assertEqual(Decimal('0.0'), Decimal(response['available_real_amount']))
#        self.assertEqual(Decimal('0.0'), Decimal(response['available_virtual_amount']))
#        self.assertEqual(Decimal('0.0'), Decimal(response['overdraft_limit']))
#        self.assertEqual(Decimal('0.0'), Decimal(response['locked_amount']))
#        self.assertEqual(None, response['locking_order'])
#
#    def test_not_owned_balance_access(self):
#        customer_id = 'client 34'
#        self.add_balance(customer_id, self.currency)
#        login = 'evil operator'
#        password = 'lalala'
#        self.add_operator(login, password)
#        data = {'login': login, 'password': password, 'customer_id': customer_id, 'new_active': False}
#        self.assertRaises(RequestProcessingError, self.handle_action, 'modify_balance', data)
#        data = {'login': login, 'password': password, 'customer_id': customer_id}
#        self.assertRaises(RequestProcessingError, self.handle_action, 'get_balance', data)

    def test_view_balances(self):
        c_ids = list('abcdef')
        for idx, c_id in enumerate(c_ids):
            self.add_balance(c_id, self.currency, overdraft_limit='%s' % idx,
                locking_order=['available_real_amount'])

if __name__ == '__main__':
    unittest.main()