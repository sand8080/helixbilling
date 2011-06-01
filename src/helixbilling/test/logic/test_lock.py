import unittest

from helixcore.error import RequestProcessingError
from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixbilling.test.logic import access_granted #@UnusedImport


class BalanceLockTestCase(ActorLogicTestCase):
    def _create_balance(self, sess, user_id, curr_code, locking_order,
        real_amount, virtual_amount, overdraft_limit='0'):
        req = {'session_id': sess.session_id, 'user_id': user_id,
            'currency_code': curr_code, 'locking_order': locking_order,
            'overdraft_limit': overdraft_limit}
        resp = self.add_balance(**req)
        self.check_response_ok(resp)
        balance_id = resp['id']
        # adding receipt
        if real_amount:
            req = {'session_id': sess.session_id, 'user_id': user_id,
                'currency_code': curr_code, 'amount': real_amount,
                'info': {'payment_system': 'YandexMoney'}}
            resp = self.add_receipt(**req)
            self.check_response_ok(resp)
        # adding bonus
        if virtual_amount:
            req = {'session_id': sess.session_id, 'user_id': user_id,
                'currency_code': curr_code, 'amount': virtual_amount,
                'info': {'payment_system': 'BonusSystem'}}
            resp = self.add_bonus(**req)
            self.check_response_ok(resp)
        return balance_id

    def test_lock(self):
        sess = self.login_actor()
        subj_user_id = 4242

        # checking currency not found
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'XXX', 'amount': '11.12'}
        self.assertRaises(RequestProcessingError, self.lock, **req)

        # checking balance not found
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': 'RUB', 'amount': '11.12'}
        self.assertRaises(RequestProcessingError, self.lock, **req)

        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])
        balance_id = self._create_balance(sess, subj_user_id, curr_code, None, '5', None)

        # locking
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': curr_code, 'amount': '3.90',
            'info': {'order_type': 'domain_com_reg', 'order_id': 4563}}
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
        balance_id = self._create_balance(sess, subj_user_id, curr_code, None, '5', None, '10')

        # locking with overdraft
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': curr_code, 'amount': '5.90',
            'info': {'order_type': 'domain_ru_reg', 'order_id': 4564}}
        resp = self.lock(**req)
        self.check_response_ok(resp)

        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('-0.90', balance_info['real_amount'])
        self.assertEquals('0.00', balance_info['virtual_amount'])
        self.assertEquals('5.90', balance_info['locked_amount'])

        # overdraft exhausted
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': curr_code, 'amount': '9.11',
            'info': {'order_type': 'domain_tel_reg', 'order_id': 4565}}
        self.assertRaises(RequestProcessingError, self.lock, **req)

        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('-0.90', balance_info['real_amount'])
        self.assertEquals('0.00', balance_info['virtual_amount'])
        self.assertEquals('5.90', balance_info['locked_amount'])

    def test_disabled_balance_lock_failed(self):
        sess = self.login_actor()
        subj_user_id = 4242

        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])
        balance_id = self._create_balance(sess, subj_user_id, curr_code, None, '5', None)

        # disabling balance
        req = {'session_id': sess.session_id, 'ids': [balance_id], 'new_is_active': False}
        resp = self.modify_balances(**req)
        self.check_response_ok(resp)

        # checking locking failure
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': curr_code, 'amount': '3.90',
            'info': {'order_type': 'domain_com_reg', 'order_id': 4563}}
        self.assertRaises(RequestProcessingError, self.lock, **req)

    def test_locking_order(self):
        sess = self.login_actor()
        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])

        # real, virtual
        subj_user_id = 11
        balance_id = self._create_balance(sess, subj_user_id, curr_code,
            ['real_amount', 'virtual_amount'], '1', '2')
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': curr_code, 'amount': '2'}
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
        balance_id = self._create_balance(sess, subj_user_id, curr_code,
            ['virtual_amount', 'real_amount'], '1', '2')
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': curr_code, 'amount': '2.60'}
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
        balance_id = self._create_balance(sess, subj_user_id, curr_code,
            ['real_amount'], '1', '2')
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': curr_code, 'amount': '0.60'}
        resp = self.lock(**req)
        self.check_response_ok(resp)
        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('0.40', balance_info['real_amount'])
        self.assertEquals('2.00', balance_info['virtual_amount'])
        self.assertEquals('0.60', balance_info['locked_amount'])
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': curr_code, 'amount': '0.41'}
        self.assertRaises(RequestProcessingError, self.lock, **req)

        # virtual
        subj_user_id = 14
        balance_id = self._create_balance(sess, subj_user_id, curr_code,
            ['virtual_amount'], '1', '2')
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': curr_code, 'amount': '1.70'}
        resp = self.lock(**req)
        self.check_response_ok(resp)
        balance_info = self.get_balance(sess, balance_id)
        self.assertEquals(balance_id, balance_info['id'])
        self.assertEquals(subj_user_id, balance_info['user_id'])
        self.assertEquals('1.00', balance_info['real_amount'])
        self.assertEquals('0.30', balance_info['virtual_amount'])
        self.assertEquals('1.70', balance_info['locked_amount'])
        req = {'session_id': sess.session_id, 'user_id': subj_user_id,
            'currency_code': curr_code, 'amount': '0.31'}
        self.assertRaises(RequestProcessingError, self.lock, **req)

    def test_get_locks(self):
        sess = self.login_actor()
        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])

        # creating balance
        subj_user_id = 11
        balance_id = self._create_balance(sess, subj_user_id, curr_code,
            ['real_amount', 'virtual_amount'], '10', '20')

        locks = ['1', '2', '3']
        for l in locks:
            req = {'session_id': sess.session_id, 'user_id': subj_user_id,
                'currency_code': curr_code, 'amount': l}
            resp = self.lock(**req)
            self.check_response_ok(resp)

        req = {'session_id': sess.session_id, 'filter_params': {'balance_id': balance_id},
            'paging_params': {}}
        resp = self.get_locks(**req)
        self.check_response_ok(resp)
        self.assertEquals(len(locks), len(resp['locks']))


if __name__ == '__main__':
    unittest.main()