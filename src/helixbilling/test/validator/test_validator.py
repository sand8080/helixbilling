import unittest

from helixcore.server.api import Api
from helixcore.server.exceptions import ValidationError

from helixbilling.test.root_test import RootTestCase
from helixbilling.validator.validator import api_scheme


class ValidatorTestCase(RootTestCase):
    api = Api(api_scheme)

    def test_add_currency(self):
        self.api.validate_request(
            'add_currency',
            {
                'name': 'USD',
                'designation': '$',
                'cent_factor': 100,
            }
        )

    def test_add_currency_invalid(self):
        self.assertRaises(ValidationError, self.api.validate_request,
            'add_currency',
            {
                'name': 'USD',
                'designation': '$',
                'cent_factor': 0,
            }
        )

    def test_create_balance(self):
        self.api.validate_request(
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
        self.assertRaises(ValidationError, self.api.validate_request,
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
        self.api.validate_request(
            'modify_balance',
            {
                'client_id': 'U-23-52',
                'active': 1,
                'overdraft_limit': (500, 50),
                'locking_order': None,
            }
        )

    def test_lock(self):
        self.api.validate_request(
            'lock',
            {
                'client_id': 'id',
                'product_id': 'super-light 555',
                'amount': (60, 00),
            }
        )

    def test_lock_invalid(self):
        self.assertRaises(ValidationError, self.api.validate_request,
            'lock',
            {
                'client_id': 'id',
                'product_id': 'super-light 555',
                'amount': (-60, 00),
            }
        )

    def test_lock_list(self):
        self.api.validate_request(
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
        self.assertRaises(ValidationError, self.api.validate_request,
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
        self.api.validate_request(
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
        self.assertRaises(ValidationError, self.api.validate_request,
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
        self.api.validate_request(
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
        self.assertRaises(ValidationError, self.api.validate_request,
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
