import helixbilling.test.test_environment #IGNORE:W0611 @UnusedImport


from helixcore.install import install


from helixbilling.conf.db import get_connection, transaction
from helixbilling.conf.settings import patch_table_name
from helixbilling.test.test_environment import patches_path
from helixbilling.logic.actions import handle_action
from helixbilling.logic import selector
from root_test import RootTestCase


class DbBasedTestCase(RootTestCase):
    def setUp(self):
        install.execute('reinit', get_connection, patch_table_name, patches_path)


class ServiceTestCase(DbBasedTestCase):
    test_login = 'test_billing_manager'
    test_password = 'qazwsx'

    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.add_billing_manager(self.test_login, self.test_password)

    def add_billing_manager(self, login, password):
        handle_action('add_billing_manager', {'login': login, 'password': password})
        man = self.get_billing_manager_by_login(login)
        auth_man = self.get_auth_billing_manager(login, password)
        self.assertEqual(login, man.login)
        self.assertEqual(man.id, auth_man.id)
        self.assertEqual(man.login, auth_man.login)
        self.assertEqual(man.password, auth_man.password)

    @transaction()
    def get_billing_manager_by_login(self, login, curs=None):
        return selector.get_billing_manager_by_login(curs, login)

    @transaction()
    def get_auth_billing_manager(self, login, password, curs=None):
        return selector.get_auth_billing_manager(curs, login, password)

    @transaction()
    def get_currencies(self, curs=None):
        return selector.get_currencies(curs)
