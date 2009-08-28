import datetime
import unittest

from common import TestCaseWithBalance

from helixcore.mapping.actions import insert, update
from helixcore.db.wrapper import EmptyResultSetError

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.logic.exceptions import ActionNotAllowedError, DataIntegrityError
from helixbilling.domain.objects import Currency, Balance


class LockTestCase(TestCaseWithBalance):
    @transaction()
    def setUp(self, curs=None): # IGNORE:W0221
        super(LockTestCase, self).setUp()
        self.balance.available_real_amount = 5000
        self.balance.available_virtual_amount = 1000
        self.balance.overdraft_limit = 6000
        update(curs, self.balance)

#    def test_lock_ok(self):
#        data = {
#            'client_id': self.balance.client_id, #IGNORE:E1101
#            'product_id': 'super-light 555',
#            'amount': (60, 00),
#        }
#        handle_action('lock', data)
#        balance = self._get_balance(data['client_id'])
#
#        self.assertEquals(balance.available_real_amount, -1000)
#        self.assertEquals(balance.locked_amount, 6000)
#
#        lock = self._get_lock(self.balance.client_id, data['product_id']) #IGNORE:E1101
#        self.assertEquals(lock.client_id, data['client_id'])
#        self.assertEquals(lock.real_amount, 6000)
#        self.assertTrue(isinstance(lock.locked_date, datetime.datetime))
#
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
#        self.assertEquals(balance.available_real_amount, 5000)
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

    def test_locking_order(self):
        self.balance.locking_order = ['available_real_amount', 'available_virtual_amount']
        self.balance.available_real_amount = 5000
        self.balance.available_virtual_amount = 2000
        self.update_balance(self.balance)

        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': '555',
            'amount': (60, 00),
        }
        handle_action('lock', data)


if __name__ == '__main__':
    unittest.main()