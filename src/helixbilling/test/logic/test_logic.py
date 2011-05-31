import unittest
from decimal import Decimal

from helixcore.db import filters
from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixbilling.test.logic import access_granted #@UnusedImport
from helixbilling.db.dataobject import Currency, Balance
from helixbilling.logic import (decimal_to_cents, cents_to_decimal,
    get_lockable_amounts, compute_locks)
from helixbilling.error import MoneyNotEnough


class LogicTestCase(ActorLogicTestCase):
    def _initial_balance(self):
        return Balance(environment_id=1, user_id=1, currency_id=1,
            real_amount=0, virtual_amount=0, overdraft_limit=0,
            locking_order=None, locked_amount=0, is_active=True)

    def test_get_available_resources(self):
        balance = self._initial_balance()
        balance.real_amount = 10
        balance.virtual_amount = 20
        self.assertEqual({'real_amount': 10, 'virtual_amount': 20},
            get_lockable_amounts(balance))

        balance.real_amount = 17
        balance.virtual_amount = 5
        balance.overdraft_limit = 9
        self.assertEqual({'real_amount': 26, 'virtual_amount': 5},
            get_lockable_amounts(balance))

    def test_compute_locks(self):
        # default locking order
        balance = self._initial_balance()
        balance.real_amount = 10
        balance.virtual_amount = 20
        self.assertEqual({'real_amount': 10, 'virtual_amount': 5},
            compute_locks(balance, 15))

        # defined locking order
        balance.locking_order = ['virtual_amount', 'real_amount']
        self.assertEqual({'virtual_amount': 15, 'real_amount': 0},
            compute_locks(balance, 15))

        balance.locking_order = ['real_amount', 'virtual_amount']
        self.assertEqual({'real_amount': 10, 'virtual_amount': 11},
            compute_locks(balance, 21))

        balance.locking_order = ['virtual_amount']
        self.assertEqual({'virtual_amount': 10},
            compute_locks(balance, 10))

    def test_compute_locks_with_overdraft(self):
        balance = self._initial_balance()
        balance.real_amount = 10
        balance.virtual_amount = 20
        balance.overdraft_limit = 10
        balance.locking_order = ['virtual_amount', 'real_amount']

        self.assertEqual({'real_amount': 15, 'virtual_amount': 20},
            compute_locks(balance, 35))

        balance.locking_order = ['real_amount', 'virtual_amount']
        self.assertEqual({'real_amount': 15, 'virtual_amount': 0},
            compute_locks(balance, 15))

    def test_compute_locks_failure(self):
        balance = self._initial_balance()
        balance.real_amount = 10
        balance.virtual_amount = 20
        balance.overdraft_limit = 0
        balance.locking_order = ['virtual_amount', 'real_amount']
        self.assertRaises(MoneyNotEnough, compute_locks, balance, 40)

    def _get_currencies_idx(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id}
        resp = self.get_currencies(**req)
        self.check_response_ok(resp)
        currs = [Currency(**d) for d in resp['currencies']]
        return filters.build_index(currs, idx_field='code')

    def test_decimal_to_cents(self):
        db_currs_idx = self._get_currencies_idx()
        currencies = {'TND': 1000, 'USD': 100, 'CNY': 10, 'MRO': 5, 'JPY': 1}
        amounts = map(Decimal, ['0.06', '0.86', '13.0', '53.01', '1113.36', '03.001', '13.359'])
        expects = {
            'TND': [60, 860, 13000, 53010, 1113360, 3001, 13359],
            'USD': [6, 86, 1300, 5301, 111336, 300, 1335],
            'CNY': [0, 8, 130, 530, 11133, 30, 133],
            'MRO': [0, 8, 65, 265, 5568, 15, 68],
            'JPY': [0, 0, 13, 53, 1113, 03, 13],
        }
        for code, cent_factor in currencies.items():
            db_currency = db_currs_idx[code]
            self.assertEqual(cent_factor, db_currency.cent_factor)
            actual = [decimal_to_cents(db_currency, amount) for amount in amounts]
            exp_code = db_currency.code
            self.assertEqual(expects[exp_code], actual)

    def test_cents_to_decimal(self):
        db_currs_idx = self._get_currencies_idx()
        currencies = {'TND': 1000, 'USD': 100, 'CNY': 10, 'MRO': 5, 'JPY': 1}
        amounts = [6, 86, 13000, 53001, 1113036, 3001, 13359]
        expects = {
            'TND': ['0.006', '0.086', '13.0', '53.001', '1113.036', '3.001', '13.359'],
            'USD': ['0.06', '0.86', '130.0', '530.01', '11130.36', '30.01', '133.59'],
            'CNY': ['0.6', '8.6', '1300', '5300.1', '111303.6', '300.1', '1335.9'],
            'MRO': ['1.1', '17.1', '2600', '10600.1', '222607.1', '600.1', '2671.4'],
            'JPY': ['6', '86', '13000', '53001', '1113036', '3001', '13359'],
        }
        for code, cent_factor in currencies.items():
            db_currency = db_currs_idx[code]
            self.assertEqual(cent_factor, db_currency.cent_factor)
            actual = [cents_to_decimal(db_currency, amount) for amount in amounts]
            self.assertEqual(map(Decimal, expects[db_currency.code]), actual)


if __name__ == '__main__':
    unittest.main()