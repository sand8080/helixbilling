import unittest

from helixcore.db.wrapper import EmptyResultSetError

from common import TestCaseWithBalance
from helixbilling.logic.actions import handle_action
from helixbilling.logic.helper import decompose_amount


class BalanceTestCase(TestCaseWithBalance):
    def test_create_balance(self):
        self.create_balance('U-23-52', self.currency, active=1)
        self.create_balance('U-23-53', self.currency, active=1, overdraft_limit=(500, 60))

    def test_modify_balance(self):
        client_id='U-23-52'
        locking_order = ['available_real_amount']
        balance = self.create_balance(client_id, self.currency, active=1,
            overdraft_limit=(999, 99), locking_order=locking_order)
        self.assertEquals(balance.locking_order, locking_order)

        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': client_id,
            'new_active': 0,
            'new_overdraft_limit': (5, 77),
            'new_locking_order': None,
        }
        handle_action('modify_balance', data)
        manager = self.get_billing_manager_by_login(self.test_billing_manager_login)
        balance = self._get_balance(data['client_id'])
        self.assertEqual(manager.id, balance.billing_manager_id)

        currency = self.get_currency_by_balance(balance)
        self.assertEquals(data['new_overdraft_limit'], decompose_amount(currency, balance.overdraft_limit))
        self.assertEquals(data['new_active'], balance.active)
        self.assertEquals(data['new_locking_order'], balance.locking_order)

    def test_delete_balance(self):
        client_id = 'cli 54'
        self.create_balance(client_id, self.currency)
        handle_action('delete_balance', {'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password, 'client_id': client_id})
        self.assertRaises(EmptyResultSetError, self._get_balance, client_id)

    def test_not_owned_balance_access(self):
        client_id = 'client 34'
        self.create_balance(client_id, self.currency)
        login = 'evil manager'
        password = 'lalala'
        self.add_billing_manager(login, password)
        data = {'login': login, 'password': password, 'client_id': client_id, 'new_active': 0}
        self.assertRaises(EmptyResultSetError, handle_action, 'modify_balance', data)

    def test_create_balance_failure(self):
        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': 52,
            'active': 1,
            'currency_code': 'USD',
            'overdraft_limit': (500, 0),
            'locking_order': ['available_real_amount'],
            'FAKE': 'ERROR',
        }
        self.assertRaises(TypeError, handle_action, 'create_balance', data)


if __name__ == '__main__':
    unittest.main()