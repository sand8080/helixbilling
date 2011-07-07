import unittest

from helixcore.error import RequestProcessingError, HelixcoreException

from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixbilling.test.logic import access_granted #@UnusedImport
from helixbilling.conf.db import transaction
from helixbilling.db.filters import BalanceFilter
from helixcore.security.auth import CoreAuthenticator


class BalanceTestCase(ActorLogicTestCase):
    def test_add_balance_with_user_checking(self):
        sess = self.login_actor()
        user_id = sess.user_id
        self.set_used_currencies(sess, ['RUB', 'BZD'])

        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'RUB',
            'check_user_exist': True}
        self.assertRaises(HelixcoreException, self.add_balance, **req)

        def user_exist(_, __, ___):
            return {'status': 'ok', 'exist': True}
        CoreAuthenticator.check_user_exist = user_exist
        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'RUB',
            'check_user_exist': True}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)

    @transaction()
    def test_add_balance(self, curs=None):
        sess = self.login_actor()
        user_id = 4444

        # not used currency
        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'RUB'}
        self.assertRaises(RequestProcessingError, self.add_balance, **req)

        self.set_used_currencies(sess, ['RUB', 'BZD'])

        # correct balance creation
        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'RUB'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_f = BalanceFilter(sess, {'id': resp['id']}, {}, {})
        balance = balance_f.filter_one_obj(curs)
        self.assertEquals(True, balance.is_active)
        self.assertEquals(sess.environment_id, balance.environment_id)
        self.assertEquals(0, balance.overdraft_limit)
        self.assertEquals(0, balance.real_amount)
        self.assertEquals(0, balance.virtual_amount)
        self.assertEquals(0, balance.locked_amount)

        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'BZD',
            'overdraft_limit': '102.30'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_f = BalanceFilter(sess, {'id': resp['id']}, {}, {})
        balance = balance_f.filter_one_obj(curs)
        self.assertEquals(True, balance.is_active)
        self.assertEquals(sess.environment_id, balance.environment_id)
        self.assertEquals(10230, balance.overdraft_limit)
        self.assertEquals(0, balance.real_amount)
        self.assertEquals(0, balance.virtual_amount)
        self.assertEquals(0, balance.locked_amount)

        # wrong currency code
        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'XXX'}
        self.assertRaises(RequestProcessingError, self.add_balance, **req)

        # adding duplicate balance
        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'RUB'}
        self.assertRaises(RequestProcessingError, self.add_balance, **req)

    def test_modify_balances(self):
        sess = self.login_actor()
        self.set_used_currencies(sess, ['RUB', 'BYR', 'CNY'])

        # Adding balances to user
        user_id = 23
        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'RUB'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_rub_id = resp['id']

        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'BYR'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_byr_id = resp['id']

        req = {'session_id': sess.session_id, 'user_id': user_id, 'currency_code': 'CNY'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_cny_id = resp['id']

        # Checking set parameters
        req = {'session_id': sess.session_id, 'filter_params': {'id': balance_rub_id},
            'paging_params': {}}
        resp = self.get_balances(**req)
        self.check_response_ok(resp)
        balances = resp['balances']
        self.assertEquals(1, len(balances))
        balance = balances[0]
        self.assertEquals(balance_rub_id, balance['id'])
        self.assertEquals(True, balance['is_active'])
        self.assertEquals(user_id, balance['user_id'])
        self.assertEquals('0.00', balance['overdraft_limit'])
        self.assertEquals('0.00', balance['real_amount'])
        self.assertEquals('0.00', balance['virtual_amount'])
        self.assertEquals('0.00', balance['locked_amount'])

        # Balances modification
        req = {'session_id': sess.session_id, 'ids': [balance_rub_id, balance_byr_id,
            balance_cny_id, 10000], 'new_is_active': False,
            'new_overdraft_limit': '100.0'}
        resp = self.modify_balances(**req)
        self.check_response_ok(resp)

        # Checking modification
        req = {'session_id': sess.session_id,
            'filter_params': {'id': balance_rub_id}, 'paging_params': {}}
        resp = self.get_balances(**req)
        self.check_response_ok(resp)
        balances = resp['balances']
        self.assertEquals(1, len(balances))
        balance = balances[0]

        self.assertEquals(balance_rub_id, balance['id'])
        self.assertEquals(False, balance['is_active'])
        self.assertEquals(user_id, balance['user_id'])
        self.assertEquals('100.00', balance['overdraft_limit'])
        self.assertEquals('0.00', balance['real_amount'])
        self.assertEquals('0.00', balance['virtual_amount'])
        self.assertEquals('0.00', balance['locked_amount'])

        req = {'session_id': sess.session_id,
            'filter_params': {'id': balance_byr_id}, 'paging_params': {}}
        resp = self.get_balances(**req)
        self.check_response_ok(resp)
        balances = resp['balances']
        self.assertEquals(1, len(balances))
        balance = balances[0]

        self.assertEquals(balance_byr_id, balance['id'])
        self.assertEquals(False, balance['is_active'])
        self.assertEquals(user_id, balance['user_id'])
        self.assertEquals('100.0', balance['overdraft_limit'])
        self.assertEquals('0.0', balance['real_amount'])
        self.assertEquals('0.0', balance['virtual_amount'])
        self.assertEquals('0.0', balance['locked_amount'])

        req = {'session_id': sess.session_id,
            'filter_params': {'id': balance_cny_id}, 'paging_params': {}}
        resp = self.get_balances(**req)
        self.check_response_ok(resp)
        balances = resp['balances']
        self.assertEquals(1, len(balances))
        balance = balances[0]

        self.assertEquals(balance_cny_id, balance['id'])
        self.assertEquals(False, balance['is_active'])
        self.assertEquals(user_id, balance['user_id'])
        self.assertEquals('100.0', balance['overdraft_limit'])
        self.assertEquals('0.0', balance['real_amount'])
        self.assertEquals('0.0', balance['virtual_amount'])
        self.assertEquals('0.0', balance['locked_amount'])

        # Modification without changing overdraft limit
        req = {'session_id': sess.session_id, 'ids': [balance_rub_id],
            'new_is_active': True, 'new_overdraft_limit': '100.0'}
        resp = self.modify_balances(**req)
        self.check_response_ok(resp)

        req = {'session_id': sess.session_id,
            'filter_params': {'id': balance_rub_id}, 'paging_params': {}}
        resp = self.get_balances(**req)
        self.check_response_ok(resp)
        balances = resp['balances']
        self.assertEquals(1, len(balances))
        balance = balances[0]

        self.assertEquals(balance_rub_id, balance['id'])
        self.assertEquals(True, balance['is_active'])
        self.assertEquals(user_id, balance['user_id'])
        self.assertEquals('100.00', balance['overdraft_limit'])
        self.assertEquals('0.00', balance['real_amount'])
        self.assertEquals('0.00', balance['virtual_amount'])
        self.assertEquals('0.00', balance['locked_amount'])

    def test_get_balances_self(self):
        sess = self.login_actor()

        self.set_used_currencies(sess, ['RUB', 'BYR'])

        req = {'session_id': sess.session_id}
        resp = self.get_balances_self(**req)
        self.check_response_ok(resp)
        self.assertEquals([], resp['balances'])
        self.assertEquals(0, resp['total'])

        # adding first balance
        req = {'session_id': sess.session_id, 'user_id': sess.user_id, 'currency_code': 'RUB'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        req = {'session_id': sess.session_id}
        resp = self.get_balances_self(**req)
        self.check_response_ok(resp)
        self.assertEquals(1, len(resp['balances']))

        balance = resp['balances'][0]
        self.assertEquals(balance_id, balance['id'])
        self.assertEquals(sess.user_id, balance['user_id'])
        self.assertEquals(True, balance['is_active'])
        self.assertEquals('0.00', balance['overdraft_limit'])
        self.assertEquals('0.00', balance['locked_amount'])
        self.assertEquals('0.00', balance['real_amount'])
        self.assertEquals('0.00', balance['virtual_amount'])
        self.assertEquals('RUB', balance['currency_code'])

        # adding second balance
        req = {'session_id': sess.session_id, 'user_id': sess.user_id, 'currency_code': 'BYR'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        req = {'session_id': sess.session_id}
        resp = self.get_balances_self(**req)
        self.check_response_ok(resp)
        self.assertEquals(2, len(resp['balances']))

    def test_get_balances(self):
        sess = self.login_actor()
        self.set_used_currencies(sess, ['RUB', 'BYR'])

        # creating balances
        u_id_0, u_id_1 = 1, 2
        req = {'session_id': sess.session_id, 'user_id': u_id_0, 'currency_code': 'RUB'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        req = {'session_id': sess.session_id, 'user_id': u_id_1, 'currency_code': 'RUB'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        req = {'session_id': sess.session_id, 'user_id': u_id_1, 'currency_code': 'BYR'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)

        # testing getting balances
        req = {'session_id': sess.session_id, 'filter_params': {'users_ids': [u_id_0]},
            'paging_params': {}}
        resp = self.get_balances(**req)
        self.check_response_ok(resp)
        self.assertEquals(1, len(resp['balances']))

        req = {'session_id': sess.session_id, 'filter_params': {'currency_code': 'XXX'},
            'paging_params': {}}
        resp = self.get_balances(**req)
        self.check_response_ok(resp)
        self.assertEquals(0, len(resp['balances']))

        req = {'session_id': sess.session_id, 'filter_params': {'users_ids': [u_id_1],
            'currency_code': 'RUB'},
            'paging_params': {}}
        resp = self.get_balances(**req)
        self.check_response_ok(resp)
        self.assertEquals(1, len(resp['balances']))
        balance = resp['balances'][0]
        self.assertEquals('RUB', balance['currency_code'])


if __name__ == '__main__':
    unittest.main()