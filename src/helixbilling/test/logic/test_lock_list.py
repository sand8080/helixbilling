import datetime
import unittest

from common import TestCaseWithBalance

from helixcore.mapping.actions import insert, get, reload, update
from helixcore.db.wrapper import EmptyResultSetError

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.logic.exceptions import ActionNotAllowedError, DataIntegrityError
from helixbilling.domain.objects import Currency, Balance


class LockTestCase(TestCaseWithBalance):
    @transaction()
    def increase_balance(self, val, curs=None):
        balance = reload(curs, self.balance, for_update=True)
        balance.available_amount += val
        update(curs, balance)
        self.balance = balance #IGNORE:W0201

    @transaction()
    def reload_balance(self, curs=None):
        self.balance = reload(curs, self.balance, for_update=True)

    def test_lock_ok(self):
        self.reload_balance()
        available_before = self.balance.available_amount
        locked_before = self.balance.locked_amount
        increase = 9000
        self.increase_balance(increase)
        data = {
            'locks': [
                {
                    'client_id': self.balance.client_id, #IGNORE:E1101
                    'product_id': 'super-light 555',
                    'amount': (20, 00),
                },
                {
                    'client_id': self.balance.client_id, #IGNORE:E1101
                    'product_id': 'super-light 556',
                    'amount': (30, 00),
                },
                {
                    'client_id': self.balance.client_id, #IGNORE:E1101
                    'product_id': 'super-light 557',
                    'amount': (40, 00),
                },
            ]
        }
        handle_action('lock_list', data)
        self.reload_balance()
        self.assertEquals(available_before, increase + self.balance.available_amount)
        self.assertEquals(locked_before, increase - self.balance.locked_amount)

#    def test_lock_overdraft_violation(self):
#        data = {
#            'client_id': self.balance.client_id, #IGNORE:E1101
#            'product_id': 'lucky boy',
#            'amount': (120, 43),
#        }
#        self.assertRaises(ActionNotAllowedError, handle_action, 'lock', data)
#
#    def test_unlock_ok(self):
#        data = {
#            'client_id': self.balance.client_id, #IGNORE:E1101
#            'product_id': '555',
#            'amount': (60, 00),
#        }
#        handle_action('lock', data)
#
#        del data['amount']
#        handle_action('unlock', data)
#
#        balance = self._get_balance(data['client_id'])
#
#        self.assertEquals(balance.available_amount, 5000)
#        self.assertEquals(balance.locked_amount, 0)
#        self.assertRaises(EmptyResultSetError, self._get_lock, self.balance.client_id, data['product_id']) #IGNORE:E1101
#
#    def test_unlock_inexistent(self):
#        data = {
#            'client_id': self.balance.client_id, #IGNORE:E1101
#            'product_id': '555',
#            'amount': (60, 00),
#        }
#        handle_action('lock', data)
#
#        del data['amount']
#        data['product_id'] = '444'
#        self.assertRaises(DataIntegrityError, handle_action, 'unlock', data)

if __name__ == '__main__':
    unittest.main()