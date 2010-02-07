import unittest
import datetime
import pytz

from helixcore.server.api import Api
from helixcore.server.exceptions import ValidationError

from helixbilling.test.root_test import RootTestCase
from helixbilling.validator.validator import protocol


class ValidatorTestCase(RootTestCase):
    api = Api(protocol)

    def validate_error_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'error', 'category': 't',
            'message': 'h', 'details': [{'f': 'v'}]})
        self.api.validate_response(action_name, {'status': 'error', 'category': 't',
            'message': 'h', 'details': [{}]})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'category': 'test'})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'category': 'test', 'message': 'm'})

    def validate_status_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'ok'})
        self.validate_error_response(action_name)

    def test_ping(self):
        self.api.validate_request('ping', {})
        self.validate_status_response('ping')

    def test_view_currencies(self):
        a_name = 'view_currencies'
        self.api.validate_request(a_name, {})
        self.api.validate_response(a_name, {'status': 'ok', 'currencies': []})
        self.api.validate_response(a_name, {'status': 'ok', 'currencies': [
            {'code': 'YYY', 'name': 'y', 'location': 'y', 'cent_factor': 100}
        ]})
        self.validate_error_response(a_name)

    def test_add_operator(self):
        a_name = 'add_operator'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'custom_operator_info': 'i'})
        self.validate_status_response(a_name)

    def test_modify_operator(self):
        a_name = 'modify_operator'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'new_login': 'nl'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'new_login': 'nl',
            'new_password': 'np', 'custom_operator_info': 'i'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p'})
        self.validate_status_response(a_name)

    def test_add_balance(self):
        a_name = 'add_balance'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'customer_id': 'U-23-52', 'active': True, 'currency': 'YYY'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'customer_id': 'U', 'active': True,
            'currency': 'YYY', 'overdraft_limit': '500.50'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'customer_id': 'U', 'active': True,
            'currency': 'YYY', 'overdraft_limit': '500.50', 'locking_order': ['available_real_amount', 'available_virtual_amount']})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'customer_id': 'U', 'active': True,
            'currency': 'YYY', 'overdraft_limit': '500.50', 'locking_order': ['available_real_amount']})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'customer_id': 'U', 'active': True,
            'currency': 'YYY', 'overdraft_limit': '500.50', 'locking_order': None})

    def test_modify_balance(self):
        a_name = 'modify_balance'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'customer_id': 'U2', 'new_active': True, 'new_overdraft_limit': '500.50',
            'new_locking_order': None})
        self.validate_status_response(a_name)

    def test_delete_balance(self):
        a_name = 'delete_balance'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'customer_id': 'U2'})
        self.validate_status_response(a_name)

    def test_get_balance(self):
        a_name = 'get_balance'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'customer_id': 'U2'})
        self.api.validate_response(a_name, {'status': 'ok', 'customer_id': 'c', 'active': True,
            'currency_code': 'RU', 'available_real_amount': '3.15', 'available_virtual_amount': '0.0',
            'locked_amount': '14.09', 'overdraft_limit': '0.14',
            'locking_order': ['available_real_amount', 'available_virtual_amount'],
            'creation_date': '%s' % datetime.datetime.now(pytz.utc),
        })
        self.validate_error_response(a_name)

    def test_view_balances(self):
        a_name = 'view_balances'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'filter_params': {},
            'paging_params': {},})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'filter_params': {},
            'paging_params': {'limit': 0,}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'filter_params': {},
            'paging_params': {'limit': 0, 'offset': 0,}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'filter_params': {
            'customer_ids': []}, 'paging_params': {'limit': 0, 'offset': 0,}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'filter_params': {
            'customer_ids': ['a', 'b']}, 'paging_params': {}})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 2, 'balances': [
            {
                'customer_id': 'c', 'active': True,
                'currency_code': 'RU', 'available_real_amount': '3.15', 'available_virtual_amount': '0.0',
                'locked_amount': '14.09', 'overdraft_limit': '0.14',
                'locking_order': ['available_real_amount', 'available_virtual_amount'],
                'creation_date': '%s' % datetime.datetime.now(pytz.utc),
            },
        ]})
        self.validate_error_response(a_name)

    def enroll_income(self, a_name):
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'customer_id': 'N5',
            'amount': '0.0'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'customer_id': 'N5',
            'amount': '10.01'})
        self.validate_status_response(a_name)

    def view_income(self, a_name, res_name):
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {}, 'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a', 'b']}, 'paging_params': {}})
        d = datetime.datetime.now(pytz.utc)
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a', 'b'], 'from_creation_date': d.isoformat()},
            'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a', 'b'], 'from_creation_date': d.isoformat(),
            'to_creation_date': d.isoformat()},
            'paging_params': {}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 10,
            res_name: []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 10,
            res_name: [
                {'customer_id': 'U2', 'amount': '1.1', 'currency': 'YYY', 'creation_date': d.isoformat()},
                {'customer_id': 'U2', 'amount': '1.1', 'currency': 'ZZZ', 'creation_date': d.isoformat()},
            ]
        })
        self.validate_error_response(a_name)

    def test_enroll_receipt(self):
        self.enroll_income('enroll_receipt')

    def test_view_receipts(self):
        self.view_income('view_receipts', 'receipts')

    def test_enroll_bonus(self):
        self.enroll_income('enroll_bonus')

    def test_view_bonuses(self):
        self.view_income('view_bonuses', 'bonuses')

    def test_lock(self):
        a_name = 'lock'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'customer_id': 'id', 'product_id': 'super', 'amount': '60.00'})
        self.validate_status_response(a_name)

#    def test_lock_invalid(self):
#        self.assertRaises(ValidationError, self.api.validate_request, 'lock', {'login': 'l', 'password': 'p',
#            'client_id': 'id', 'product_id': 'super-light 555', 'amount': (-60, 00)})
#
#    def test_lock_list(self):
#        self.api.validate_request(
#            'lock_list',
#            {
#                'login': 'l',
#                'password': 'p',
#                'locks': [
#                    {
#                        'client_id': 'id_one',
#                        'product_id': 'super-light 555',
#                        'amount': (60, 00),
#                    },
#                    {
#                        'client_id': 'id_two',
#                        'product_id': 'brb',
#                        'amount': (60, 00),
#                    }
#                ]
#            }
#        )
#        self.validate_status_response('lock_list')
#
#    def test_lock_list_invalid(self):
#        self.assertRaises(ValidationError, self.api.validate_request,
#            'lock_list',
#            {
#                'login': 'l',
#                'password': 'p',
#                'locks': [
#                    {
#                        'client_id': 'id_one',
#                        'product_id': 'super-light 555',
#                        'amount': (60, 00),
#                    },
#                    {
#                        'client_id': 'id_two',
#                        'ERROR_HERE': 'brb',
#                        'amount': (60, 00),
#                    }
#                ]
#            }
#        )
#
#    def test_unlock(self):
#        self.api.validate_request('unlock', {'login': 'l', 'password': 'p',
#            'client_id': 'id_one', 'product_id': 'super-light 555'})
#        self.validate_status_response('unlock')
#
#    def test_unlock_list(self):
#        self.api.validate_request(
#            'unlock_list',
#            {
#                'login': 'l',
#                'password': 'p',
#                'unlocks': [
#                    {
#                        'client_id': 'id_one',
#                        'product_id': 'super-light 555',
#                    },
#                    {
#                        'client_id': 'id_two',
#                        'product_id': 'brb',
#                    }
#                ]
#            }
#        )
#        self.validate_status_response('unlock_list')
#
#    def test_unlock_list_invalid(self):
#        self.assertRaises(ValidationError, self.api.validate_request,
#            'unlock_list',
#            {
#                'login': 'l',
#                'password': 'p',
#                'unlocks': [
#                    {
#                        'client_id': 'id_one',
#                        'product_id': 'super-light 555',
#                    },
#                    {
#                        'client_id': 'id_two',
#                        'product_id': 'brb',
#                        'ERROR_HERE': 'bug',
#                    }
#                ]
#            }
#        )
#
#    def test_chargeoff(self):
#        self.api.validate_request('chargeoff', {'login': 'l', 'password': 'p',
#            'client_id': 'id_two', 'product_id': 'brb'})
#        self.validate_status_response('chargeoff')
#
#    def test_chargeoff_list(self):
#        self.api.validate_request(
#            'chargeoff_list',
#            {
#                'password': 'p',
#                'login': 'l',
#                'chargeoffs': [
#                    {
#                        'client_id': 'id_one',
#                        'product_id': 'super-light 555',
#                    },
#                    {
#                        'client_id': 'id_two',
#                        'product_id': 'brb',
#                    }
#                ]
#            }
#        )
#        self.validate_status_response('chargeoff_list')
#
#    def test_chargeoff_list_invalid(self):
#        self.assertRaises(ValidationError, self.api.validate_request,
#            'chargeoff_list',
#            {
#                'password': 'p',
#                'login': 'l',
#                'chargeoff': [
#                    {
#                        'client_id': 'id_one',
#                        'product_id': 'super-light 555',
#                    },
#                    {
#                        'client_id': 'id_two',
#                        'product_id': 'brb',
#                        'amount': 'BUG',
#                    }
#                ]
#            }
#        )
#
#    def test_product_status(self):
#        self.api.validate_request('product_status', {'login': 'l', 'password': 'p',
#            'client_id': 'id_two', 'product_id': 'brb'})
#        self.api.validate_response('product_status', {'status': 'ok', 'product_status': 'unknown'})
#        self.api.validate_response('product_status', {'status': 'ok', 'product_status': 'locked',
#            'real_amount': (0, 0), 'virtual_amount': (1, 9),
#            'locked_date': datetime.datetime(year=2009, month=10, day=29, tzinfo=pytz.utc).isoformat(),
#        })
#        self.api.validate_response('product_status', {'status': 'ok', 'product_status': 'charged_off',
#            'real_amount': (0, 0), 'virtual_amount': (1, 9),
#            'locked_date': datetime.datetime(year=2009, month=10, day=29, tzinfo=pytz.utc).isoformat(),
#            'chargeoff_date': datetime.datetime.now().isoformat(),
#        })
#
#    def test_view_bonuses(self):
#        self.api.validate_request('view_bonuses', {'login': 'l', 'password': 'p',
#            'client_id': 'U', 'offset': 2, 'limit': 3})
#        self.api.validate_request('view_bonuses', {'login': 'l', 'password': 'p', 'client_id': 'U',
#            'start_date': datetime.datetime.now().isoformat(), 'offset': 2, 'limit': 3})
#        self.api.validate_request('view_bonuses', {'login': 'l', 'password': 'p', 'client_id': 'U',
#            'start_date': datetime.datetime.now().isoformat(),
#            'end_date': (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat(), 'offset': 2, 'limit': 3})
#        self.api.validate_response('view_bonuses', {'status': 'ok', 'total': 0, 'bonuses': []})
#        self.api.validate_response('view_bonuses', {'status': 'ok', 'total': 10,
#            'bonuses': [
#                {
#                    'client_id': 'U2',
#                    'amount': (2, 49),
#                    'created_date': datetime.datetime.now().isoformat(),
#                }
#            ]
#        })
#        self.api.validate_response('view_bonuses', {'status': 'ok', 'total': 10,
#            'bonuses': [
#                {
#                    'client_id': 'U2',
#                    'amount': (2, 49),
#                    'created_date': datetime.datetime.now().isoformat(),
#                },
#                {
#                    'client_id': 'U3',
#                    'amount': (3, 77),
#                    'created_date': datetime.datetime.now().isoformat(),
#                }
#            ]
#        })
#
#    def test_view_chargeoffs(self):
#        self.api.validate_request('view_chargeoffs', {'login': 'l', 'password': 'p',
#            'client_id': 'U', 'offset': 2, 'limit': 3})
#        self.api.validate_request('view_chargeoffs', {'login': 'l', 'password': 'p',
#            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j'})
#        self.api.validate_request('view_chargeoffs', {'login': 'l', 'password': 'p',
#            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j',
#            'locked_start_date': datetime.datetime.now().isoformat()})
#        self.api.validate_request('view_chargeoffs', {'login': 'l', 'password': 'p',
#            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j',
#            'locked_start_date': datetime.datetime.now().isoformat(),
#            'locked_end_date': (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat(),
#        })
#        self.api.validate_request('view_chargeoffs', {'login': 'l', 'password': 'p',
#            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j',
#            'locked_start_date': datetime.datetime.now().isoformat(),
#            'locked_end_date': (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat(),
#            'chargeoff_start_date': datetime.datetime.now().isoformat(),
#        })
#        self.api.validate_request('view_chargeoffs', {'login': 'l', 'password': 'p',
#            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j',
#            'locked_start_date': datetime.datetime.now().isoformat(),
#            'locked_end_date': (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat(),
#            'chargeoff_start_date': datetime.datetime.now().isoformat(),
#            'chargeoff_end_date': (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat(),
#        })
#        self.api.validate_response('view_chargeoffs', {'status': 'ok', 'total': 0, 'chargeoffs': []})
#        self.api.validate_response('view_chargeoffs', {'status': 'ok', 'total': 10,
#            'chargeoffs': [
#                {
#                    'client_id': 'U2',
#                    'product_id': 'k9',
#                    'real_amount': (2, 49),
#                    'virtual_amount': (0, 0),
#                    'locked_date': datetime.datetime.now().isoformat(),
#                    'chargeoff_date': datetime.datetime.now().isoformat(),
#                }
#            ]
#        })
#        self.api.validate_response('view_chargeoffs', {'status': 'ok', 'total': 10,
#            'chargeoffs': [
#                {
#                    'client_id': 'U2',
#                    'product_id': 'k9',
#                    'real_amount': (2, 49),
#                    'virtual_amount': (0, 0),
#                    'locked_date': datetime.datetime.now().isoformat(),
#                    'chargeoff_date': datetime.datetime.now().isoformat(),
#                },
#                {
#                    'client_id': 'U2',
#                    'product_id': 'k9',
#                    'real_amount': (0, 0),
#                    'virtual_amount': (0, 0),
#                    'locked_date': datetime.datetime.now().isoformat(),
#                    'chargeoff_date': datetime.datetime.now().isoformat(),
#                },
#                {
#                    'client_id': 'U2',
#                    'product_id': 'k5',
#                    'real_amount': (0, 0),
#                    'virtual_amount': (60, 0),
#                    'locked_date': datetime.datetime.now().isoformat(),
#                    'chargeoff_date': datetime.datetime.now().isoformat(),
#                },
#            ]
#        })
#
#    def test_view_balance_locks(self):
#        self.api.validate_request('view_balance_locks', {'login': 'l', 'password': 'p',
#            'client_id': 'U', 'offset': 2, 'limit': 3})
#        self.api.validate_request('view_balance_locks', {'login': 'l', 'password': 'p',
#            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j'})
#        self.api.validate_request('view_balance_locks', {'login': 'l', 'password': 'p',
#            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j',
#            'locked_start_date': datetime.datetime.now().isoformat()})
#        self.api.validate_request('view_balance_locks', {'login': 'l', 'password': 'p',
#            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j',
#            'locked_start_date': datetime.datetime.now().isoformat(),
#            'locked_end_date': (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat(),
#        })
#        self.api.validate_response('view_balance_locks', {'status': 'ok', 'total': 0, 'balance_locks': []})
#        self.api.validate_response('view_balance_locks', {'status': 'ok', 'total': 10,
#            'balance_locks': [
#                {
#                    'client_id': 'U2',
#                    'product_id': 'k9',
#                    'real_amount': (2, 49),
#                    'virtual_amount': (0, 0),
#                    'locked_date': datetime.datetime.now().isoformat(),
#                }
#            ]
#        })
#        self.api.validate_response('view_balance_locks', {'status': 'ok', 'total': 10,
#            'balance_locks': [
#                {
#                    'client_id': 'U2',
#                    'product_id': 'k9',
#                    'real_amount': (2, 49),
#                    'virtual_amount': (0, 0),
#                    'locked_date': datetime.datetime.now().isoformat(),
#                },
#                {
#                    'client_id': 'U2',
#                    'product_id': 'k9',
#                    'real_amount': (0, 0),
#                    'virtual_amount': (0, 0),
#                    'locked_date': datetime.datetime.now().isoformat(),
#                },
#                {
#                    'client_id': 'U2',
#                    'product_id': 'k5',
#                    'real_amount': (0, 0),
#                    'virtual_amount': (60, 0),
#                    'locked_date': datetime.datetime.now().isoformat(),
#                },
#            ]
#        })


if __name__ == '__main__':
    unittest.main()
