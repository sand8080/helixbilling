import unittest
import datetime
import pytz

from helixcore.server.api import Api
from helixcore.server.exceptions import ValidationError

from helixbilling.test.root_test import RootTestCase
from helixbilling.validator.validator import (protocol, ORDER_STATUS_UNKNOWN, ORDER_STATUS_LOCKED,
    ORDER_STATUS_CHARGED_OFF)


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

    def test_balance_lock(self):
        a_name = 'balance_lock'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'customer_id': 'id', 'order_id': '1', 'amount': '60.00'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'customer_id': 'id', 'order_id': '1', 'order_type': 'super', 'amount': '60.00'})
        self.validate_status_response(a_name)

    def test_balance_lock_list(self):
        a_name = 'balance_lock_list'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'locks': []})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'locks': [
            {'customer_id': 'c0', 'order_id': '110', 'amount': '60.00'},
            {'customer_id': 'c1', 'order_id': '10', 'order_type': 'space', 'amount': '50.00'},
        ]})
        self.validate_status_response(a_name)

    def test_view_balance_locks(self):
        a_name = 'view_balance_locks'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {}, 'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a', 'b']}, 'paging_params': {}})
        d = datetime.datetime.now(pytz.utc)
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'filter_params':
            {'customer_ids': [], 'from_locking_date': d.isoformat()},
            'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': [], 'from_locking_date': d.isoformat(),
            'to_locking_date': d.isoformat()}, 'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'from_locking_date': d.isoformat(),
            'to_locking_date': d.isoformat()}, 'paging_params': {'limit': 5}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'from_locking_date': d.isoformat(),
            'to_locking_date': d.isoformat()}, 'paging_params': {'limit': 5, 'offset': 10}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'from_locking_date': d.isoformat(),
            'to_locking_date': d.isoformat(), 'order_id': '77H'}, 'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'from_locking_date': d.isoformat(),
            'to_locking_date': d.isoformat(), 'order_type': 'moon'}, 'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'from_locking_date': d.isoformat(),
            'to_locking_date': d.isoformat(), 'order_type': None}, 'paging_params': {}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 0, 'balance_locks': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 10,
            'balance_locks': [
                {'customer_id': 'U2', 'order_id': 'k9', 'order_type': 'mia', 'real_amount': '2.49',
                    'virtual_amount': '0.0', 'locking_date': d.isoformat(), 'currency': 'YYY'},
                {'customer_id': 'U3', 'order_id': 'k9', 'order_type': None, 'real_amount': '2.49',
                    'virtual_amount': '0.0', 'locking_date': d.isoformat(), 'currency': 'YES'},
            ]
        })
        self.validate_error_response(a_name)

    def test_balance_unlock(self):
        a_name = 'balance_unlock'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'customer_id': 'id', 'order_id': '1'})
        self.validate_status_response(a_name)

    def test_balance_unlock_list(self):
        a_name = 'balance_unlock_list'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'unlocks': []})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'unlocks': [
            {'customer_id': 'c0', 'order_id': '110'},
            {'customer_id': 'c1', 'order_id': '10'},
        ]})
        self.validate_status_response(a_name)

    def test_chargeoff(self):
        a_name = 'chargeoff'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'customer_id': 'id', 'order_id': '1'})
        self.validate_status_response(a_name)

    def test_chargeoff_list(self):
        a_name = 'chargeoff_list'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'chargeoffs': []})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'chargeoffs': [
            {'customer_id': 'c0', 'order_id': '110'},
            {'customer_id': 'c1', 'order_id': '10'},
        ]})
        self.validate_status_response(a_name)

    def test_view_chargeoffs(self):
        a_name = 'view_chargeoffs'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {}, 'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a', 'b']}, 'paging_params': {}})
        d = datetime.datetime.now(pytz.utc)
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'filter_params':
            {'customer_ids': [], 'from_chargeoff_date': d.isoformat()},
            'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': [], 'from_chargeoff_date': d.isoformat(),
            'to_chargeoff_date': d.isoformat()}, 'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'from_chargeoff_date': d.isoformat(),
            'to_chargeoff_date': d.isoformat()}, 'paging_params': {'limit': 5}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'from_chargeoff_date': d.isoformat(),
            'to_chargeoff_date': d.isoformat()}, 'paging_params': {'limit': 5, 'offset': 10}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'from_chargeoff_date': d.isoformat(),
            'to_chargeoff_date': d.isoformat(), 'order_id': '77H'}, 'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'from_chargeoff_date': d.isoformat(),
            'to_chargeoff_date': d.isoformat(), 'order_type': 'moon'}, 'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'from_chargeoff_date': d.isoformat(),
            'to_chargeoff_date': d.isoformat(), 'order_type': None}, 'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'from_locking_date': d.isoformat(),
            'to_locking_date': d.isoformat(), 'order_type': None}, 'paging_params': {}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 0, 'chargeoffs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 10,
            'chargeoffs': [
                {'customer_id': 'U2', 'order_id': 'k9', 'order_type': 'mia', 'real_amount': '2.49',
                    'virtual_amount': '0.0','chargeoff_date': d.isoformat(),
                    'locking_date': d.isoformat(), 'currency': 'YYY'},
                {'customer_id': 'U3', 'order_id': 'k9', 'order_type': None, 'real_amount': '2.49',
                    'virtual_amount': '0.0', 'chargeoff_date': d.isoformat(),
                    'locking_date': d.isoformat(), 'currency': 'YES'},
            ]
        })
        self.validate_error_response(a_name)

    def test_order_status(self):
        a_name = 'order_status'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'customer_id': 'c',
            'order_id': 'r'})

        self.api.validate_response(a_name, {'status': 'ok', 'customer_id': 'c', 'order_id': '1',
            'order_status': ORDER_STATUS_UNKNOWN, 'real_amount': None, 'virtual_amount': None,
            'locking_date': None, 'chargeoff_date': None})
        self.validate_error_response(a_name)
        d = datetime.datetime.now(pytz.utc)
        self.api.validate_response(a_name, {'status': 'ok', 'customer_id': 'c', 'order_id': '1',
            'order_status': ORDER_STATUS_LOCKED, 'real_amount': '1.09', 'virtual_amount': '0',
            'locking_date': d.isoformat(), 'chargeoff_date': None})
        self.api.validate_response(a_name, {'status': 'ok', 'customer_id': 'c', 'order_id': '1',
            'order_status': ORDER_STATUS_CHARGED_OFF, 'real_amount': '1.09', 'virtual_amount': '0',
            'locking_date': d.isoformat(), 'chargeoff_date': d.isoformat()})
        self.validate_error_response(a_name)

    def test_view_order_statuses(self):
        a_name = 'view_order_statuses'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'filter_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a']}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'order_types': ['t']}})
        d = datetime.datetime.now(pytz.utc)
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'order_types': ['t'],
            'from_locking_date': d.isoformat()}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'order_types': ['t'],
            'from_locking_date': d.isoformat(), 'to_locking_date': d.isoformat()}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'order_types': ['t'],
            'from_locking_date': d.isoformat(), 'to_locking_date': d.isoformat(),
            'from_chargeoff_date': d.isoformat()}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'customer_ids': ['a'], 'order_types': ['t'],
            'from_locking_date': d.isoformat(), 'to_locking_date': d.isoformat(),
            'from_chargeoff_date': d.isoformat(), 'to_chargeoff_date': d.isoformat()}})

        self.api.validate_response(a_name, {'status': 'ok', 'order_statuses': [
            {'customer_id': 'c', 'order_id': '1', 'order_status': ORDER_STATUS_UNKNOWN,
                'real_amount': None, 'virtual_amount': None, 'locking_date': None,
                'chargeoff_date': None},
            ]})
        self.api.validate_response(a_name, {'status': 'ok', 'order_statuses': [
            {'customer_id': 'c', 'order_id': '1', 'order_status': ORDER_STATUS_LOCKED,
                'real_amount': '1.0', 'virtual_amount': '0', 'locking_date': d.isoformat(),
                'chargeoff_date': None},
            {'customer_id': 'c', 'order_id': '1', 'order_status': ORDER_STATUS_CHARGED_OFF,
                'real_amount': '1.0', 'virtual_amount': '0', 'locking_date': d.isoformat(),
                'chargeoff_date': d.isoformat()},
            ]})
        self.validate_error_response(a_name)

    def test_view_action_logs(self):
        a_name = 'view_action_logs'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {}, 'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'action': 'a'}, 'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'action': 'a'}, 'paging_params': {'limit': 4}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'action': 'a'}, 'paging_params': {}})
        s_d1 = datetime.datetime(year=2009, month=10, day=29, tzinfo=pytz.utc).isoformat()
        s_d2 = datetime.datetime.now(pytz.utc).isoformat()
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'action': 'a', 'from_request_date': s_d1},
            'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'action': 'a', 'from_request_date': s_d1, 'to_request_date': s_d2},
            'paging_params': {}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'action': 'a', 'from_request_date': s_d1, 'to_request_date': s_d2,
            'remote_addr': 'a'},
            'paging_params': {'limit': 1}})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'filter_params': {'action': 'a', 'from_request_date': s_d1, 'to_request_date': s_d2,
            'remote_addr': 'a'},
            'paging_params': {'limit': 0, 'offset': 3}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 10, 'action_logs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 10, 'action_logs': [
            {'custom_client_info': None, 'action': 'a', 'request_date': s_d2,
                'remote_addr': 'a', 'request': 't', 'response': 't'},
            {'custom_client_info': 'i', 'action': 'a', 'request_date': s_d2,
                'remote_addr': 'b', 'request': 't', 'response': 't'},
        ]})
        self.validate_error_response(a_name)


if __name__ == '__main__':
    unittest.main()
