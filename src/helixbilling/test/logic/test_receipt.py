import unittest


from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixcore.error import RequestProcessingError
from helixbilling.test.logic import access_granted #@UnusedImport


class ReceiptTestCase(ActorLogicTestCase):
    def test_add_receipt(self):
        sess = self.login_actor()
        subj_user_id = 4242

        # checking currency not found
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'XXX', 'amount': '11.12'}
        self.assertRaises(RequestProcessingError, self.add_receipt, **req)

        # checking balance not found
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'RUB', 'amount': '11.12'}
        self.assertRaises(RequestProcessingError, self.add_receipt, **req)

        # creating balance
        self.set_used_currencies(sess, ['RUB'])
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'RUB'}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        # adding receipt
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'RUB', 'amount': '11.12'}
        resp = self.add_receipt(**req)
        self.check_response_ok(resp)

        req = {'session_id': sess.session_id, 'filter_params': {'id': balance_id},
           'paging_params': {}}
        resp = self.get_balances(**req)
        self.check_response_ok(resp)
        balance_info = resp['balances'][0]
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('11.12', balance_info['real_amount'])
        self.assertEquals('0.00', balance_info['virtual_amount'])
        self.assertEquals('0.00', balance_info['locked_amount'])

        # checking balance disabled
        req = {'session_id': sess.session_id, 'ids': [balance_id],
            'new_is_active': False}
        resp = self.modify_balances(**req)

        self.check_response_ok(resp)
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'RUB', 'amount': '11.12'}
        self.assertRaises(RequestProcessingError, self.add_receipt, **req)


if __name__ == '__main__':
    unittest.main()