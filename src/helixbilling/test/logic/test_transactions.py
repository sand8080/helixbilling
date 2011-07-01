# coding=utf-8
import unittest

from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixbilling.test.logic import access_granted #@UnusedImport


class TransactionsTestCase(ActorLogicTestCase):
    def test_get_transactions(self):
        sess = self.login_actor()
        subj_user_id = 4242

        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])
        balance_id = self.create_balance(sess, subj_user_id, curr_code, None,
            '10', '5', '3')

        req = {'session_id': sess.session_id, 'filter_params': {'user_id': subj_user_id},
            'paging_params': {}}
        resp = self.get_transactions(**req)
        self.check_response_ok(resp)

        len_before = len(resp['transactions'])

        lock_id_0 = self.make_lock(sess, balance_id, '9')
        lock_id_1 = self.make_lock(sess, balance_id, '3')
        lock_id_2 = self.make_lock(sess, balance_id, '4')

        req = {'session_id': sess.session_id, 'filter_params': {'user_id': subj_user_id},
            'paging_params': {}}
        req = {'session_id': sess.session_id, 'filter_params': {'balance_id': balance_id},
            'paging_params': {}}
        resp = self.get_transactions(**req)
        self.check_response_ok(resp)
        print '###', resp

        self.assertEquals(len_before + 3, len(resp['transactions']))
        for d_trn in resp['transactions']:
            self.assertEquals('lock', d_trn['type'])


if __name__ == '__main__':
    unittest.main()
