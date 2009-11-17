import datetime
import unittest

from helixcore.db.wrapper import EmptyResultSetError

from common import TestCaseWithBalance
from helixbilling.logic.actions import handle_action


class BalanceTestCase(TestCaseWithBalance):
    def test_create_balance(self):
        self.create_balance('U-23-52', self.currency, active=1, overdraft_limit=(500, 60))

#    def test_modify_balance(self):
#        data = {
#            'client_id': 'U-23-52',
#            'active': 1,
#            'currency_name': 'YYY',
#            'overdraft_limit': (500, 0),
#            'locking_order': ['available_real_amount'],
#        }
#        balance = self.create_balance(data)
#        self.assertEquals(balance.locking_order, ['available_real_amount'])
#
#        data = {
#            'client_id': 'U-23-52',
#            'active': 0,
#            'overdraft_limit': (999, 99),
#            'locking_order': None,
#        }
#        handle_action('modify_balance', data)
#        balance = self._get_balance(data['client_id'])
#
#        self.assertEquals(balance.overdraft_limit, 99999)
#        self.assertEquals(balance.active, data['active'])
#        self.assertEquals(balance.locking_order, None)

#    def test_delete_balance(self):
#        client_id = 'cli 54'
#        data = {
#            'client_id': client_id,
#            'active': 1,
#            'currency_name': 'YYY',
#            'overdraft_limit': (500, 0),
#            'locking_order': ['available_real_amount'],
#        }
#        self.create_balance(data)
#
#        data = {'client_id': client_id}
#        handle_action('delete_balance', data)
#        self.assertRaises(EmptyResultSetError, self._get_balance, client_id)
#
#    def test_create_balance_failure(self):
#        data = {
#            'client_id': 52,
#            'active': 1,
#            'currency_name': 'YYY',
#            'overdraft_limit': (500, 0),
#            'locking_order': ['available_real_amount'],
#            'FAKE': 'ERROR',
#        }
#        self.assertRaises(TypeError, handle_action, 'create_balance', data)


if __name__ == '__main__':
    unittest.main()