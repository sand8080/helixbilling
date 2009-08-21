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
            }
        )

    def test_create_balance_invalid(self):
        self.assertRaises(ValidationError, validate,
            'create_balance',
            {
                'client_id': 2,
                'active': 1,
                'currency_name': 'USD',
                'overdraft_limit': (500, 50),
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


if __name__ == '__main__':
    unittest.main()
