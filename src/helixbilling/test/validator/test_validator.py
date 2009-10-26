import unittest

from helixcore.server.api import Api
from helixcore.server.exceptions import ValidationError

from helixbilling.test.root_test import RootTestCase
from helixbilling.validator.validator import api_scheme


class ValidatorTestCase(RootTestCase):
    api = Api(api_scheme)

    def test_ping(self):
        self.api.validate_request('ping', {})
        self.validate_status_response('ping')

    def validate_status_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'ok'})
        self.api.validate_response(action_name, {'status': 'error', 'category': 'test', 'message': 'happens'})
        self.assertRaises(ValidationError, self.api.validate_response, action_name, {'status': 'error', 'category': 'test'})

    def test_add_currency(self):
        self.api.validate_request('add_currency', {'name': 'USD', 'designation': '$', 'cent_factor': 100})
        self.validate_status_response('add_currency')

    def test_add_currency_invalid(self):
        self.assertRaises(ValidationError, self.api.validate_request,
            'add_currency', {'name': 'USD', 'designation': '$', 'cent_factor': 0})

    def test_modify_currency(self):
        self.api.validate_request('modify_currency', {'name': 'USD', 'designation': '$', 'cent_factor': 100})
        self.api.validate_request('modify_currency', {'name': 'USD', 'designation': '$'})
        self.api.validate_request('modify_currency', {'name': 'USD'})
        self.validate_status_response('modify_currency')

    def test_delete_currency(self):
        self.api.validate_request('delete_currency', {'name': 'USD'})
        self.validate_status_response('delete_currency')

    def test_get_currencies(self):
        self.api.validate_request('get_currencies', {})
        self.api.validate_response('get_currencies', {'status': 'ok', 'currencies': []})
        self.api.validate_response('get_currencies', {'status': 'ok',
            'currencies': [{'name': 'USD', 'designation': '$', 'cent_factor': 100}]})
        self.api.validate_response('get_currencies', {'status': 'error', 'category': 'test', 'message': 'happens'})

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
        self.validate_status_response('create_balance')

    def test_create_balance_invalid(self):
        self.assertRaises(ValidationError, self.api.validate_request,
            'create_balance', {'client_id': '2', 'active': 1, 'currency_name': 'USD', 'overdraft_limit': (500, 50),
            'locking_order': ['ERROR_HERE']})

    def test_modify_balance(self):
        self.api.validate_request('modify_balance', {'client_id': 'U2', 'active': 1,
            'overdraft_limit': (500, 50), 'locking_order': None})
        self.validate_status_response('modify_balance')

    def test_delete_balance(self):
        self.api.validate_request('delete_balance', {'client_id': 'U2'})
        self.validate_status_response('delete_balance')

    def test_lock(self):
        self.api.validate_request('lock', {'client_id': 'id', 'product_id': 'super', 'amount': (60, 00)})
        self.validate_status_response('lock')

    def test_lock_invalid(self):
        self.assertRaises(ValidationError, self.api.validate_request,
            'lock', {'client_id': 'id', 'product_id': 'super-light 555', 'amount': (-60, 00)})

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
        self.validate_status_response('lock_list')

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

    def test_unlock(self):
        self.api.validate_request('unlock', {'client_id': 'id_one', 'product_id': 'super-light 555'})
        self.validate_status_response('unlock')

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
        self.validate_status_response('unlock_list')

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

    def test_chargeoff(self):
        self.api.validate_request('chargeoff', {'client_id': 'id_two', 'product_id': 'brb'})
        self.validate_status_response('chargeoff')

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
        self.validate_status_response('chargeoff_list')

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
