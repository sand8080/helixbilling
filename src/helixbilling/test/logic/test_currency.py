import unittest

from helixcore.error import RequestProcessingError

from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixbilling.test.logic import access_granted #@UnusedImport


class CurrencyTestCase(ActorLogicTestCase):
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

        req = {'session_id': sess.session_id, 'new_currencies_codes': []}
        resp = self.modify_used_currencies(**req)
        self.check_response_ok(resp)
        # checking used currencies added
        req = {'session_id': sess.session_id}
        resp = self.get_used_currencies(**req)
        self.check_response_ok(resp)
        self.assertEquals(0, len(resp['currencies']))
        self.assertEquals([], resp['currencies'])

        req = {'session_id': sess.session_id, 'new_currencies_codes': ['RUB', 'XXX']}
        self.assertRaises(RequestProcessingError, self.modify_used_currencies, **req)

        req = {'session_id': sess.session_id, 'new_currencies_codes': ['RUB', 'BYR']}
        resp = self.modify_used_currencies(**req)
        self.check_response_ok(resp)

        # checking in used currencies modified
        req = {'session_id': sess.session_id}
        resp = self.get_used_currencies(**req)
        self.check_response_ok(resp)
        self.assertEquals(2, len(resp['currencies']))


if __name__ == '__main__':
    unittest.main()
