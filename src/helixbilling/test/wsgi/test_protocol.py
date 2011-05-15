# coding=utf-8
import unittest

from helixcore.server.api import Api
from helixcore.test.utils_for_testing import ProtocolTester

from helixbilling.test.root_test import RootTestCase
from helixbilling.wsgi.protocol import protocol
import datetime
import pytz


class ProtocolTestCase(RootTestCase, ProtocolTester):
    api = Api(protocol)

    def test_login(self):
        a_name = 'login'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'environment_name': 'e', 'custom_actor_info': 'i'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'environment_name': 'n'})

        self.api.validate_response(a_name, {'status': 'ok', 'session_id': 'i',
            'user_id': 5, 'environment_id': 7})
        self.validate_error_response(a_name)

    def test_logout(self):
        a_name = 'logout'
        self.api.validate_request(a_name, {'session_id': 'i'})
        self.validate_status_response(a_name)

    def test_get_currencies(self):
        a_name = 'get_currencies'
        self.api.validate_request(a_name, {'session_id': 's'})
        self.api.validate_request(a_name, {'session_id': 's',
            'ordering_params': ['code']})
        self.api.validate_request(a_name, {'session_id': 's',
            'ordering_params': ['-code']})

        self.api.validate_response(a_name, {'status': 'ok', 'currencies': []})
        self.api.validate_response(a_name, {'status': 'ok', 'currencies': [
            {'id': 1, 'code': 'YYY', 'name': 'y',
                'location': 'y', 'cent_factor': 100}
        ]})
        self.validate_error_response(a_name)

    def test_get_used_currencies(self):
        a_name = 'get_used_currencies'
        self.api.validate_request(a_name, {'session_id': 's'})
        self.api.validate_request(a_name, {'session_id': 's',
            'ordering_params': ['code']})
        self.api.validate_request(a_name, {'session_id': 's',
            'ordering_params': ['-code']})

        self.api.validate_response(a_name, {'status': 'ok', 'currencies': []})
        self.api.validate_response(a_name, {'status': 'ok', 'currencies': [
            {'id': 1, 'code': 'YYY', 'name': 'y',
                'location': 'y', 'cent_factor': 100}
        ]})
        self.validate_error_response(a_name)

    def test_modify_used_currencies(self):
        a_name = 'modify_used_currencies'
        self.api.validate_request(a_name, {'session_id': 's'})
        self.api.validate_request(a_name, {'session_id': 's',
            'new_currencies_codes': []})
        self.api.validate_request(a_name, {'session_id': 's',
            'new_currencies_codes': ['XXX', 'RUR', 'RUB']})

        self.validate_status_response(a_name)

    def test_get_action_logs(self):
        a_name = 'get_action_logs'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'from_request_date': '2011-02-21 00:00:00',
            'to_request_date': '2011-02-21 23:59:59'},
            'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'action': 'a'}, 'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'user_id': 1}, 'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'session_id': ''}, 'paging_params': {}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'action_logs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'action_logs': [
            {
                'id': 42, 'session_id': 's_id', 'custom_actor_info': None,
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.1', 'request': 'req',
                'response': 'resp'
            },
        ]})
        self.validate_error_response(a_name)

    def test_get_action_logs_self(self):
        a_name = 'get_action_logs_self'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'from_request_date': '2011-02-21 00:00:00',
            'to_request_date': '2011-02-21 23:59:59'},
            'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'action': 'a'}, 'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'session_id': ''}, 'paging_params': {}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'action_logs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'action_logs': [
            {
                'id': 42, 'session_id': 's_id', 'custom_actor_info': None,
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.1', 'request': 'req',
                'response': 'resp'
            },
        ]})
        self.validate_error_response(a_name)

    def test_add_balance(self):
        a_name = 'add_balance'
        self.api.validate_request(a_name, {'session_id': 'i',
            'user_id': 23, 'currency_code': 'YYY'})
        self.api.validate_request(a_name, {'session_id': 'i',
            'user_id': 23, 'is_active': True, 'currency_code': 'YYY',
            'overdraft_limit': '500.50'})
        self.api.validate_request(a_name, {'session_id': 'i',
            'user_id': 23, 'is_active': True, 'currency_code': 'YYY',
            'overdraft_limit': '500.50', 'locking_order': [
                'available_real_amount', 'available_virtual_amount'
            ]})
        self.api.validate_request(a_name, {'session_id': 'i',
            'user_id': 23, 'is_active': False, 'currency_code': 'YYY',
            'overdraft_limit': '500.50', 'locking_order': [
                'available_real_amount'
            ]})
        self.api.validate_request(a_name, {'session_id': 'i',
            'user_id': 23, 'is_active': False, 'currency_code': 'YYY',
            'overdraft_limit': '500.50', 'locking_order': None})
        self.api.validate_request(a_name, {'session_id': 'i',
            'user_id': 23, 'is_active': False, 'currency_code': 'YYY',
            'overdraft_limit': '500.50', 'check_user_exist': True})

        self.api.validate_response(a_name, {'status': 'ok', 'id': 1})
        self.validate_error_response(a_name)

    def test_modify_balances(self):
        a_name = 'modify_balances'
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [2], 'new_is_active': True,
            'new_overdraft_limit': '500.50', 'new_locking_order': None})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [2, 3, 4], 'new_is_active': True,
            'new_overdraft_limit': '500.50', 'new_locking_order': None})

        self.validate_status_response(a_name)

    def test_get_balance_self(self):
        a_name = 'get_balance_self'
        self.api.validate_request(a_name, {'session_id': 'i'})

        self.api.validate_response(a_name, {'status': 'ok', 'balances': [
                {'id': 2, 'user_id': 3, 'is_active': True, 'currency_code': 'RUB',
                'available_real_amount': '3.15', 'available_virtual_amount': '0.0',
                'locked_amount': '14.09', 'overdraft_limit': '0.14',
                'locking_order': ['available_real_amount', 'available_virtual_amount']}
            ],
            'total': 1,
        })
        self.validate_error_response(a_name)

    def test_get_balances(self):
        a_name = 'get_balances'
        self.api.validate_request(a_name, {'session_id': 'i',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 'i',
            'filter_params': {},
            'paging_params': {'limit': 0, 'offset': 0,}})
        self.api.validate_request(a_name, {'session_id': 'i',
            'filter_params': {'users_ids': [], 'is_active': True,
            'currency_code': 'XXX',
            'from_available_real_amount': '1.0',
            'to_available_real_amount': '2.01',
            'from_available_virtual_amount': '7.10',
            'to_available_virtual_amount': '19.01',
            'from_overdraft_limit': '600.17', 'to_overdraft_limit': '700',
            'from_locked_amount': '41.24', 'to_locked_amount': '50',},
            'paging_params': {}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'balances': [
                {
                    'id': 22, 'user_id': 4, 'is_active': True,
                    'currency_code': 'RU', 'available_real_amount': '3.15',
                    'available_virtual_amount': '0.0',
                    'locked_amount': '14.09', 'overdraft_limit': '0.14',
                    'locking_order': ['available_real_amount', 'available_virtual_amount'],
                },
            ]
        })
        self.validate_error_response(a_name)

#    def enroll_income(self, a_name):
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'customer_id': 'N5',
#            'amount': '0.0'})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'customer_id': 'N5',
#            'amount': '10.01'})
#        self.validate_status_response(a_name)
#
#    def view_income(self, a_name, res_name):
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a', 'b']}, 'paging_params': {}})
#        d = datetime.datetime.now(pytz.utc)
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a', 'b'], 'from_creation_date': d.isoformat()},
#            'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a', 'b'], 'from_creation_date': d.isoformat(),
#            'to_creation_date': d.isoformat()},
#            'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {}, 'paging_params': {},
#            'ordering_params': ['creation_date']})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {}, 'paging_params': {},
#            'ordering_params': ['-creation_date']})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 10,
#            res_name: []})
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 10,
#            res_name: [
#                {'customer_id': 'U2', 'amount': '1.1', 'currency': 'YYY', 'creation_date': d.isoformat()},
#                {'customer_id': 'U2', 'amount': '1.1', 'currency': 'ZZZ', 'creation_date': d.isoformat()},
#            ]
#        })
#        self.validate_error_response(a_name)
#
#    def test_enroll_receipt(self):
#        self.enroll_income('enroll_receipt')
#
#    def test_view_receipts(self):
#        self.view_income('view_receipts', 'receipts')
#
#    def test_enroll_bonus(self):
#        self.enroll_income('enroll_bonus')
#
#    def test_view_bonuses(self):
#        self.view_income('view_bonuses', 'bonuses')
#
#    def test_balance_lock(self):
#        a_name = 'balance_lock'
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'customer_id': 'id', 'order_id': '1', 'amount': '60.00'})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'customer_id': 'id', 'order_id': '1', 'order_type': 'super', 'amount': '60.00'})
#        self.validate_status_response(a_name)
#
#    def test_balance_lock_list(self):
#        a_name = 'balance_lock_list'
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'locks': []})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'locks': [
#            {'customer_id': 'c0', 'order_id': '110', 'amount': '60.00'},
#            {'customer_id': 'c1', 'order_id': '10', 'order_type': 'space', 'amount': '50.00'},
#        ]})
#        self.validate_status_response(a_name)
#
#    def test_view_balance_locks(self):
#        a_name = 'view_balance_locks'
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a', 'b']}, 'paging_params': {}})
#        d = datetime.datetime.now(pytz.utc)
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'filter_params':
#            {'customer_ids': [], 'from_locking_date': d.isoformat()},
#            'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': [], 'from_locking_date': d.isoformat(),
#            'to_locking_date': d.isoformat()}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'from_locking_date': d.isoformat(),
#            'to_locking_date': d.isoformat()}, 'paging_params': {'limit': 5}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'from_locking_date': d.isoformat(),
#            'to_locking_date': d.isoformat()}, 'paging_params': {'limit': 5, 'offset': 10}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'from_locking_date': d.isoformat(),
#            'to_locking_date': d.isoformat(), 'order_id': '77H'}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'from_locking_date': d.isoformat(),
#            'to_locking_date': d.isoformat(), 'order_type': 'moon'}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'from_locking_date': d.isoformat(),
#            'to_locking_date': d.isoformat(), 'order_type': None}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {}, 'paging_params': {},
#            'ordering_params': []})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {}, 'paging_params': {},
#            'ordering_params': ['locking_date']})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {}, 'paging_params': {},
#            'ordering_params': ['-locking_date']})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 0, 'balance_locks': []})
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 10,
#            'balance_locks': [
#                {'customer_id': 'U2', 'order_id': 'k9', 'order_type': 'mia', 'real_amount': '2.49',
#                    'virtual_amount': '0.0', 'locking_date': d.isoformat(), 'currency': 'YYY'},
#                {'customer_id': 'U3', 'order_id': 'k9', 'order_type': None, 'real_amount': '2.49',
#                    'virtual_amount': '0.0', 'locking_date': d.isoformat(), 'currency': 'YES'},
#            ]
#        })
#        self.validate_error_response(a_name)
#
#    def test_balance_unlock(self):
#        a_name = 'balance_unlock'
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'customer_id': 'id', 'order_id': '1'})
#        self.validate_status_response(a_name)
#
#    def test_balance_unlock_list(self):
#        a_name = 'balance_unlock_list'
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'unlocks': []})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'unlocks': [
#            {'customer_id': 'c0', 'order_id': '110'},
#            {'customer_id': 'c1', 'order_id': '10'},
#        ]})
#        self.validate_status_response(a_name)
#
#    def test_chargeoff(self):
#        a_name = 'chargeoff'
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'customer_id': 'id', 'order_id': '1'})
#        self.validate_status_response(a_name)
#
#    def test_chargeoff_list(self):
#        a_name = 'chargeoff_list'
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'chargeoffs': []})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'chargeoffs': [
#            {'customer_id': 'c0', 'order_id': '110'},
#            {'customer_id': 'c1', 'order_id': '10'},
#        ]})
#        self.validate_status_response(a_name)
#
#    def test_view_chargeoffs(self):
#        a_name = 'view_chargeoffs'
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a', 'b']}, 'paging_params': {}})
#        d = datetime.datetime.now(pytz.utc)
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'filter_params':
#            {'customer_ids': [], 'from_chargeoff_date': d.isoformat()},
#            'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': [], 'from_chargeoff_date': d.isoformat(),
#            'to_chargeoff_date': d.isoformat()}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'from_chargeoff_date': d.isoformat(),
#            'to_chargeoff_date': d.isoformat()}, 'paging_params': {'limit': 5}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'from_chargeoff_date': d.isoformat(),
#            'to_chargeoff_date': d.isoformat()}, 'paging_params': {'limit': 5, 'offset': 10}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'from_chargeoff_date': d.isoformat(),
#            'to_chargeoff_date': d.isoformat(), 'order_id': '77H'}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'from_chargeoff_date': d.isoformat(),
#            'to_chargeoff_date': d.isoformat(), 'order_type': 'moon'}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'from_chargeoff_date': d.isoformat(),
#            'to_chargeoff_date': d.isoformat(), 'order_type': None}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'from_locking_date': d.isoformat(),
#            'to_locking_date': d.isoformat(), 'order_type': None}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {}, 'paging_params': {}, 'ordering_params': []})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {}, 'paging_params': {}, 'ordering_params': ['chargeoff_date']})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {}, 'paging_params': {}, 'ordering_params': ['-chargeoff_date']})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 0, 'chargeoffs': []})
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 10,
#            'chargeoffs': [
#                {'customer_id': 'U2', 'order_id': 'k9', 'order_type': 'mia', 'real_amount': '2.49',
#                    'virtual_amount': '0.0','chargeoff_date': d.isoformat(),
#                    'locking_date': d.isoformat(), 'currency': 'YYY'},
#                {'customer_id': 'U3', 'order_id': 'k9', 'order_type': None, 'real_amount': '2.49',
#                    'virtual_amount': '0.0', 'chargeoff_date': d.isoformat(),
#                    'locking_date': d.isoformat(), 'currency': 'YES'},
#            ]
#        })
#        self.validate_error_response(a_name)
#
#    def test_order_status(self):
#        a_name = 'order_status'
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'customer_id': 'c',
#            'order_id': 'r'})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'customer_id': 'c', 'order_id': '1',
#            'order_status': ORDER_STATUS_UNKNOWN, 'real_amount': None, 'virtual_amount': None,
#            'locking_date': None, 'chargeoff_date': None})
#        self.validate_error_response(a_name)
#        d = datetime.datetime.now(pytz.utc)
#        self.api.validate_response(a_name, {'status': 'ok', 'customer_id': 'c', 'order_id': '1',
#            'order_status': ORDER_STATUS_LOCKED, 'real_amount': '1.09', 'virtual_amount': '0',
#            'locking_date': d.isoformat(), 'chargeoff_date': None})
#        self.api.validate_response(a_name, {'status': 'ok', 'customer_id': 'c', 'order_id': '1',
#            'order_status': ORDER_STATUS_CHARGED_OFF, 'real_amount': '1.09', 'virtual_amount': '0',
#            'locking_date': d.isoformat(), 'chargeoff_date': d.isoformat()})
#        self.validate_error_response(a_name)
#
#    def test_view_order_statuses(self):
#        a_name = 'view_order_statuses'
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'filter_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a']}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'order_types': ['t']}})
#        d = datetime.datetime.now(pytz.utc)
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'order_types': ['t'],
#            'from_locking_date': d.isoformat()}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'order_types': ['t'],
#            'from_locking_date': d.isoformat(), 'to_locking_date': d.isoformat()}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'order_types': ['t'],
#            'from_locking_date': d.isoformat(), 'to_locking_date': d.isoformat(),
#            'from_chargeoff_date': d.isoformat()}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'customer_ids': ['a'], 'order_types': ['t'],
#            'from_locking_date': d.isoformat(), 'to_locking_date': d.isoformat(),
#            'from_chargeoff_date': d.isoformat(), 'to_chargeoff_date': d.isoformat()}})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'order_statuses': [
#            {'customer_id': 'c', 'order_id': '1', 'order_status': ORDER_STATUS_UNKNOWN,
#                'real_amount': None, 'virtual_amount': None, 'locking_date': None,
#                'chargeoff_date': None},
#            ]})
#        self.api.validate_response(a_name, {'status': 'ok', 'order_statuses': [
#            {'customer_id': 'c', 'order_id': '1', 'order_status': ORDER_STATUS_LOCKED,
#                'real_amount': '1.0', 'virtual_amount': '0', 'locking_date': d.isoformat(),
#                'chargeoff_date': None},
#            {'customer_id': 'c', 'order_id': '1', 'order_status': ORDER_STATUS_CHARGED_OFF,
#                'real_amount': '1.0', 'virtual_amount': '0', 'locking_date': d.isoformat(),
#                'chargeoff_date': d.isoformat()},
#            ]})
#        self.validate_error_response(a_name)
#
#    def test_view_action_logs(self):
#        a_name = 'view_action_logs'
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'action': 'a'}, 'paging_params': {}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'action': 'a'}, 'paging_params': {'limit': 4}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
#            'filter_params': {'action': 'a'}, 'paging_params': {}})
#        s_d1 = datetime.datetime(year=2009, month=10, day=29, tzinfo=pytz.utc).isoformat()
#        s_d2 = datetime.datetime.now(pytz.utc).isoformat()
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'paging_params': {},
#            'filter_params': {'action': 'a', 'from_request_date': s_d1}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'paging_params': {},
#            'filter_params': {'action': 'a', 'from_request_date': s_d1, 'customer_id': '1'}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'paging_params': {},
#            'filter_params': {'action': 'a', 'from_request_date': s_d1, 'to_request_date': s_d2}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'paging_params': {'limit': 1},
#            'filter_params': {'action': 'a', 'from_request_date': s_d1, 'to_request_date': s_d2, 'remote_addr': 'a'}})
#        self.api.validate_request(a_name, {'login': 'l', 'password': 'p', 'paging_params': {'limit': 0, 'offset': 3},
#            'filter_params': {'action': 'a', 'from_request_date': s_d1, 'to_request_date': s_d2, 'remote_addr': 'a'}})
#
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 10, 'action_logs': []})
#        self.api.validate_response(a_name, {'status': 'ok', 'total': 10, 'action_logs': [
#            {'custom_operator_info': None, 'action': 'a', 'request_date': s_d2,
#                'customer_ids': [], 'remote_addr': 'a', 'request': 't', 'response': 't'},
#            {'custom_operator_info': 'i', 'action': 'a', 'request_date': s_d2,
#                'customer_ids': ['a', 'b'], 'remote_addr': 'b', 'request': 't', 'response': 't'},
#        ]})
#        self.validate_error_response(a_name)


if __name__ == '__main__':
    unittest.main()
