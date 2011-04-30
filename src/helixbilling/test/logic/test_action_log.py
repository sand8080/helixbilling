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


#    def _check_action_tracked(self, operator, action_name, custom_operator_info):
#        action_logs = self.get_action_logs(operator, {'action': action_name})
#        self.assertEqual(1, len(action_logs))
#        action_log = action_logs[0]
#        self.assertEqual(operator.id, action_log.operator_id)
#        self.assertEqual(action_name, action_log.action)
#        self.assertEqual(custom_operator_info, action_log.custom_operator_info)
#
#    def _make_trackable_action(self, operator, action_name, data):
#        self._make_action(action_name, data)
#        self._check_action_tracked(operator, action_name, data.get('custom_operator_info', None))
#
#    def _make_action(self, action_name, data):
#        auth_data = {'login': self.cli.login, 'password': self.cli.password}
#        auth_data.update(data)
#        m = getattr(self.cli, action_name)
#        m(**auth_data)
#
#    def test_unauthorized_tracking_action(self):
#        login = 'oper-action_log_test'
#        self.cli.add_operator(login=login, password='qaz') #IGNORE:E1101
#        self._check_action_tracked(self.get_operator_by_login(login), 'add_operator', None)
#
#    def test_tracking_error_action(self):
#        custom_operator_info = 'fake'
#        self.cli.add_operator(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
#            custom_operator_info=custom_operator_info)
#        operator = self.get_operator_by_login(self.cli.login)
#        self._check_action_tracked(operator, 'add_operator', custom_operator_info)
#        c_id = 'cc'
#        self._make_trackable_action(operator, 'add_balance', {'customer_id': c_id, 'active': True,
#            'currency': self.currency.code})
#
#    def test_tracking_action(self):
#        self.cli.add_operator(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
#        operator = self.get_operator_by_login(self.cli.login)
#
#        self._make_trackable_action(operator, 'modify_operator', {'custom_operator_info': 'jah',
#            'new_password': self.cli.password})
#
#        c_id = 'tracked customer'
#        self._make_trackable_action(operator, 'add_balance', {'customer_id': c_id, 'active': True,
#            'currency': self.currency.code})
#        self._make_trackable_action(operator, 'modify_balance', {'customer_id': c_id, 'new_active': True})
#        self._make_trackable_action(operator, 'delete_balance', {'customer_id': c_id})
#        self._make_action('add_balance', {'customer_id': c_id, 'active': True,
#            'currency': self.currency.code})
#
#        self._make_trackable_action(operator, 'enroll_receipt', {'customer_id': c_id, 'amount': '15.00'})
#        self._make_trackable_action(operator, 'enroll_bonus', {'customer_id': c_id, 'amount': '25.00'})
#
#        order_id = 'lock_unlock'
#        self._make_trackable_action(operator, 'balance_lock', {'customer_id': c_id, 'order_id': order_id,
#            'amount': '20.00'})
#
#        self._make_trackable_action(operator, 'balance_unlock', {'customer_id': c_id, 'order_id': order_id})
#
#        order_id = 'lock_chargeoff'
#        self._make_action('balance_lock', {'customer_id': c_id, 'order_id': order_id, 'amount': '22.00'})
#        self._make_trackable_action(operator, 'chargeoff', {'customer_id': c_id, 'order_id': order_id})
#
#        c_id_1 = 'customer for list operations'
#        self._make_action('add_balance', {'customer_id': c_id_1, 'active': True,
#            'currency': self.currency.code})
#        self._make_action('enroll_receipt', {'customer_id': c_id_1, 'amount': '16.00'})
#        self._make_action('enroll_bonus', {'customer_id': c_id_1, 'amount': '26.00'})
#
#        order_id = 'lock_list_unlock_list'
#        self._make_trackable_action(operator, 'balance_lock_list', {'locks': [
#            {'customer_id': c_id, 'order_id': order_id, 'amount': '0.01'},
#            {'customer_id': c_id_1, 'order_id': order_id, 'order_type': 'ot', 'amount': '0.01'},
#        ]})
#        self._make_trackable_action(operator, 'balance_unlock_list', {'unlocks': [
#            {'customer_id': c_id, 'order_id': order_id},
#            {'customer_id': c_id_1, 'order_id': order_id},
#        ]})
#
#        order_id = 'lock_list_chargeoff_list'
#        self._make_action('balance_lock_list', {'locks': [
#            {'customer_id': c_id, 'order_id': order_id, 'amount': '0.01'},
#            {'customer_id': c_id_1, 'order_id': order_id, 'order_type': 'ot', 'amount': '0.01'},
#        ]})
#        self._make_action('chargeoff_list', {'chargeoffs': [
#            {'customer_id': c_id, 'order_id': order_id},
#            {'customer_id': c_id_1, 'order_id': order_id},
#        ]})
#
#    def test_view_action_logs(self):
#        self.cli.add_operator(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
#        c_id_0 = 'view_action_logs_0'
#        c_id_1 = 'view_action_logs_1'
#        self._make_action('add_balance', {'customer_id': c_id_0, 'active': True, 'currency': self.currency.code})
#        self._make_action('add_balance', {'customer_id': c_id_1, 'active': True, 'currency': self.currency.code})
#        self._make_action('enroll_receipt', {'customer_id': c_id_0, 'amount': '15.00'})
#        self._make_action('enroll_bonus', {'customer_id': c_id_1, 'amount': '25.00'})
#        order_id_0 = '1'
#        self._make_action('balance_lock', {'customer_id': c_id_0, 'order_id': order_id_0, 'amount': '5.00'})
#        self._make_action('balance_lock', {'customer_id': c_id_1, 'order_id': order_id_0, 'amount': '6.00'})
#        order_id_1 = '2'
#        d_0 = datetime.datetime.now(pytz.utc)
#        self._make_action('balance_lock_list', {'locks': [
#            {'customer_id': c_id_0, 'order_id': order_id_1, 'amount': '7.00'},
#            {'customer_id': c_id_1, 'order_id': order_id_1, 'amount': '8.00'},
#        ]})
#        self._make_action('balance_unlock', {'customer_id': c_id_0, 'order_id': order_id_0})
#        self._make_action('balance_unlock_list', {'unlocks': [{'customer_id': c_id_1, 'order_id': order_id_0}]})
#
#        d_1 = datetime.datetime.now(pytz.utc)
#        self._make_action('chargeoff_list', {'chargeoffs': [{'customer_id': c_id_0, 'order_id': order_id_1},
#            {'customer_id': c_id_1, 'order_id': order_id_1},]})
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {},
#            'paging_params': {},
#        }
#        response = self.handle_action('view_action_logs', data)
#        self.assertEqual(11, response['total'])
#        self.assertEqual(11, len(response['action_logs']))
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'from_request_date': d_0.isoformat(), 'to_request_date': d_1.isoformat()},
#            'paging_params': {},
#        }
#        response = self.handle_action('view_action_logs', data)
#        self.assertEqual(3, len(response['action_logs']))
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'action': 'balance_lock'},
#            'paging_params': {},
#        }
#        response = self.handle_action('view_action_logs', data)
#        self.assertEqual(2, len(response['action_logs']))
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'customer_id': c_id_0},
#            'paging_params': {},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        self.assertEqual(6, len(al_info))
#        for al in al_info:
#            self.assertTrue(c_id_0 in al['customer_ids'])


if __name__ == '__main__':
    unittest.main()
