import unittest
import datetime
from decimal import Decimal

from helixcore.server.exceptions import ActionNotAllowedError

from helixbilling.logic.helper import (decimal_to_cents, cents_to_decimal, compute_locks,
    get_lockable_amounts)
from helixbilling.domain.objects import Balance
from helixbilling.test.logic.common import TestCaseWithCurrency


class HelpersTestCase(TestCaseWithCurrency):
    def test_get_available_resources(self):
        b = Balance(
            active=1, customer_id='customer_id',
            currency_id=1, #IGNORE:E1103
            creation_date=datetime.datetime.now(),
            available_real_amount=10,
            available_virtual_amount=20,
            overdraft_limit=0,
            locking_order=None,
            locked_amount=0
        )
        self.assertEqual(
            {'available_real_amount': 10, 'available_virtual_amount': 20},
            get_lockable_amounts(b)
        )

        b = Balance(
            active=1, customer_id='customer_id',
            currency_id=1,
            creation_date=datetime.datetime.now(),
            available_real_amount=17,
            available_virtual_amount=5,
            overdraft_limit=9,
            locking_order=None,
            locked_amount=0
        )
        self.assertEqual(
            {'available_real_amount': 26, 'available_virtual_amount': 5},
            get_lockable_amounts(b)
        )

    def test_compute_locks_default(self):
        b = Balance(
            active=1, customer_id='customer_id',
            currency_id=-1,
            creation_date=datetime.datetime.now(),
            available_real_amount=10,
            available_virtual_amount=20,
            overdraft_limit=0,
            locking_order=None,
            locked_amount=0
        )
        self.assertEqual(
            {'available_real_amount': 10, 'available_virtual_amount': 5},
            compute_locks(self.currency, b, 15)
        )

    def test_compute_locks(self):
        b = Balance(
            active=1, customer_id='customer_id',
            currency_id=-1,
            creation_date=datetime.datetime.now(),
            available_real_amount=10,
            available_virtual_amount=20,
            overdraft_limit=0,
            locking_order=['available_virtual_amount', 'available_real_amount'],
            locked_amount=0
        )
        self.assertEqual(
            {'available_virtual_amount': 15, 'available_real_amount': 0},
            compute_locks(self.currency, b, 15)
        )

        b = Balance(
            active=1, customer_id='customer_id',
            currency_id=-1,
            creation_date=datetime.datetime.now(),
            available_real_amount=10,
            available_virtual_amount=20,
            overdraft_limit=0,
            locking_order=['available_virtual_amount', 'available_real_amount'],
            locked_amount=0
        )
        self.assertEqual(
            {'available_real_amount': 1, 'available_virtual_amount': 20},
            compute_locks(self.currency, b, 21)
        )

        b = Balance(
            active=1, customer_id='customer_id',
            currency_id=-1,
            creation_date=datetime.datetime.now(),
            available_real_amount=10,
            available_virtual_amount=20,
            overdraft_limit=0,
            locking_order=['available_virtual_amount'],
            locked_amount=0
        )
        self.assertEqual(
            {'available_virtual_amount': 10},
            compute_locks(self.currency, b, 10)
        )

    def test_compute_locks_with_overdraft(self):
        b = Balance(
            active=1, customer_id='customer_id',
            currency_id=-1,
            creation_date=datetime.datetime.now(),
            available_real_amount=10,
            available_virtual_amount=20,
            overdraft_limit=10,
            locking_order=['available_virtual_amount', 'available_real_amount'],
            locked_amount=0
        )
        self.assertEqual(
            {'available_real_amount': 15, 'available_virtual_amount': 20},
            compute_locks(self.currency, b, 35)
        )

        b = Balance(
            active=1, customer_id='customer_id',
            currency_id=-1,
            creation_date=datetime.datetime.now(),
            available_real_amount=10,
            available_virtual_amount=0,
            overdraft_limit=10,
            locking_order=['available_virtual_amount', 'available_real_amount'],
            locked_amount=0
        )
        self.assertEqual(
            {'available_real_amount': 15, 'available_virtual_amount': 0},
            compute_locks(self.currency, b, 15)
        )

    def test_compute_locks_failure(self):
        b = Balance(
            active=1, customer_id='Flatter',
            currency_id=-1,
            creation_date=datetime.datetime.now(),
            available_real_amount=10,
            available_virtual_amount=20,
            overdraft_limit=0,
            locking_order=['available_virtual_amount', 'available_real_amount'],
            locked_amount=0
        )
        self.assertRaises(ActionNotAllowedError, compute_locks, self.currency, b, 40)

        b = Balance(
            active=1, customer_id='Flatter',
            currency_id=-1,
            creation_date=datetime.datetime.now(),
            available_real_amount=10,
            available_virtual_amount=20,
            overdraft_limit=10,
            locking_order=['available_virtual_amount', 'available_real_amount'],
            locked_amount=0
        )
        self.assertRaises(ActionNotAllowedError, compute_locks, self.currency, b, 41)

# >>> to del
#    def test_compose_amount(self):
#        currencies = {'TND': 1000, 'USD': 100, 'CNY': 10, 'MRO': 5, 'JPY': 1}
#        amounts = [(0, 6), (0, 86), (13, 0), (53, 01), (1113, 36), (03, 001), (13, 359)]
#        expects = {
#            'TND': [6, 86, 13000, 53001, 1113036, 3001, 13359],
#            'USD': [6, 86, 1300, 5301, 111336, 301, 1659],
#            'CNY': [6, 86, 130, 531, 11166, 31, 489],
#            'MRO': [6, 86, 65, 266, 5601, 16, 424],
#            'JPY': [6, 86, 13, 54, 1149, 4, 372],
#        }
#        for code, cent_factor in currencies.items():
#            currency = self._get_currency(code)
#            self.assertEqual(cent_factor, currency.cent_factor)
#            actual = [compose_amount(currency, *amount) for amount in amounts]
#            self.assertEqual(expects[currency.code], actual)
#
#    def test_decompose_amount(self):
#        currencies = {'TND': 1000, 'USD': 100, 'CNY': 10, 'MRO': 5, 'JPY': 1}
#        amounts = [6, 86, 13000, 53001, 1113036, 3001, 13359]
#        expects = {
#            'TND': [(0, 6), (0, 86), (13, 0),    (53, 1),    (1113, 36),   (3, 1),    (13, 359)],
#            'USD': [(0, 6), (0, 86), (130, 0),   (530, 1),   (11130, 36),  (30, 1),   (133, 59)],
#            'CNY': [(0, 6), (8, 6),  (1300, 0),  (5300, 1),  (111303, 6),  (300, 1),  (1335, 9)],
#            'MRO': [(1, 1), (17, 1), (2600, 0),  (10600, 1), (222607, 1),  (600, 1),  (2671, 4)],
#            'JPY': [(6, 0), (86, 0), (13000, 0), (53001, 0), (1113036, 0), (3001, 0), (13359, 0)],
#        }
#        for code, cent_factor in currencies.items():
#            currency = self._get_currency(code)
#            self.assertEqual(cent_factor, currency.cent_factor)
#            actual = [decompose_amount(currency, amount) for amount in amounts]
#            self.assertEqual(expects[currency.code], actual)
# <<< to del

    def test_decimal_to_cents(self):
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
            currency = self._get_currency(code)
            self.assertEqual(cent_factor, currency.cent_factor)
            actual = [decimal_to_cents(currency, amount) for amount in amounts]
            self.assertEqual(expects[currency.code], actual)

    def test_cents_to_decimal(self):
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
            currency = self._get_currency(code)
            self.assertEqual(cent_factor, currency.cent_factor)
            actual = [cents_to_decimal(currency, amount) for amount in amounts]
            self.assertEqual(map(Decimal, expects[currency.code]), actual)


if __name__ == '__main__':
    unittest.main()