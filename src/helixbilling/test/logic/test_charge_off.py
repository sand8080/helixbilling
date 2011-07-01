import unittest

from helixcore.error import RequestProcessingError
from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixbilling.test.logic import access_granted #@UnusedImport


class BalanceChargeOffTestCase(ActorLogicTestCase):
    def test_lock_not_found(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'balance_id': 9999,
            'lock_id': 8888}
        self.assertRaises(RequestProcessingError, self.unlock, **req)

    def test_balance_not_found(self):
        sess = self.login_actor()
        subj_user_id = 4242

        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])
        balance_id = self.create_balance(sess, subj_user_id, curr_code, None, '5', None)
        lock_id = self.make_lock(sess, balance_id, '3.90')

        req = {'session_id': sess.session_id, 'balance_id': 9999,
            'lock_id': lock_id}
        self.assertRaises(RequestProcessingError, self.unlock, **req)

    def test_charge_off(self):
        sess = self.login_actor()
        subj_user_id = 4242

        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])
        balance_id = self.create_balance(sess, subj_user_id, curr_code, None, '5', None)
        lock_id = self.make_lock(sess, balance_id, '3.90')

        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('1.10', balance_info['real_amount'])
        self.assertEquals('0.00', balance_info['virtual_amount'])
        self.assertEquals('3.90', balance_info['locked_amount'])

        # charge off
        req = {'session_id': sess.session_id, 'balance_id': balance_id,
            'lock_id': lock_id, 'info': {'order_type': 'domain_com_reg',
            'order_id': 4563}}
        resp = self.charge_off(**req)
        self.check_response_ok(resp)

        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('1.10', balance_info['real_amount'])
        self.assertEquals('0.00', balance_info['virtual_amount'])
        self.assertEquals('0.00', balance_info['locked_amount'])

        req = {'session_id': sess.session_id, 'filter_params': {'id': lock_id},
            'paging_params': {}}
        resp = self.get_locks(**req)
        self.check_response_ok(resp)
        self.assertEquals([], resp['locks'])


if __name__ == '__main__':
    unittest.main()