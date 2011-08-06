# coding=utf-8
import unittest

from helixcore.test.utils_for_testing import ActionsLogTester

from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixbilling.test.wsgi.client import Client
from helixbilling.test.logic import access_granted #@UnusedImport
from helixcore.security.auth import CoreAuthenticator
from helixbilling.test.logic.access_granted import (access_denied_call,
    access_granted_call)


class ActionLogTestCase(ActorLogicTestCase, ActionsLogTester):
    sess_id = 'action_log_test_session'

    def setUp(self):
        super(ActionLogTestCase, self).setUp()
        self.cli = Client()

    def test_get_currencies(self):
        action = 'get_currencies'
        req = {}
        self._not_logged_action(action, self.sess_id, req)

    def test_modify_used_currencies(self):
        action = 'modify_used_currencies'
        req = {'session_id': self.sess_id, 'new_currencies_codes': ['RUB']}
        self._logged_action(action, req)

    def test_get_action_logs(self):
        action = 'get_action_logs'
        self._not_logged_filtering_action(action, self.sess_id)

    def test_get_action_logs_self(self):
        action = 'get_action_logs_self'
        self._not_logged_filtering_action(action, self.sess_id)

    def test_add_balance(self):
        action = 'modify_used_currencies'
        req = {'session_id': self.sess_id, 'new_currencies_codes': ['RUB']}
        self._logged_action(action, req)

        action = 'add_balance'
        user_id = 4242
        req = {'session_id': self.sess_id, 'currency_code': 'RUB', 'user_id': user_id}
        self._logged_action(action, req)
        self._check_subject_users_ids_set(self.sess_id, action, user_id)

        action = 'add_balance'
        req = {'session_id': self.sess_id, 'currency_code': 'XXX', 'user_id': user_id}
        self._logged_action(action, req, check_resp=False)
        self._check_subject_users_ids_set(self.sess_id, action, user_id)

    def test_get_balances_self(self):
        action = 'get_balances_self'
        req = {'session_id': self.sess_id}
        self._not_logged_action(action, self.sess_id, req)

    def test_modify_balances(self):
        action = 'modify_used_currencies'
        req = {'session_id': self.sess_id, 'new_currencies_codes': ['RUB', 'BYR']}
        self._logged_action(action, req)

        action = 'add_balance'
        user_id = 4242
        req = {'session_id': self.sess_id, 'currency_code': 'RUB', 'user_id': user_id}
        resp = self.cli.add_balance(**req)
        self.check_response_ok(resp)
        balance_rub_id = resp['id']

        req = {'session_id': self.sess_id, 'currency_code': 'BYR', 'user_id': user_id}
        resp = self.cli.add_balance(**req)
        self.check_response_ok(resp)
        balance_byr_id = resp['id']

        action = 'modify_balances'
        req = {'session_id': self.sess_id, 'ids': [balance_rub_id, balance_byr_id],
            'new_is_active': False}
        self._logged_action(action, req, check_resp=False)
        self._check_subject_users_ids_set(self.sess_id, action, user_id)

    def test_add_receipt(self):
        action = 'modify_used_currencies'
        req = {'session_id': self.sess_id, 'new_currencies_codes': ['RUB', 'BYR']}
        self._logged_action(action, req)
        user_id = 4242

        # testing success action logged
        action = 'add_balance'
        req = {'session_id': self.sess_id, 'currency_code': 'RUB', 'user_id': user_id}
        resp = self.cli.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        action = 'add_receipt'
        req = {'session_id': self.sess_id, 'balance_id':balance_id, 'amount': '17.09'}
        self._logged_action(action, req, check_resp=False)
        self._check_subject_users_ids_set(self.sess_id, action, user_id)

    def test_add_bonus(self):
        action = 'modify_used_currencies'
        req = {'session_id': self.sess_id, 'new_currencies_codes': ['RUB', 'BYR']}
        self._logged_action(action, req)
        user_id = 4242

        # testing success action logged
        action = 'add_balance'
        req = {'session_id': self.sess_id, 'currency_code': 'RUB', 'user_id': user_id}
        resp = self.cli.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        action = 'add_bonus'
        req = {'session_id': self.sess_id, 'balance_id': balance_id, 'amount': '17.09'}
        self._logged_action(action, req, check_resp=False)
        self._check_subject_users_ids_set(self.sess_id, action, user_id)

    def test_lock(self):
        action = 'modify_used_currencies'
        req = {'session_id': self.sess_id, 'new_currencies_codes': ['RUB']}
        self._logged_action(action, req)

        user_id = 4242

        # testing success action logged
        action = 'add_balance'
        req = {'session_id': self.sess_id, 'currency_code': 'RUB', 'user_id': user_id}
        resp = self.cli.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        action = 'add_receipt'
        req = {'session_id': self.sess_id, 'balance_id': balance_id, 'amount': '17.09'}
        self._logged_action(action, req, check_resp=False)
        self._check_subject_users_ids_set(self.sess_id, action, user_id)

        action = 'lock'
        req = {'session_id': self.sess_id, 'balance_id': balance_id, 'amount': '17.09',
            'order_id': 'ord_id_4', 'locking_order': ['real_amount'], 'order_id': '1'}
        self._logged_action(action, req, check_resp=False)
        self._check_subject_users_ids_set(self.sess_id, action, user_id)

    def test_unlock(self):
        action = 'modify_used_currencies'
        req = {'session_id': self.sess_id, 'new_currencies_codes': ['RUB']}
        self._logged_action(action, req)

        user_id = 4242

        # testing success action logged
        action = 'add_balance'
        req = {'session_id': self.sess_id, 'currency_code': 'RUB', 'user_id': user_id}
        resp = self.cli.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        action = 'add_receipt'
        req = {'session_id': self.sess_id, 'balance_id': balance_id, 'amount': '17.09'}
        self._logged_action(action, req)
        self._check_subject_users_ids_set(self.sess_id, action, user_id)

        action = 'lock'
        req = {'session_id': self.sess_id, 'balance_id': balance_id, 'amount': '10',
            'locking_order': ['real_amount'], 'order_id': '2'}
        resp = self._logged_action(action, req)
        self._check_subject_users_ids_set(self.sess_id, action, user_id)
        lock_id = resp['lock_id']

        action = 'unlock'
        req = {'session_id': self.sess_id, 'balance_id': balance_id, 'lock_id': lock_id}
        resp = self._logged_action(action, req, check_resp=False)
        self._check_subject_users_ids_set(self.sess_id, action, user_id)

    def _logged_failed_action(self, action, req):
        logs_num = self._count_records(self.sess_id, action)
        api_call = getattr(self.cli, action)
        CoreAuthenticator.check_access = access_denied_call
        resp = api_call(**req)
        CoreAuthenticator.check_access = access_granted_call
        self.assertEquals('error', resp['status'])
        self.assertEquals(logs_num + 1, self._count_records(self.sess_id, action))

    def test_failed_actions_logged(self):
        action = 'modify_used_currencies'
        req = {'session_id': self.sess_id, 'new_currencies_codes': ['RUB']}
        self._logged_failed_action(action, req)

        user_id = 4242
        action = 'add_balance'
        req = {'session_id': self.sess_id, 'currency_code': 'RUB', 'user_id': user_id}
        self._logged_failed_action(action, req)

        fake_balance_id = 9999
        action = 'add_bonus'
        req = {'session_id': self.sess_id, 'balance_id': fake_balance_id, 'amount': '17.09'}
        self._logged_failed_action(action, req)

        action = 'add_receipt'
        req = {'session_id': self.sess_id, 'balance_id': fake_balance_id, 'amount': '17.09'}
        self._logged_action(action, req, check_resp=False)

    def test_get_locks(self):
        action = 'modify_used_currencies'
        req = {'session_id': self.sess_id, 'new_currencies_codes': ['RUB']}
        self._logged_action(action, req)
        user_id = 4242

        # testing success action logged
        action = 'add_balance'
        req = {'session_id': self.sess_id, 'currency_code': 'RUB', 'user_id': user_id}
        resp = self.cli.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        action = 'add_receipt'
        req = {'session_id': self.sess_id, 'balance_id': balance_id, 'amount': '17.09'}
        self._logged_action(action, req)
        self._check_subject_users_ids_set(self.sess_id, action, user_id)

        action = 'lock'
        req = {'session_id': self.sess_id, 'balance_id': balance_id, 'amount': '10',
            'locking_order': ['real_amount'], 'order_id': '4'}
        resp = self._logged_action(action, req)
        self._check_subject_users_ids_set(self.sess_id, action, user_id)

        action = 'get_locks'
        req = {'session_id': self.sess_id, 'filter_params': {'user_id': user_id},
            'paging_params': {}}
        resp = self._not_logged_action(action, self.sess_id, req)
        self.assertTrue(len(resp['locks']) > 0)

        action = 'get_locks_self'
        req = {'session_id': self.sess_id, 'filter_params': {}, 'paging_params': {}}
        resp = self._not_logged_action(action, self.sess_id, req)
        self.assertTrue(len(resp['locks']) == 0)

    def test_get_transactions(self):
        action = 'modify_used_currencies'
        req = {'session_id': self.sess_id, 'new_currencies_codes': ['RUB']}
        self._logged_action(action, req)
        user_id = 4242

        # testing success action logged
        action = 'add_balance'
        req = {'session_id': self.sess_id, 'currency_code': 'RUB', 'user_id': user_id}
        resp = self.cli.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        action = 'add_receipt'
        req = {'session_id': self.sess_id, 'balance_id': balance_id, 'amount': '17.09'}
        self._logged_action(action, req)
        self._check_subject_users_ids_set(self.sess_id, action, user_id)

        action = 'get_transactions'
        req = {'session_id': self.sess_id, 'filter_params': {'user_id': user_id},
            'paging_params': {}}
        resp = self._not_logged_action(action, self.sess_id, req)
        self.assertTrue(len(resp['transactions']) > 0)

        action = 'get_transactions_self'
        req = {'session_id': self.sess_id, 'filter_params': {}, 'paging_params': {}}
        resp = self._not_logged_action(action, self.sess_id, req)
        self.assertTrue(len(resp['transactions']) == 0)


if __name__ == '__main__':
    unittest.main()
