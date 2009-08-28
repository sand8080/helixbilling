import unittest

from common import TestCaseWithBalance

from helixcore.mapping import actions

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.logic.exceptions import ActionNotAllowedError
from helixbilling.logic.helper import compose_amount


class LockListTestCase(TestCaseWithBalance):
    @transaction()
    def increase_balance(self, val, curs=None):
        balance = actions.reload(curs, self.balance, for_update=True)
        balance.available_real_amount += val
        actions.update(curs, balance)
        self.balance = balance #IGNORE:W0201

    @transaction()
    def reload_balance(self, curs=None):
        self.balance = actions.reload(curs, self.balance, for_update=True)

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
        balance_increase = 9000
        balance_decrease = self.get_amount_sum(lock_data['locks'])

        self.increase_balance(balance_increase)
        available_before = self.balance.available_real_amount
        locked_before = self.balance.locked_amount

        handle_action('lock_list', lock_data)
        self.reload_balance()
        self.assertEquals(available_before, self.balance.available_real_amount + balance_decrease)
        self.assertEquals(locked_before, self.balance.locked_amount - balance_decrease)

    def test_unlock_ok(self):
        self.test_lock_ok()
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
        self.reload_balance()
        available_before = self.balance.available_real_amount
        locked_before = self.balance.locked_amount
        handle_action('unlock_list', unlock_data)
        self.reload_balance()
        self.assertEqual(
            available_before + locked_before,
            self.balance.available_real_amount + self.balance.locked_amount
        )

    def get_amount_sum(self, data):
        return reduce(lambda x, y: x + y, [compose_amount(self.currency, '', *d['amount']) for d in data])

    def test_lock_failure(self):
        balance_increase = 2500
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
        self.increase_balance(balance_increase)
        self.assertRaises(ActionNotAllowedError, handle_action, 'lock_list', lock_data)


if __name__ == '__main__':
    unittest.main()