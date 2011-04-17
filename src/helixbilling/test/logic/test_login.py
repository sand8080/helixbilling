import unittest

from helixcore import error_code

from helixbilling.test.logic.logic_test import LogicTestCase


class LoginTestCase(LogicTestCase):
    def test_login(self):
        from helixbilling.test.logic import access_granted
        req = {'environment_name': 'n', 'login': 'l', 'password': 'p'}
        resp = self.login(**req)
        self.check_response_ok(resp)
        self.assertEquals(access_granted.GRANTED_SESSION_ID, resp['session_id'])
        self.assertEquals(access_granted.GRANTED_USER_ID, resp['user_id'])
        self.assertEquals(access_granted.GRANTED_ENV_ID, resp['environment_id'])

    def test_login_failed(self):
        from helixbilling.test.logic import access_denied #@UnusedImport
        req = {'environment_name': 'n', 'login': 'l', 'password': 'p'}
        resp = self.login(**req)
        self.assertEquals('error', resp['status'])
        self.assertEquals(error_code.HELIX_AUTH_ERROR, resp['code'])


if __name__ == '__main__':
    unittest.main()