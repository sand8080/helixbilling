import unittest

from helixbilling.test.logic.actor_logic_test import ActorLogicTestCase
from helixbilling.test.logic import access_granted #@UnusedImport


class ViewCurrencyTestCase(ActorLogicTestCase):
    def test_view_currencies(self):
        sess = self.login_actor()
        req = {'session_id': sess.session_id}
        resp = self.get_currencies(**req)
        self.check_response_ok(resp)


if __name__ == '__main__':
    unittest.main()