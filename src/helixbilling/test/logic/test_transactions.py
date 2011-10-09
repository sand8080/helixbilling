import unittest

from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase


class TransactionsTestCase(ActorLogicTestCase):
    def test_get_transactions(self):
        sess = self.login_actor()
        subj_user_id = 4242

        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])
        balance_id = self.create_balance(sess, subj_user_id, curr_code, '10', '5', '3')

        req = {'session_id': sess.session_id, 'filter_params': {'user_id': subj_user_id,
            'type': 'lock'}, 'paging_params': {}}
        resp = self.get_transactions(**req)
        self.check_response_ok(resp)

        len_before = len(resp['transactions'])

        locking_order = ['real_amount', 'virtual_amount']
        lock_id_0 = self.make_lock(sess, balance_id, '9', locking_order)
        lock_id_1 = self.make_lock(sess, balance_id, '3', locking_order)
        lock_id_2 = self.make_lock(sess, balance_id, '4', locking_order)
        lock_ids = (lock_id_0, lock_id_1, lock_id_2)

        req = {'session_id': sess.session_id, 'filter_params': {'user_id': subj_user_id,
            'type': 'lock'},
            'paging_params': {}, 'ordering_params': ['-id']}
        resp = self.get_transactions(**req)
        self.check_response_ok(resp)
        self.assertEquals(len_before + len(lock_ids), len(resp['transactions']))
        for d_trn in resp['transactions']:
            self.assertEquals('lock', d_trn['type'])

    def test_get_transactions_self(self):
        sess = self.login_actor()

        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])
        balance_id = self.create_balance(sess, sess.user_id, curr_code, '10', '5', '3')

        req = {'session_id': sess.session_id, 'filter_params': {'type': 'lock'},
            'paging_params': {}}
        resp = self.get_transactions_self(**req)
        self.check_response_ok(resp)

        len_before = len(resp['transactions'])

        locking_order = ['real_amount', 'virtual_amount']
        lock_id_0 = self.make_lock(sess, balance_id, '9', locking_order)
        lock_id_1 = self.make_lock(sess, balance_id, '3', locking_order)
        lock_id_2 = self.make_lock(sess, balance_id, '4', locking_order)
        lock_ids = (lock_id_0, lock_id_1, lock_id_2)

        req = {'session_id': sess.session_id, 'filter_params': {'type': 'lock'},
            'paging_params': {}, 'ordering_params': ['-id']}
        resp = self.get_transactions_self(**req)
        self.check_response_ok(resp)
        self.assertEquals(len_before + len(lock_ids), len(resp['transactions']))
        for d_trn in resp['transactions']:
            self.assertEquals('lock', d_trn['type'])

    def test_get_transactions_self_isolated(self):
        sess = self.login_actor()

        curr_code = 'RUB'
        self.set_used_currencies(sess, [curr_code])
        u_id = sess.user_id + 1
        balance_id = self.create_balance(sess, sess.user_id, curr_code, '10', '5', '3')
        balance_u_id = self.create_balance(sess, u_id, curr_code, '11', '7')

        locking_order = ['real_amount', 'virtual_amount']
        self.make_lock(sess, balance_id, '9', locking_order)
        self.make_lock(sess, balance_u_id, '3', locking_order)

        # getting own transactions
        req = {'session_id': sess.session_id, 'filter_params': {'type': 'lock',
            'balance_id': balance_id}, 'paging_params': {}}
        resp = self.get_transactions_self(**req)
        self.check_response_ok(resp)
        self.assertEquals(1, len(resp['transactions']))

        # getting all alien transactions
        req = {'session_id': sess.session_id, 'filter_params': {'type': 'lock',
            'balance_id': balance_u_id}, 'paging_params': {}}
        resp = self.get_transactions(**req)
        self.check_response_ok(resp)
        self.assertEquals(1, len(resp['transactions']))

        # checking alien transactions not available
        req = {'session_id': sess.session_id, 'filter_params': {
            'balance_id': balance_u_id}, 'paging_params': {}}
        resp = self.get_transactions_self(**req)
        self.check_response_ok(resp)
        self.assertEquals(0, len(resp['transactions']))


if __name__ == '__main__':
    unittest.main()
