import unittest

from helixcore.error import RequestProcessingError

from helixbilling.test.logic.logic_test import LogicTestCase
from helixbilling.test.logic import access_granted #@UnusedImport


class LoginTestCase(LogicTestCase):
    env_name = 'env_0'
    su_login = 'l'
    su_password = 'p'

    def setUp(self):
        super(LoginTestCase, self).setUp()

    def test_login_super_user(self):
        req = {'environment_name': self.env_name,
            'login': self.su_login, 'password': self.su_password}
        resp = self.login(**req)
        self.check_response_ok(resp)
#        self.get_session(resp['session_id'])

#    def test_login_failed(self):
#        # Wrong environment
#        self.assertRaises(RequestProcessingError,
#            self.login, environment_name='_%s_' % self.env_name,
#            login=self.su_login, password=self.su_password)
#        # Wrong login
#        self.assertRaises(RequestProcessingError,
#            self.login, environment_name=self.env_name,
#            login='_%s_' % self.su_login, password=self.su_password)
#        # Wrong password
#        self.assertRaises(RequestProcessingError,
#            self.login, environment_name=self.env_name,
#            login=self.su_login, password='_%s_' % self.su_password)
#        # User is inactive
#        env = self.get_environment_by_name(self.env_name)
#        user = self.get_subj_user(env.id, self.su_login, self.su_password)
#        self.inactivate_user(user)
#        self.assertRaises(RequestProcessingError,
#            self.login, environment_name=self.env_name,
#            login=self.su_login, password=self.su_password)


if __name__ == '__main__':
    unittest.main()