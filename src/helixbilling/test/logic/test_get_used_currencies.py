import unittest

from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixbilling.test.logic import access_granted #@UnusedImport


class GetUsedCurrenciesTestCase(ActorLogicTestCase):
    def test_get_used_currencies(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id}
        resp = self.get_used_currencies(**req)
        self.check_response_ok(resp)
        self.assertEquals([], resp['currencies'])


if __name__ == '__main__':
    unittest.main()