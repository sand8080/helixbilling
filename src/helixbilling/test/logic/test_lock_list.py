import unittest

from common import TestCaseWithBalance

from helixcore.mapping import actions

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.logic.exceptions import ActionNotAllowedError
from helixbilling.logic.helper import compose_amount


class LockListTestCase(TestCaseWithBalance):
    @transaction()
    def increase_balance(self, real_val, virtual_val, curs=None):
        balance = actions.reload(curs, self.balance, for_update=True)
        balance.available_real_amount += real_val
        balance.available_virtual_amount += virtual_val
        actions.update(curs, balance)
        self.balance = balance #IGNORE:W0201

    def get_amount_sum(self, data):
        return reduce(lambda x, y: x + y, [compose_amount(self.currency, '', *d['amount']) for d in data])

    def test_lock_ok(self):
        lock_data = {
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
        balance_real_increase = 5000
        balance_virtual_increase = 4000
        balance_decrease = self.get_amount_sum(lock_data['locks'])

        self.increase_balance(balance_real_increase, balance_virtual_increase)
        available_real_before = self.balance.available_real_amount
        available_virtual_before = self.balance.available_virtual_amount
        locked_before = self.balance.locked_amount

        handle_action('lock_list', lock_data)
        self.balance = self.reload_balance(self.balance)
        self.assertEquals(available_real_before, self.balance.available_real_amount + balance_real_increase)
        self.assertEquals(available_virtual_before, self.balance.available_virtual_amount + balance_virtual_increase)
        self.assertEquals(locked_before, self.balance.locked_amount - balance_decrease)

    def test_unlock_ok(self):
        self.test_lock_ok()
        self.balance = self.reload_balance(self.balance)
        available_real_before = self.balance.available_real_amount
        available_virtual_before = self.balance.available_virtual_amount
        locked_before = self.balance.locked_amount

        unlock_data = {
            'unlocks': [
                {
                    'client_id': self.balance.client_id, #IGNORE:E1101
                    'product_id': 'super-light 555',
                },
                {
                    'client_id': self.balance.client_id, #IGNORE:E1101
                    'product_id': 'super-light 557',
                },
            ]
        }
        handle_action('unlock_list', unlock_data)
        self.balance = self.reload_balance(self.balance)

        self.assertEqual(
            available_real_before + available_virtual_before + locked_before,
            self.balance.available_real_amount + self.balance.available_virtual_amount + self.balance.locked_amount
        )

    def test_lock_failure(self):
        balance_real_increase = 1500
        balance_virtual_increase = 1000
        lock_data = {
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
            ]
        }
        self.increase_balance(balance_real_increase, balance_virtual_increase)
        self.assertRaises(ActionNotAllowedError, handle_action, 'lock_list', lock_data)


if __name__ == '__main__':
    unittest.main()