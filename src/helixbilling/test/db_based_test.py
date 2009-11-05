import helixbilling.test.test_environment #IGNORE:W0611 @UnusedImport

from helixcore.install import install

from helixbilling.conf.db import get_connection
from helixbilling.conf.settings import patch_table_name
from helixbilling.test.test_environment import patches_path

from root_test import RootTestCase


class DbBasedTestCase(RootTestCase):
    def setUp(self):
        install.execute('reinit', get_connection, patch_table_name, patches_path)
