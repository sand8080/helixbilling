import datetime
import unittest

from common import TestCaseWithBalance

from helixcore.mapping import actions
from helixcore.db.wrapper import EmptyResultSetError

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.logic.exceptions import ActionNotAllowedError
from helixbilling.domain.objects import BalanceLock


class ChargeOffTestCase(TestCaseWithBalance):
    @transaction()
    def add_lock(self, lock, curs=None):
        actions.insert(curs, lock)

    def test_chargeoff_ok(self):
        self.balance.available_real_amount = 2500
        self.balance.available_virtual_amount = 1000
        self.balance.locked_amount = 2500
        self.balance.overdraft_limit = 0
        self.balance = self.update_balance(self.balance)

        product_id = '33 cow'
        lock = BalanceLock(
            client_id=self.balance.client_id, #IGNORE:E1101
            product_id=product_id,
            real_amount=1500,
            virtual_amount=1000
        )
        self.add_lock(lock)

        # check lock created, default fields loading
        lock = self._get_lock(self.balance.client_id, product_id)

        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': product_id,
        }
        handle_action('chargeoff', data)

        self.balance = self.reload_balance(self.balance)
        self.assertEquals(0, self.balance.locked_amount)
        self.assertEquals(2500, self.balance.available_real_amount) #IGNORE:E1101
        self.assertEquals(1000, self.balance.available_virtual_amount) #IGNORE:E1101

        # check balance_lock removed
        self.assertRaises(EmptyResultSetError, self._get_lock, self.balance.client_id, data['product_id']) #IGNORE:E1101

        chargeoff = self._get_chargeoff(self.balance.client_id, data['product_id'])
        self.assertEquals(chargeoff.client_id, data['client_id'])
        self.assertEquals(
            chargeoff.real_amount, #INGONRE:E1101
            lock.real_amount #IGNORE:E1101
        )
        self.assertEquals(
            chargeoff.virtual_amount, #IGNORE:E1101
            lock.virtual_amount #IGNORE:E1101
        )
        self.assertEquals(
            chargeoff.locked_date, #IGNORE:E1101
            lock.locked_date #IGNORE:E1101
        )
        self.assertTrue(isinstance(chargeoff.chargeoff_date, datetime.datetime))

    def test_chargeoff_not_locked(self):
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': '555',
        }
        self.assertRaises(ActionNotAllowedError, handle_action, 'chargeoff', data)


if __name__ == '__main__':
    unittest.main()