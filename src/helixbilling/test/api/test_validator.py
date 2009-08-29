import unittest

from helixbilling.test.root_test import RootTestCase
from helixbilling.api.validator import validate, ValidationError


class ValidatorTestCase(RootTestCase):
    def test_add_currency(self):
        validate(
            'add_currency',
            {
                'name': 'USD',
                'designation': '$',
                'cent_factor': 100,
            }
        )

    def test_add_currency_invalid(self):
        self.assertRaises(ValidationError, validate,
            'add_currency',
            {
                'name': 'USD',
                'designation': '$',
                'cent_factor': 0,
            }
        )

    def test_create_balance(self):
        validate(
            'create_balance',
            {
                'client_id': 'U-23-52',
                'active': 1,
                'currency_name': 'USD',
                'overdraft_limit': (500, 50),
                'locking_order': ['available_real_amount', 'available_virtual_amount']
            }
        )

    def test_create_balance_invalid(self):
        self.assertRaises(ValidationError, validate,
            'create_balance',
            {
                'client_id': '2',
                'active': 1,
                'currency_name': 'USD',
                'overdraft_limit': (500, 50),
                'locking_order': ['ERROR_HERE']
            }
        )

    def test_modify_balance(self):
        validate(
            'modify_balance',
            {
                'client_id': 'U-23-52',
                'active': 1,
                'overdraft_limit': (500, 50),
                'locking_order': None,
            }
        )

    def test_lock(self):
        validate(
            'lock',
            {
                'client_id': 'id',
                'product_id': 'super-light 555',
                'amount': (60, 00),
            }
        )

    def test_lock_invalid(self):
        self.assertRaises(ValidationError, validate,
            'lock',
            {
                'client_id': 'id',
                'product_id': 'super-light 555',
                'amount': (-60, 00),
            }
        )

    def test_lock_list(self):
        validate(
            'lock_list',
            {
                'locks': [
                    {
                        'client_id': 'id_one',
                        'product_id': 'super-light 555',
                        'amount': (60, 00),
                    },
                    {
                        'client_id': 'id_two',
                        'product_id': 'brb',
                        'amount': (60, 00),
                    }
                ]
            }
        )

    def test_lock_list_invalid(self):
        self.assertRaises(ValidationError, validate,
            'lock_list',
            {
                'locks': [
                    {
                        'client_id': 'id_one',
                        'product_id': 'super-light 555',
                        'amount': (60, 00),
                    },
                    {
                        'client_id': 'id_two',
                        'ERROR_HERE': 'brb',
                        'amount': (60, 00),
                    }
                ]
            }
        )

    def test_unlock_list(self):
        validate(
            'unlock_list',
            {
                'unlocks': [
                    {
                        'client_id': 'id_one',
                        'product_id': 'super-light 555',
                    },
                    {
                        'client_id': 'id_two',
                        'product_id': 'brb',
                    }
                ]
            }
        )

    def test_unlock_list_invalid(self):
        self.assertRaises(ValidationError, validate,
            'unlock_list',
            {
                'unlocks': [
                    {
                        'client_id': 'id_one',
                        'product_id': 'super-light 555',
                    },
                    {
                        'client_id': 'id_two',
                        'product_id': 'brb',
                        'ERROR_HERE': 'bug',
                    }
                ]
            }
        )

    def test_chargeoff_list(self):
        validate(
            'chargeoff_list',
            {
                'chargeoffs': [
                    {
                        'client_id': 'id_one',
                        'product_id': 'super-light 555',
                    },
                    {
                        'client_id': 'id_two',
                        'product_id': 'brb',
                    }
                ]
            }
        )

    def test_chargeoff_list_invalid(self):
        self.assertRaises(ValidationError, validate,
            'chargeoff_list',
            {
                'chargeoff': [
                    {
                        'client_id': 'id_one',
                        'product_id': 'super-light 555',
                    },
                    {
                        'client_id': 'id_two',
                        'product_id': 'brb',
                        'amount': 'BUG',
                    }
                ]
            }
        )



if __name__ == '__main__':
    unittest.main()
