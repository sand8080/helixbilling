import unittest

from common import TestCaseWithBalance

from helixcore.mapping import actions
from helixcore.server.exceptions import ActionNotAllowedError

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.logic import helper


class ChargeoffListTestCase(TestCaseWithBalance):
    @transaction()
    def increase_balance(self, val, curs=None):
        balance = actions.reload(curs, self.balance, for_update=True)
        balance.available_real_amount += val
        actions.update(curs, balance)
        self.balance = balance

    def test_chargeoff_ok(self):
        chargeoff_size = (15, 01)
        chargeoff_data = {
            'login': self.test_login,
            'password': self.test_password,
            'chargeoffs': [
                {
                    'client_id': self.balance.client_id, #IGNORE:E1101
                    'product_id': 'super-light 555',
                },
                {
                    'client_id': self.balance.client_id, #IGNORE:E1101
                    'product_id': 'super-light 556',
                },
                {
                    'client_id': self.balance.client_id, #IGNORE:E1101
                    'product_id': 'super-light 557',
                },
            ]
        }

        balance_increase = 9000
        balance_decrease = 0
        self.increase_balance(balance_increase)
        locked_before = self.balance.locked_amount

        for chargeoff in chargeoff_data['chargeoffs']:
            d = dict(chargeoff, amount=chargeoff_size, login=self.test_login,
                password=self.test_password)
            handle_action('lock', d)
            balance_decrease += helper.compose_amount(self.currency, *chargeoff_size)

        self.balance = self.reload_balance(self.balance)
        self.assertEquals(balance_increase - balance_decrease, self.balance.available_real_amount)
        self.assertEquals(balance_decrease, self.balance.locked_amount)

        handle_action('chargeoff_list', chargeoff_data)

        self.balance = self.reload_balance(self.balance)
        self.assertEquals(balance_increase - balance_decrease, self.balance.available_real_amount)
        self.assertEquals(locked_before, self.balance.locked_amount)

    def test_lock_failure(self):
        chargeoff_data = {
            'login': self.test_login,
            'password': self.test_password,
            'chargeoffs': [
                {
                    'client_id': self.balance.client_id, #IGNORE:E1101
                    'product_id': 'super-light 555',
                },
                {
                    'client_id': self.balance.client_id, #IGNORE:E1101
                    'product_id': 'super-light 556',
                },
            ]
        }
        self.assertRaises(ActionNotAllowedError, handle_action, 'chargeoff_list', chargeoff_data)


if __name__ == '__main__':
    unittest.main()