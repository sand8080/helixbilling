import unittest

from helixcore.error import RequestProcessingError

from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixbilling.test.logic import access_granted #@UnusedImport
from helixbilling.conf.db import transaction
from helixbilling.db.filters import BalanceFilter


class BalanceTestCase(ActorLogicTestCase):
    @transaction()
    def test_add_balance(self, curs=None):
        sess = self.login_actor()
        user_id = '4444'

        # not used currency
        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'RUB'}
        self.assertRaises(RequestProcessingError, self.add_balance, **req)

        req = {'session_id': sess.session_id, 'new_currencies_codes': ['RUB', 'BZD']}
        resp = self.modify_used_currencies(**req)
        self.check_response_ok(resp)

        # correct balance creation
        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'RUB'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_f = BalanceFilter(sess, {'id': resp['id']}, {}, {})
        balance = balance_f.filter_one_obj(curs)
        self.assertEquals(True, balance.is_active)
        self.assertEquals(sess.environment_id, balance.environment_id)
        self.assertEquals(0, balance.overdraft_limit)
        self.assertEquals(0, balance.available_real_amount)
        self.assertEquals(0, balance.available_virtual_amount)
        self.assertEquals(0, balance.locked_amount)
        self.assertEquals(None, balance.locking_order)

        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'BZD',
            'overdraft_limit': '102.30', 'locking_order': ['available_real_amount']}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_f = BalanceFilter(sess, {'id': resp['id']}, {}, {})
        balance = balance_f.filter_one_obj(curs)
        self.assertEquals(True, balance.is_active)
        self.assertEquals(sess.environment_id, balance.environment_id)
        self.assertEquals(10230, balance.overdraft_limit)
        self.assertEquals(0, balance.available_real_amount)
        self.assertEquals(0, balance.available_virtual_amount)
        self.assertEquals(0, balance.locked_amount)
        self.assertEquals(['available_real_amount'], balance.locking_order)

        # wrong currency code
        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'XXX'}
        self.assertRaises(RequestProcessingError, self.add_balance, **req)

        # adding balance with duplicate currency
        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'RUB'}
        self.assertRaises(RequestProcessingError, self.add_balance, **req)

    @transaction()
    def test_modify_balance(self, curs=None):
        sess = self.login_actor()

        req = {'session_id': sess.session_id, 'new_currencies_codes': ['RUB']}
        resp = self.modify_used_currencies(**req)
        self.check_response_ok(resp)

        user_id='U-23-52'
        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'RUB'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        balance_f = BalanceFilter(sess, {'id': balance_id}, {}, {})
        balance = balance_f.filter_one_obj(curs)
        self.assertEquals(True, balance.is_active)
        self.assertEquals(sess.environment_id, balance.environment_id)
        self.assertEquals(user_id, balance.user_id)
        self.assertEquals(0, balance.overdraft_limit)
        self.assertEquals(0, balance.available_real_amount)
        self.assertEquals(0, balance.available_virtual_amount)
        self.assertEquals(0, balance.locked_amount)
        self.assertEquals(None, balance.locking_order)

        req = {'session_id': sess.session_id, 'user_id': user_id,
            'new_is_active': False, 'new_overdraft_limit': '100',
            'new_locking_order': ['available_real_amount', 'available_virtual_amount']}
        resp = self.modify_balance(**req)
        self.check_response_ok(resp)

        balance_f = BalanceFilter(sess, {'id': balance_id}, {}, {})
        balance = balance_f.filter_one_obj(curs)
        self.assertEquals(False, balance.is_active)
        self.assertEquals(sess.environment_id, balance.environment_id)
        self.assertEquals(user_id, balance.user_id)
        self.assertEquals(10000, balance.overdraft_limit)
        self.assertEquals(0, balance.available_real_amount)
        self.assertEquals(0, balance.available_virtual_amount)
        self.assertEquals(0, balance.locked_amount)
        self.assertEquals(['available_real_amount', 'available_virtual_amount'],
            balance.locking_order)


#    def test_get_balance(self):
#        c_id = 'cu54'
#        self.add_balance(self.test_login, self.test_password, c_id, self.currency)
#        response = self.handle_action('get_balance', {
#            'login': self.test_login,
#            'password': self.test_password,
#            'customer_id': c_id
#        })
#        self.assertEqual(True, response['active'])
#        self.assertEqual(c_id, response['customer_id'])
#        self.assertEqual(self.currency.code, response['currency_code']) #IGNORE:E1103
#        self.assertEqual(Decimal('0.0'), Decimal(response['available_real_amount']))
#        self.assertEqual(Decimal('0.0'), Decimal(response['available_virtual_amount']))
#        self.assertEqual(Decimal('0.0'), Decimal(response['overdraft_limit']))
#        self.assertEqual(Decimal('0.0'), Decimal(response['locked_amount']))
#        self.assertEqual(None, response['locking_order'])
#
#    def test_view_balances(self):
#        l, p = 't', 'p'
#        self.add_operator('t', 'p')
#        c_ids = list('abcdef')
#        for idx, c_id in enumerate(c_ids):
#            self.add_balance(l, p, c_id, self.currency, overdraft_limit='%s' % idx,
#                locking_order=['available_real_amount'])
#        expected_c_ids = c_ids[:3]
#        response = self.handle_action('view_balances', {
#            'login': l, 'password': p,
#            'filter_params': {'customer_ids': expected_c_ids},
#            'paging_params': {},
#        })
#        b_info = response['balances']
#        self.assertEqual(len(expected_c_ids), len(b_info))
#        self.assertEqual(response['total'], len(expected_c_ids))
#        actual_c_ids = [i['customer_id'] for i in b_info]
#        self.assertEqual(sorted(actual_c_ids), sorted(expected_c_ids))
#
#        offset = 2
#        expected_c_ids = c_ids[offset:]
#        response = self.handle_action('view_balances', {
#            'login': l, 'password': p,
#            'filter_params': {},
#            'paging_params': {'offset': offset},
#        })
#        b_info = response['balances']
#        self.assertEqual(len(expected_c_ids), len(b_info))
#        self.assertEqual(response['total'], len(c_ids))
#        actual_c_ids = [i['customer_id'] for i in b_info]
#        self.assertEqual(sorted(actual_c_ids), sorted(expected_c_ids))
#
#        offset = 1
#        limit = 2
#        expected_c_ids = c_ids[offset:offset + limit]
#        response = self.handle_action('view_balances', {
#            'login': l, 'password': p,
#            'filter_params': {},
#            'paging_params': {'offset': offset, 'limit': 2}
#        })
#        b_info = response['balances']
#        self.assertEqual(len(expected_c_ids), len(b_info))
#        self.assertEqual(response['total'], len(c_ids))
#        actual_c_ids = [i['customer_id'] for i in b_info]
#        self.assertEqual(sorted(actual_c_ids), sorted(expected_c_ids))


if __name__ == '__main__':
    unittest.main()