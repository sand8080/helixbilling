# coding=utf-8
import unittest

from helixcore.test.utils_for_testing import ActionsLogTester

from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixbilling.test.wsgi.client import Client
from helixbilling.test.logic import access_granted #@UnusedImport


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
        req = {'session_id': self.sess_id, 'currency_code': 'RUB', 'user_id': '4242'}
        self._logged_action(action, req)

    def test_get_balance_self(self):
        action = 'get_balance_self'
        req = {'session_id': self.sess_id}
        self._not_logged_action(action, self.sess_id, req)


if __name__ == '__main__':
    unittest.main()
