from helixcore.security import Session

from helixbilling.test.logic.logic_test import LogicTestCase
from helixbilling.test.logic.access_granted import (GRANTED_ENV_ID,
    GRANTED_USER_ID)


class ActorLogicTestCase(LogicTestCase):
    def login_actor(self):
        return Session('ACTOR_LOGIC_TEST_CASE', GRANTED_ENV_ID, GRANTED_USER_ID)

    def set_used_currencies(self, sess, currs_codes):
        req = {'session_id': sess.session_id, 'new_currencies_codes': currs_codes}
        resp = self.modify_used_currencies(**req)
        self.check_response_ok(resp)

    def get_balance(self, sess, balance_id):
        req = {'session_id': sess.session_id, 'filter_params': {'id': balance_id},
           'paging_params': {}}
        resp = self.get_balances(**req)
        self.check_response_ok(resp)
        self.assertEquals(1, len(resp['balances']))
        balance_info = resp['balances'][0]
        return balance_info

    def create_balance(self, sess, user_id, curr_code,
        real_amount, virtual_amount, overdraft_limit='0'):
        req = {'session_id': sess.session_id, 'user_id': user_id,
            'currency_code': curr_code, 'overdraft_limit': overdraft_limit}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']
        # adding receipt
        if real_amount:
            req = {'session_id': sess.session_id, 'balance_id': balance_id,
                'amount': real_amount, 'info': {'payment_system': 'YandexMoney'}}
            resp = self.add_receipt(**req)
            self.check_response_ok(resp)
        # adding bonus
        if virtual_amount:
            req = {'session_id': sess.session_id, 'balance_id': balance_id,
                'amount': virtual_amount, 'info': {'payment_system': 'BonusSystem'}}
            resp = self.add_bonus(**req)
            self.check_response_ok(resp)
        return balance_id

    def make_lock(self, sess, balance_id, amount, locking_order):
        req = {'session_id': sess.session_id, 'balance_id': balance_id,
            'amount': amount, 'locking_order': locking_order,
            'order_id': '%s_%s' % (balance_id, amount)}
        resp = self.lock(**req)
        self.check_response_ok(resp)
        return resp['lock_id']

