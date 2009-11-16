import unittest
import datetime

from helixbilling.logic.helper import compute_locks, get_available_resources
from helixcore.server.exceptions import ActionNotAllowedError
from helixbilling.domain.objects import Currency, Balance
from helixbilling.test.root_test import RootTestCase


class HelpersTestCase(RootTestCase):
    def __init__(self, *args, **kwargs): #IGNORE:W0231
        super(HelpersTestCase, self).__init__(*args, **kwargs)
        self.currency = Currency(code='YYY', name='y currency', location='y country', cent_factor=100)

    def test_get_available_resources(self):
        b = Balance(
            active=1, client_id='client_id',
            currency_id=1, #IGNORE:E1103
            created_date=datetime.datetime.now(),
            available_real_amount=10,
            available_virtual_amount=20,
            overdraft_limit=0,
            locking_order=None,
            locked_amount=0
        )
        self.assertEqual(
            {'available_real_amount': 10, 'available_virtual_amount': 20},
            get_available_resources(b)
        )

        b = Balance(
            active=1, client_id='client_id',
            currency_id=1, #IGNORE:E1103
            created_date=datetime.datetime.now(),
            available_real_amount=17,
            available_virtual_amount=5,
            overdraft_limit=9,
            locking_order=None,
            locked_amount=0
        )
        self.assertEqual(
            {'available_real_amount': 26, 'available_virtual_amount': 5},
            get_available_resources(b)
        )

    def test_compute_locks_default(self):
        b = Balance(
            active=1, client_id='client_id',
            currency_id=-1,
            created_date=datetime.datetime.now(),
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
            active=1, client_id='client_id',
            currency_id=-1,
            created_date=datetime.datetime.now(),
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
            active=1, client_id='client_id',
            currency_id=-1,
            created_date=datetime.datetime.now(),
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
            active=1, client_id='client_id',
            currency_id=-1,
            created_date=datetime.datetime.now(),
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
            active=1, client_id='client_id',
            currency_id=-1,
            created_date=datetime.datetime.now(),
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
            active=1, client_id='client_id',
            currency_id=-1,
            created_date=datetime.datetime.now(),
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
            active=1, client_id='Flatter',
            currency_id=-1,
            created_date=datetime.datetime.now(),
            available_real_amount=10,
            available_virtual_amount=20,
            overdraft_limit=0,
            locking_order=['available_virtual_amount', 'available_real_amount'],
            locked_amount=0
        )
        self.assertRaises(ActionNotAllowedError, compute_locks, self.currency, b, 40)

        b = Balance(
            active=1, client_id='Flatter',
            currency_id=-1,
            created_date=datetime.datetime.now(),
            available_real_amount=10,
            available_virtual_amount=20,
            overdraft_limit=10,
            locking_order=['available_virtual_amount', 'available_real_amount'],
            locked_amount=0
        )
        self.assertRaises(ActionNotAllowedError, compute_locks, self.currency, b, 41)


if __name__ == '__main__':
    unittest.main()