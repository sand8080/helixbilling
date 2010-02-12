# coding=utf-8
import unittest
import datetime
import pytz

from helixbilling.test.db_based_test import ServiceTestCase
from helixbilling.conf import settings
from helixbilling.test.wsgi.client import Client


class ActionLogTestCase(ServiceTestCase):
    def setUp(self):
        super(ActionLogTestCase, self).setUp()
        self.cli = Client(u'биллинг %s' % datetime.datetime.now(), 'qazwsx')

    def _check_action_tracked(self, operator, action_name, custom_operator_info):
        action_logs = self.get_action_logs(operator, {'action': action_name})
        self.assertEqual(1, len(action_logs))
        action_log = action_logs[0]
        self.assertEqual(operator.id, action_log.operator_id)
        self.assertEqual(action_name, action_log.action)
        self.assertEqual(custom_operator_info, action_log.custom_operator_info)

    def _make_trackable_action(self, operator, action_name, data):
        self._make_action(action_name, data)
        self._check_action_tracked(operator, action_name, data.get('custom_operator_info', None))

    def _make_action(self, action_name, data):
        auth_data = {'login': self.cli.login, 'password': self.cli.password}
        auth_data.update(data)
        m = getattr(self.cli, action_name)
        m(**auth_data)

    def test_unauthorized_tracking_action(self):
        login = 'oper-action_log_test'
        self.cli.add_operator(login=login, password='qaz') #IGNORE:E1101
        self._check_action_tracked(self.get_operator_by_login(login), 'add_operator', None)

    def test_tracking_error_action(self):
        custom_operator_info = 'fake'
        self.cli.add_operator(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
            custom_operator_info=custom_operator_info)
        operator = self.get_operator_by_login(self.cli.login)
        self._check_action_tracked(operator, 'add_operator', custom_operator_info)
        c_id = 'cc'
        self._make_trackable_action(operator, 'add_balance', {'customer_id': c_id, 'active': True,
            'currency': self.currency.code})

    def test_tracking_action(self):
        self.cli.add_operator(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
        operator = self.get_operator_by_login(self.cli.login)

        self._make_trackable_action(operator, 'modify_operator', {'custom_client_info': 'jah'})

#        old_st_name = 'service type'
#        self._make_trackable_action(operator, 'add_service_type', {'name': old_st_name})
#        st_name = 'new %s' % old_st_name
#        self._make_trackable_action(operator, 'modify_service_type', {'name': old_st_name,
#            'new_name': st_name})
#
#        old_ss_name = 'service set'
#        self._make_trackable_action(operator, 'add_service_set', {'name': old_ss_name,
#            'service_types': [st_name]})
#        ss_name = 'new %s' % old_ss_name
#        self._make_trackable_action(operator, 'modify_service_set', {'name': old_ss_name,
#            'new_name': ss_name})
#
#        old_t_name = 'tariff'
#        self._make_trackable_action(operator, 'add_tariff', {'name': old_t_name,
#            'parent_tariff': None, 'service_set': ss_name, 'in_archive': False})
#        t_name = 'new %s' % old_t_name
#        self._make_trackable_action(operator, 'modify_tariff', {'name': old_t_name,
#            'new_name': t_name, 'new_in_archive': True})
#
#        r_text = 'price = 1.0'
#        self._make_trackable_action(operator, 'save_draft_rule', {'tariff': t_name,
#            'service_type': st_name, 'rule': r_text, 'enabled': True})
#        self._make_trackable_action(operator, 'make_draft_rules_actual', {'tariff': t_name})
#        self._make_trackable_action(operator, 'modify_actual_rule', {'tariff': t_name,
#            'service_type': st_name, 'new_enabled': False})
#
#        self._make_trackable_action(operator, 'delete_tariff', {'name': t_name})
#        self.cli.modify_service_set(login=self.cli.login, password=self.cli.password, #IGNORE:E1101
#            name=ss_name, new_service_types=[])
#        self._make_trackable_action(operator, 'delete_service_set', {'name': ss_name})
#        self._make_trackable_action(operator, 'delete_service_type', {'name': st_name})
#
#    def test_view_action_logs(self):
#        self.cli.add_client(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
#
#        st_names = ['st 0', 'st 1', 'st 2']
#        date_0 = datetime.datetime.now(pytz.utc)
#        for st_name in st_names:
#            self._make_action('add_service_type', {'name': st_name})
#
#        ss_names = ['ss 0', 'ss 1']
#        date_1 = datetime.datetime.now(pytz.utc)
#        for ss_name in ss_names:
#            self._make_action('add_service_set', {'name': ss_name,
#                'service_types': st_names})
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        total = len(st_names) + len(ss_names) + 1
#        self.assertEqual(total, len(al_info))
#        self.assertEqual(total, response['total'])
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'action': 'add_service_type'},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        self.assertEqual(len(st_names), len(al_info))
#        self.assertEqual(0, len(filter(lambda x: x['action'] != 'add_service_type', al_info)))
#        self.assertEqual(len(st_names), response['total'])
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'action': 'add_service_type', 'limit': 2},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        self.assertEqual(2, len(al_info))
#        self.assertEqual(0, len(filter(lambda x: x['action'] != 'add_service_type', al_info)))
#        self.assertEqual(len(st_names), response['total'])
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'action': 'add_service_type', 'offset': 2},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        self.assertEqual(1, len(al_info))
#        self.assertEqual(0, len(filter(lambda x: x['action'] != 'add_service_type', al_info)))
#        self.assertEqual(len(st_names), response['total'])
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'from_date': date_1.isoformat()},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        self.assertEqual(len(ss_names), len(al_info))
#        self.assertEqual(0, len(filter(lambda x: x['action'] != 'add_service_set', al_info)))
#        self.assertEqual(len(ss_names), response['total'])
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'from_date': date_0.isoformat(), 'to_date': date_1.isoformat()},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        self.assertEqual(len(st_names), len(al_info))
#        self.assertEqual(0, len(filter(lambda x: x['action'] != 'add_service_type', al_info)))
#        self.assertEqual(len(st_names), response['total'])


if __name__ == '__main__':
    unittest.main()
