import unittest
import datetime
import pytz

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

    def test_add_billing_manager(self):
        self.api.validate_request('add_billing_manager', {'login': 'admin', 'password': 'crypted twice'})
        self.validate_status_response('add_billing_manager')

    def test_add_billing_manager_invalid(self):
        self.assertRaises(ValidationError, self.api.validate_request, 'add_billing_manager', {'login': 'admin'})
        self.assertRaises(ValidationError, self.api.validate_request, 'add_billing_manager', {'password': 'admin'})
        self.assertRaises(ValidationError, self.api.validate_request, 'add_billing_manager', {})

    def test_modify_billing_manager(self):
        self.api.validate_request('modify_billing_manager', {'login': 'log', 'password': 'pi', 'new_login': 'new_log'})
        self.api.validate_request('modify_billing_manager', {'login': 'log', 'password': 'pi', 'new_login': 'new_log', 'new_password': 'pw'})
        self.api.validate_request('modify_billing_manager', {'login': 'log', 'password': 'pi'})
        self.validate_status_response('modify_billing_manager')

    def test_delete_billing_manager(self):
        self.api.validate_request('delete_billing_manager', {'login': 'log', 'password': 'pi'})
        self.validate_status_response('delete_billing_manager')

    def test_view_currencies(self):
        self.api.validate_request('view_currencies', {})
        self.api.validate_response('view_currencies', {'status': 'ok', 'currencies': []})
        self.api.validate_response('view_currencies', {'status': 'ok',
            'currencies': [{'code': 'YYY', 'name': 'y', 'location': 'y', 'cent_factor': 100}]})
        self.api.validate_response('view_currencies', {'status': 'error', 'category': 'test', 'message': 'happens'})

    def test_create_balance(self):
        data = {'login': 'l', 'password': 'p', 'client_id': 'U-23-52', 'active': True,
            'currency_code': 'YYY'}
        self.api.validate_request('create_balance', data)

        data['overdraft_limit'] = (500, 50)
        self.api.validate_request('create_balance', data)

        data['locking_order'] = ['available_real_amount', 'available_virtual_amount']
        self.api.validate_request('create_balance', data)

        self.validate_status_response('create_balance')

    def test_create_balance_invalid(self):
        self.assertRaises(ValidationError, self.api.validate_request,
            'create_balance',
            {
                'login': 'l',
                'password': 'p',
                'client_id': '2',
                'active': 1,
                'currency_code': 'USD',
                'overdraft_limit': (500, 50),
                'locking_order': ['ERROR_HERE']
            }
        )

    def test_modify_balance(self):
        self.api.validate_request('modify_balance', {'login': 'l', 'password': 'p', 'client_id': 'U2',
            'new_active': True, 'new_overdraft_limit': (500, 50), 'new_locking_order': None})
        self.validate_status_response('modify_balance')

    def test_delete_balance(self):
        self.api.validate_request('delete_balance', {'login': 'l', 'password': 'p', 'client_id': 'U2'})
        self.validate_status_response('delete_balance')

    def test_enroll_receipt(self):
        self.api.validate_request('enroll_receipt', {'login': 'l', 'password': 'p',
            'client_id': 'N5', 'amount': (30, 00)})
        self.assertRaises(ValidationError, self.api.validate_request, 'enroll_receipt',
            {'login': 'l', 'password': 'p', 'client_id': 'N5', 'amount': (00, 00)})
        self.validate_status_response('enroll_receipt')

    def test_enroll_bonus(self):
        self.api.validate_request('enroll_bonus', {'login': 'l', 'password': 'p',
            'client_id': 'N5', 'amount': (30, 00)})
        self.assertRaises(ValidationError, self.api.validate_request, 'enroll_bonus',
            {'login': 'l', 'password': 'p', 'client_id': 'N5', 'amount': (00, 00)})
        self.validate_status_response('enroll_bonus')

    def test_lock(self):
        self.api.validate_request('lock', {'login': 'l', 'password': 'p',
            'client_id': 'id', 'product_id': 'super', 'amount': (60, 00)})
        self.validate_status_response('lock')

    def test_lock_invalid(self):
        self.assertRaises(ValidationError, self.api.validate_request, 'lock', {'login': 'l', 'password': 'p',
            'client_id': 'id', 'product_id': 'super-light 555', 'amount': (-60, 00)})

    def test_lock_list(self):
        self.api.validate_request(
            'lock_list',
            {
                'login': 'l',
                'password': 'p',
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
                'login': 'l',
                'password': 'p',
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
        self.api.validate_request('unlock', {'login': 'l', 'password': 'p',
            'client_id': 'id_one', 'product_id': 'super-light 555'})
        self.validate_status_response('unlock')

    def test_unlock_list(self):
        self.api.validate_request(
            'unlock_list',
            {
                'login': 'l',
                'password': 'p',
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
                'login': 'l',
                'password': 'p',
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
        self.api.validate_request('chargeoff', {'login': 'l', 'password': 'p',
            'client_id': 'id_two', 'product_id': 'brb'})
        self.validate_status_response('chargeoff')

    def test_chargeoff_list(self):
        self.api.validate_request(
            'chargeoff_list',
            {
                'password': 'p',
                'login': 'l',
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
                'password': 'p',
                'login': 'l',
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

    def test_product_status(self):
        self.api.validate_request('product_status', {'login': 'l', 'password': 'p',
            'client_id': 'id_two', 'product_id': 'brb'})
        self.api.validate_response('product_status', {'status': 'ok', 'product_status': 'unknown'})
        self.api.validate_response('product_status', {'status': 'ok', 'product_status': 'locked',
            'real_amount': (0, 0), 'virtual_amount': (1, 9),
            'locked_date': datetime.datetime(year=2009, month=10, day=29, tzinfo=pytz.utc).isoformat(),
        })
        self.api.validate_response('product_status', {'status': 'ok', 'product_status': 'charged_off',
            'real_amount': (0, 0), 'virtual_amount': (1, 9),
            'locked_date': datetime.datetime(year=2009, month=10, day=29, tzinfo=pytz.utc).isoformat(),
            'chargeoff_date': datetime.datetime.now().isoformat(),
        })

    def test_view_receipts(self):
        self.api.validate_request('view_receipts', {'login': 'l', 'password': 'p',
            'client_id': 'U', 'offset': 2, 'limit': 3})
        self.api.validate_request('view_receipts', {'login': 'l', 'password': 'p', 'client_id': 'U',
            'start_date': datetime.datetime.now().isoformat(), 'offset': 2, 'limit': 3})
        self.api.validate_request('view_receipts', {'login': 'l', 'password': 'p', 'client_id': 'U',
            'start_date': datetime.datetime.now().isoformat(),
            'end_date': (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat(), 'offset': 2, 'limit': 3})
        self.api.validate_response('view_receipts', {'status': 'ok', 'total': 0, 'receipts': []})
        self.api.validate_response('view_receipts', {'status': 'ok', 'total': 10,
            'receipts': [
                {
                    'client_id': 'U2',
                    'amount': (2, 49),
                    'created_date': datetime.datetime.now().isoformat(),
                }
            ]
        })
        self.api.validate_response('view_receipts', {'status': 'ok', 'total': 10,
            'receipts': [
                {
                    'client_id': 'U2',
                    'amount': (2, 49),
                    'created_date': datetime.datetime.now().isoformat(),
                },
                {
                    'client_id': 'U3',
                    'amount': (3, 77),
                    'created_date': datetime.datetime.now().isoformat(),
                }
            ]
        })

    def test_view_bonuses(self):
        self.api.validate_request('view_bonuses', {'login': 'l', 'password': 'p',
            'client_id': 'U', 'offset': 2, 'limit': 3})
        self.api.validate_request('view_bonuses', {'login': 'l', 'password': 'p', 'client_id': 'U',
            'start_date': datetime.datetime.now().isoformat(), 'offset': 2, 'limit': 3})
        self.api.validate_request('view_bonuses', {'login': 'l', 'password': 'p', 'client_id': 'U',
            'start_date': datetime.datetime.now().isoformat(),
            'end_date': (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat(), 'offset': 2, 'limit': 3})
        self.api.validate_response('view_bonuses', {'status': 'ok', 'total': 0, 'bonuses': []})
        self.api.validate_response('view_bonuses', {'status': 'ok', 'total': 10,
            'bonuses': [
                {
                    'client_id': 'U2',
                    'amount': (2, 49),
                    'created_date': datetime.datetime.now().isoformat(),
                }
            ]
        })
        self.api.validate_response('view_bonuses', {'status': 'ok', 'total': 10,
            'bonuses': [
                {
                    'client_id': 'U2',
                    'amount': (2, 49),
                    'created_date': datetime.datetime.now().isoformat(),
                },
                {
                    'client_id': 'U3',
                    'amount': (3, 77),
                    'created_date': datetime.datetime.now().isoformat(),
                }
            ]
        })

    def test_view_chargeoffs(self):
        self.api.validate_request('view_chargeoffs', {'login': 'l', 'password': 'p',
            'client_id': 'U', 'offset': 2, 'limit': 3})
        self.api.validate_request('view_chargeoffs', {'login': 'l', 'password': 'p',
            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j'})
        self.api.validate_request('view_chargeoffs', {'login': 'l', 'password': 'p',
            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j',
            'locked_start_date': datetime.datetime.now().isoformat()})
        self.api.validate_request('view_chargeoffs', {'login': 'l', 'password': 'p',
            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j',
            'locked_start_date': datetime.datetime.now().isoformat(),
            'locked_end_date': (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat(),
        })
        self.api.validate_request('view_chargeoffs', {'login': 'l', 'password': 'p',
            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j',
            'locked_start_date': datetime.datetime.now().isoformat(),
            'locked_end_date': (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat(),
            'chargeoff_start_date': datetime.datetime.now().isoformat(),
        })
        self.api.validate_request('view_chargeoffs', {'login': 'l', 'password': 'p',
            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j',
            'locked_start_date': datetime.datetime.now().isoformat(),
            'locked_end_date': (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat(),
            'chargeoff_start_date': datetime.datetime.now().isoformat(),
            'chargeoff_end_date': (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat(),
        })
        self.api.validate_response('view_chargeoffs', {'status': 'ok', 'total': 0, 'chargeoffs': []})
        self.api.validate_response('view_chargeoffs', {'status': 'ok', 'total': 10,
            'chargeoffs': [
                {
                    'client_id': 'U2',
                    'product_id': 'k9',
                    'real_amount': (2, 49),
                    'virtual_amount': (0, 0),
                    'locked_date': datetime.datetime.now().isoformat(),
                    'chargeoff_date': datetime.datetime.now().isoformat(),
                }
            ]
        })
        self.api.validate_response('view_chargeoffs', {'status': 'ok', 'total': 10,
            'chargeoffs': [
                {
                    'client_id': 'U2',
                    'product_id': 'k9',
                    'real_amount': (2, 49),
                    'virtual_amount': (0, 0),
                    'locked_date': datetime.datetime.now().isoformat(),
                    'chargeoff_date': datetime.datetime.now().isoformat(),
                },
                {
                    'client_id': 'U2',
                    'product_id': 'k9',
                    'real_amount': (0, 0),
                    'virtual_amount': (0, 0),
                    'locked_date': datetime.datetime.now().isoformat(),
                    'chargeoff_date': datetime.datetime.now().isoformat(),
                },
                {
                    'client_id': 'U2',
                    'product_id': 'k5',
                    'real_amount': (0, 0),
                    'virtual_amount': (60, 0),
                    'locked_date': datetime.datetime.now().isoformat(),
                    'chargeoff_date': datetime.datetime.now().isoformat(),
                },
            ]
        })

    def test_view_balance_locks(self):
        self.api.validate_request('view_balance_locks', {'login': 'l', 'password': 'p',
            'client_id': 'U', 'offset': 2, 'limit': 3})
        self.api.validate_request('view_balance_locks', {'login': 'l', 'password': 'p',
            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j'})
        self.api.validate_request('view_balance_locks', {'login': 'l', 'password': 'p',
            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j',
            'locked_start_date': datetime.datetime.now().isoformat()})
        self.api.validate_request('view_balance_locks', {'login': 'l', 'password': 'p',
            'client_id': 'U', 'offset': 2, 'limit': 3, 'product_id': 'j',
            'locked_start_date': datetime.datetime.now().isoformat(),
            'locked_end_date': (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat(),
        })
        self.api.validate_response('view_balance_locks', {'status': 'ok', 'total': 0, 'balance_locks': []})
        self.api.validate_response('view_balance_locks', {'status': 'ok', 'total': 10,
            'balance_locks': [
                {
                    'client_id': 'U2',
                    'product_id': 'k9',
                    'real_amount': (2, 49),
                    'virtual_amount': (0, 0),
                    'locked_date': datetime.datetime.now().isoformat(),
                }
            ]
        })
        self.api.validate_response('view_balance_locks', {'status': 'ok', 'total': 10,
            'balance_locks': [
                {
                    'client_id': 'U2',
                    'product_id': 'k9',
                    'real_amount': (2, 49),
                    'virtual_amount': (0, 0),
                    'locked_date': datetime.datetime.now().isoformat(),
                },
                {
                    'client_id': 'U2',
                    'product_id': 'k9',
                    'real_amount': (0, 0),
                    'virtual_amount': (0, 0),
                    'locked_date': datetime.datetime.now().isoformat(),
                },
                {
                    'client_id': 'U2',
                    'product_id': 'k5',
                    'real_amount': (0, 0),
                    'virtual_amount': (60, 0),
                    'locked_date': datetime.datetime.now().isoformat(),
                },
            ]
        })


if __name__ == '__main__':
    unittest.main()
