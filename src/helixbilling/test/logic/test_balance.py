from decimal import Decimal
from helixbilling.error import BalanceNotFound
import unittest

from helixcore.db.wrapper import EmptyResultSetError

from common import TestCaseWithBalance
from helixbilling.logic.actions import handle_action
from helixbilling.logic.helper import decompose_amount, decimal_to_cents, cents_to_decimal


class BalanceTestCase(TestCaseWithBalance):
#    def test_add_balance(self):
#        self.add_balance('U-23-52', self.currency, active=True)
#        self.add_balance('U-23-53', self.currency, active=True, overdraft_limit='500.60')
#
#    def test_modify_balance(self):
#        client_id='U-23-52'
#        self.add_balance(client_id, self.currency, active=True, overdraft_limit='999.99',
#            locking_order=['available_real_amount'])
#        data = {
#            'login': self.test_login,
#            'password': self.test_password,
#            'client_id': client_id,
#            'new_active': False,
#            'new_overdraft_limit': '5.77',
#            'new_locking_order': None,
#        }
#        handle_action('modify_balance', data)
#        manager = self.get_billing_manager_by_login(self.test_login)
#        balance = self._get_balance(data['client_id'])
#        self.assertEqual(manager.id, balance.billing_manager_id)
#        self.assertEqual(
#            Decimal(data['new_overdraft_limit']),
#            Decimal(balance.overdraft_limit)
#        )
#        self.assertEqual(data['new_active'], balance.active)
#        self.assertEqual(data['new_locking_order'], balance.locking_order)
#
#    def test_delete_balance(self):
#        client_id = 'cli 54'
#        self.add_balance(client_id, self.currency)
#        handle_action('delete_balance', {'login': self.test_login, 'password': self.test_password,
#            'client_id': client_id})
#        self.assertRaises(EmptyResultSetError, self._get_balance, client_id)

    def test_get_balance(self):
        client_id = 'cli 54'
        self.add_balance(client_id, self.currency)
        response = handle_action('get_balance', {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': client_id
        })
        print '###', response
        self.assertRaises(EmptyResultSetError, self._get_balance, client_id)

#    def test_not_owned_balance_access(self):
#        client_id = 'client 34'
#        self.add_balance(client_id, self.currency)
#        login = 'evil manager'
#        password = 'lalala'
#        self.add_billing_manager(login, password)
#        data = {'login': login, 'password': password, 'client_id': client_id, 'new_active': False}
#        self.assertRaises(BalanceNotFound, handle_action, 'modify_balance', data)
#        data = {'login': login, 'password': password, 'client_id': client_id}
#        self.assertRaises(BalanceNotFound, handle_action, 'get_balance', data)


if __name__ == '__main__':
    unittest.main()