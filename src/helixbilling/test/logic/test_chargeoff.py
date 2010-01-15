import datetime
import unittest

from common import TestCaseWithBalance

from helixcore.db.wrapper import EmptyResultSetError
from helixcore.server.exceptions import ActionNotAllowedError

from helixbilling.logic.actions import handle_action


class ChargeOffTestCase(TestCaseWithBalance):
    def test_chargeoff_ok(self):
        self.balance.available_real_amount = 1500
        self.balance.available_virtual_amount = 1500
        self.balance.locked_amount = 0
        self.balance.overdraft_limit = 0
        self.balance = self.update_balance(self.balance)

        product_id = '33 cow'
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': self.balance.client_id,
            'product_id': product_id,
            'amount': (25, 00),
        }
        handle_action('lock', data)

        # check lock created, default fields loading
        lock = self._get_lock(self.balance.client_id, product_id)

        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': product_id,
        }
        handle_action('chargeoff', data)

        self.balance = self.reload_balance(self.balance)
        self.assertEquals(0, self.balance.locked_amount)
        self.assertEquals(0, self.balance.available_real_amount)
        self.assertEquals(500, self.balance.available_virtual_amount)

        # check balance_lock removed
        self.assertRaises(EmptyResultSetError, self._get_lock, self.balance.client_id, data['product_id'])

        chargeoff = self._get_chargeoff(self.balance.client_id, data['product_id'])
        self.assertEquals(chargeoff.client_id, data['client_id'])
        self.assertEquals(chargeoff.real_amount, lock.real_amount)
        self.assertEquals(chargeoff.virtual_amount, lock.virtual_amount)
        self.assertEquals(chargeoff.locked_date, lock.locked_date)
        self.assertTrue(isinstance(chargeoff.chargeoff_date, datetime.datetime))

    def test_chargeoff_not_locked(self):
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': self.balance.client_id,
            'product_id': '555',
        }
        self.assertRaises(ActionNotAllowedError, handle_action, 'chargeoff', data)


if __name__ == '__main__':
    unittest.main()