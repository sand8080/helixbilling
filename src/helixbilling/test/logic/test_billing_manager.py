import unittest

from helixcore.server.exceptions import DataIntegrityError, AuthError
from helixcore.db.wrapper import EmptyResultSetError

from helixbilling.test.db_based_test import ServiceTestCase
from helixbilling.logic.actions import handle_action


class BillingManagerTestCase(ServiceTestCase):
    def test_add_billing_manager(self):
        self.add_billing_manager('john', 'milk and soda')

    def test_add_billing_manager_invalid(self):
        self.add_billing_manager('john', 'milk and soda')
        self.assertRaises(DataIntegrityError, self.add_billing_manager, 'john', 'milk and cola')

    def test_modify_billing_manager(self):
        login_old = 'john'
        password_old = 'milk and soda'
        self.add_billing_manager(login_old, password_old)
        m_old = self.get_billing_manager_by_login(login_old)

        login_new = 'silver'
        data = {
            'login': login_old,
            'password': password_old,
            'new_login': login_new
        }
        handle_action('modify_billing_manager', data)
        self.assertRaises(EmptyResultSetError, self.get_billing_manager_by_login, m_old.login)
        m_new_0 = self.get_billing_manager_by_login(login_new)
        self.assertEqual(m_old.id, m_new_0.id)
        self.assertEqual(login_new, m_new_0.login)

        password_new = 'yahoo'
        data = {
            'login': login_new,
            'password': password_old,
            'new_login': m_old.login,
            'new_password': password_new
        }
        handle_action('modify_billing_manager', data)
        self.assertRaises(EmptyResultSetError, self.get_billing_manager_by_login, m_new_0.login)
        m_new_1 = self.get_billing_manager_by_login(m_old.login)
        self.assertEqual(m_old.id, m_new_1.id)
        self.assertEqual(m_old.login, m_new_1.login)
        self.assertNotEqual(m_new_0.password, m_new_1.password)

        data = {
            'login': m_new_1.login,
            'password': password_new
        }
        handle_action('modify_billing_manager', data)
        m_new_2 = self.get_billing_manager_by_login(m_new_1.login)
        self.assertEqual(m_new_1.id, m_new_2.id)
        self.assertEqual(m_new_1.login, m_new_2.login)
        self.assertEqual(m_new_1.password, m_new_2.password)

    def test_access_denied(self):
        login_old = 'john'
        password = 'milk and soda'
        self.add_billing_manager(login_old, password)
        data = {'login': login_old, 'password': password + ' ', 'new_login': 'silver'}
        self.assertRaises(AuthError, handle_action, 'modify_billing_manager', data)

    def test_delete_billing_manager(self):
        login = 'zimorodok'
        self.add_billing_manager(login, '')
        handle_action('delete_billing_manager', {'login': login, 'password': ''})
        self.assertRaises(EmptyResultSetError, self.get_billing_manager_by_login, login)


if __name__ == '__main__':
    unittest.main()