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

        self.set_used_currencies(sess, ['RUB'])

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

    def test_get_balance_self(self):
        sess = self.login_actor()

        self.set_used_currencies(sess, ['RUB', 'BYR'])

        req = {'session_id': sess.session_id}
        resp = self.get_balance_self(**req)
        self.check_response_ok(resp)
        self.assertEquals([], resp['balances'])
        self.assertEquals(0, resp['total'])

        # adding first balance
        req = {'session_id': sess.session_id, 'user_id': sess.user_id, 'currency_code': 'RUB'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        req = {'session_id': sess.session_id}
        resp = self.get_balance_self(**req)
        self.check_response_ok(resp)
        self.assertEquals(1, len(resp['balances']))

        balance = resp['balances'][0]
        self.assertEquals(balance_id, balance['id'])
        self.assertEquals(sess.user_id, balance['user_id'])
        self.assertEquals(True, balance['is_active'])
        self.assertEquals('0.00', balance['overdraft_limit'])
        self.assertEquals('0.00', balance['locked_amount'])
        self.assertEquals(None, balance['locking_order'])
        self.assertEquals('0.00', balance['available_real_amount'])
        self.assertEquals('0.00', balance['available_virtual_amount'])
        self.assertEquals('RUB', balance['currency_code'])

        # adding second balance
        req = {'session_id': sess.session_id, 'user_id': sess.user_id, 'currency_code': 'BYR'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        req = {'session_id': sess.session_id}
        resp = self.get_balance_self(**req)
        self.check_response_ok(resp)
        self.assertEquals(2, len(resp['balances']))

    def test_get_balances(self):
        sess = self.login_actor()
        self.set_used_currencies(sess, ['RUB', 'BYR'])

        # creating balances
        u_id_0, u_id_1 = 'u_id_0', 'u_id_1'
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
        req = {'session_id': sess.session_id, 'filter_params': {'users_ids': ['u_id_0']},
            'paging_params': {}}
        resp = self.get_balances(**req)
        self.check_response_ok(resp)
        self.assertEquals(1, len(resp['balances']))

        req = {'session_id': sess.session_id, 'filter_params': {'currency_code': 'XXX'},
            'paging_params': {}}
        resp = self.get_balances(**req)
        self.check_response_ok(resp)
        self.assertEquals(0, len(resp['balances']))

        req = {'session_id': sess.session_id, 'filter_params': {'users_ids': ['u_id_1'],
            'currency_code': 'RUB'},
            'paging_params': {}}
        resp = self.get_balances(**req)
        self.check_response_ok(resp)
        self.assertEquals(1, len(resp['balances']))
        balance = resp['balances'][0]
        self.assertEquals('RUB', balance['currency_code'])


if __name__ == '__main__':
    unittest.main()