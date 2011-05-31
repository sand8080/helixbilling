import unittest


from helixcore.error import RequestProcessingError
from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixbilling.test.logic import access_granted #@UnusedImport


class BonusTestCase(ActorLogicTestCase):
    def test_add_bonus(self):
        sess = self.login_actor()
        subj_user_id = 4242

        # checking currency not found
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'XXX', 'amount': '11.12'}
        self.assertRaises(RequestProcessingError, self.add_bonus, **req)

        # checking balance not found
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'RUB', 'amount': '11.12'}
        self.assertRaises(RequestProcessingError, self.add_bonus, **req)

        # creating balance
        self.set_used_currencies(sess, ['RUB'])
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'RUB'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        # adding bonus
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'RUB', 'amount': '11.12'}
        resp = self.add_bonus(**req)
        self.check_response_ok(resp)

        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('0.00', balance_info['real_amount'])
        self.assertEquals('11.12', balance_info['virtual_amount'])
        self.assertEquals('0.00', balance_info['locked_amount'])

        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'RUB', 'amount': '08.909'}
        resp = self.add_bonus(**req)
        self.check_response_ok(resp)

        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('0.00', balance_info['real_amount'])
        self.assertEquals('20.02', balance_info['virtual_amount'])
        self.assertEquals('0.00', balance_info['locked_amount'])

        # checking balance disabled
        req = {'session_id': sess.session_id, 'ids': [balance_id],
            'new_is_active': False}
        resp = self.modify_balances(**req)

        self.check_response_ok(resp)
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'RUB', 'amount': '11.12'}
        self.assertRaises(RequestProcessingError, self.add_bonus, **req)


if __name__ == '__main__':
    unittest.main()