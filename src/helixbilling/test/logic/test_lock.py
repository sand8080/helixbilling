import unittest

from helixcore.error import RequestProcessingError
from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase


class BalanceLockTestCase(ActorLogicTestCase):
    def test_balance_not_found(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id, 'balance_id': 9999,
            'amount': '11.12'}
        self.assertRaises(RequestProcessingError, self.lock, **req)

    def test_lock(self):
        sess = self.login_actor()
        subj_user_id = 4242

        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])
        balance_id = self.create_balance(sess, subj_user_id, curr_code, '5', None)
        order_id = '444'

        # locking
        req = {'session_id': sess.session_id, 'balance_id': balance_id,
            'amount': '3.90', 'locking_order': ['real_amount', 'virtual_amount'],
            'info': {'order_type': 'domain_com_reg', 'order_id': 4563},
            'order_id': order_id}
        resp = self.lock(**req)
        self.check_response_ok(resp)

        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('1.10', balance_info['real_amount'])
        self.assertEquals('0.00', balance_info['virtual_amount'])
        self.assertEquals('3.90', balance_info['locked_amount'])

    def test_lock_with_overdraft(self):
        sess = self.login_actor()
        subj_user_id = 4242

        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])
        balance_id = self.create_balance(sess, subj_user_id, curr_code, '5', None, '10')
        order_id = 'order_pizza_55'

        # locking with overdraft
        req = {'session_id': sess.session_id, 'balance_id': balance_id,
            'amount': '5.90', 'locking_order': ['real_amount'],
            'info': {'order_type': 'domain_ru_reg', 'order_id': 4564},
            'order_id': order_id}
        resp = self.lock(**req)
        self.check_response_ok(resp)

        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('-0.90', balance_info['real_amount'])
        self.assertEquals('0.00', balance_info['virtual_amount'])
        self.assertEquals('5.90', balance_info['locked_amount'])

        # overdraft exhausted
        req = {'session_id': sess.session_id, 'balance_id': balance_id,
            'amount': '9.11', 'locking_order': ['real_amount'],
            'info': {'order_type': 'domain_tel_reg', 'order_id': 4565}}
        self.assertRaises(RequestProcessingError, self.lock, **req)

        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('-0.90', balance_info['real_amount'])
        self.assertEquals('0.00', balance_info['virtual_amount'])
        self.assertEquals('5.90', balance_info['locked_amount'])

    def test_disabled_balance_failure(self):
        sess = self.login_actor()
        subj_user_id = 4242

        # creating balance
        self.set_used_currencies(sess, ['RUB'])
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'RUB', 'is_active': False}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']

        req = {'session_id': sess.session_id, 'balance_id': balance_id,
            'amount': '11.12', 'locking_order': ['real_amount'],
            'order_id': '1'}
        self.assertRaises(RequestProcessingError, self.lock, **req)

    def test_locking_order(self):
        sess = self.login_actor()
        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])

        # real, virtual
        subj_user_id = 11
        balance_id = self.create_balance(sess, subj_user_id, curr_code,
            '1', '2')
        req = {'session_id': sess.session_id, 'balance_id': balance_id,
            'amount': '2', 'locking_order': ['real_amount', 'virtual_amount'],
            'order_id': '1'}
        resp = self.lock(**req)
        self.check_response_ok(resp)
        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('0.00', balance_info['real_amount'])
        self.assertEquals('1.00', balance_info['virtual_amount'])
        self.assertEquals('2.00', balance_info['locked_amount'])

        # virtual, real
        subj_user_id = 12
        balance_id = self.create_balance(sess, subj_user_id, curr_code,
            '1', '2')
        req = {'session_id': sess.session_id, 'balance_id': balance_id,
            'amount': '2.60', 'locking_order': ['virtual_amount', 'real_amount'],
            'order_id': '1'}
        resp = self.lock(**req)
        self.check_response_ok(resp)
        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('0.40', balance_info['real_amount'])
        self.assertEquals('0.00', balance_info['virtual_amount'])
        self.assertEquals('2.60', balance_info['locked_amount'])

        # real
        subj_user_id = 13
        balance_id = self.create_balance(sess, subj_user_id, curr_code,
            '1', '2')
        req = {'session_id': sess.session_id, 'balance_id': balance_id,
            'amount': '0.60', 'locking_order': ['real_amount'],
            'order_id': '1'}
        resp = self.lock(**req)
        self.check_response_ok(resp)
        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('0.40', balance_info['real_amount'])
        self.assertEquals('2.00', balance_info['virtual_amount'])
        self.assertEquals('0.60', balance_info['locked_amount'])
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': curr_code, 'amount': '0.41',
            'order_id': '1'}
        self.assertRaises(RequestProcessingError, self.lock, **req)

        # virtual
        subj_user_id = 14
        balance_id = self.create_balance(sess, subj_user_id, curr_code,
            '1', '2')
        req = {'session_id': sess.session_id, 'balance_id': balance_id,
            'amount': '1.70', 'locking_order': ['virtual_amount'],
            'order_id': '1'}
        resp = self.lock(**req)
        self.check_response_ok(resp)
        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('1.00', balance_info['real_amount'])
        self.assertEquals('0.30', balance_info['virtual_amount'])
        self.assertEquals('1.70', balance_info['locked_amount'])
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': curr_code, 'amount': '0.31',
            'order_id': '1'}
        self.assertRaises(RequestProcessingError, self.lock, **req)

    def test_get_locks(self):
        sess = self.login_actor()
        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])

        # creating balance
        subj_user_id = 11
        balance_id = self.create_balance(sess, subj_user_id, curr_code, '10', '20')

        locks = ['1', '2', '3']
        for l in locks:
            req = {'session_id': sess.session_id, 'balance_id': balance_id,
                'amount': l, 'locking_order': ['real_amount', 'virtual_amount'],
                'order_id': 'order_%s' % l}
            resp = self.lock(**req)
            self.check_response_ok(resp)

        req = {'session_id': sess.session_id, 'filter_params': {'balance_id': balance_id},
            'paging_params': {}}
        resp = self.get_locks(**req)
        self.check_response_ok(resp)
        self.assertEquals(len(locks), len(resp['locks']))


if __name__ == '__main__':
    unittest.main()