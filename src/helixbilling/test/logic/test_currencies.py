import unittest

from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixbilling.test.logic import access_granted #@UnusedImport


class CurrenciesTestCase(ActorLogicTestCase):
    def test_get_currencies(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id}
        resp = self.get_currencies(**req)
        self.check_response_ok(resp)

    def test_get_used_currencies(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id}
        resp = self.get_used_currencies(**req)
        self.check_response_ok(resp)
        self.assertEquals([], resp['currencies'])

    def test_modify_used_currencies(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id}
        resp = self.modify_used_currencies(**req)
        self.check_response_ok(resp)
        # checking used currencies not added
        req = {'session_id': sess.session_id}
        resp = self.get_used_currencies(**req)
        self.check_response_ok(resp)
        self.assertEquals(0, len(resp['currencies']))

        req = {'session_id': sess.session_id, 'new_currencies_ids': []}
        resp = self.modify_used_currencies(**req)
        self.check_response_ok(resp)
        # checking used currencies added
        req = {'session_id': sess.session_id}
        resp = self.get_used_currencies(**req)
        self.check_response_ok(resp)
        self.assertEquals(0, len(resp['currencies']))
        self.assertEquals([], resp['currencies'])

        req = {'session_id': sess.session_id, 'new_currencies_ids': [32, 10000]}
        resp = self.modify_used_currencies(**req)
        self.check_response_ok(resp)
        # checking in used currencies only valid ids
        req = {'session_id': sess.session_id}
        resp = self.get_used_currencies(**req)
        self.check_response_ok(resp)
        self.assertEquals(1, len(resp['currencies']))
        curr_data = resp['currencies'][0]
        self.assertEquals(32, curr_data['id'])


if __name__ == '__main__':
    unittest.main()
