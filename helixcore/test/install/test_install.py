import unittest
import os

import conf.settings
conf.settings.DSN = 'dbname=sandbox host=localhost user=sandbox password=qazwsx'

from install.install import in_diapasone, filter_patches, filter_backward, filter_forward
from install.install import get_patches, apply, revert, get_last_applied, patch_table_name

class InstallTestCase(unittest.TestCase):

    def test_in_diapasone(self):
        self.assertTrue(in_diapasone('1', '5', '4-6-7'))
        self.assertTrue(in_diapasone('1', None, '5'))
        self.assertTrue(in_diapasone(None, '7', '5'))
        self.assertTrue(in_diapasone('4', '7', '5'))
        self.assertFalse(in_diapasone('4', '7', '2-3'))
        self.assertFalse(in_diapasone('4', None, '2-3'))
        self.assertFalse(in_diapasone(None, '2', '2-3'))

    def test_filter_patches(self):
        patches = ['1', '2-2', '37', '4', '4-1', '4-1-0', '35', '35-0']
        self.assertEqual(
            ['2-2', '4', '4-1', '4-1-0', '35', '35-0', '37'],
            filter_patches('2', '7-9-1', patches, reverse=False)
        )
        self.assertEqual(
            ['1', '2-2', '4', '4-1', '4-1-0', '35', '35-0', '37'],
            filter_patches(None, '7-9-1', patches, reverse=False)
        )
        self.assertEqual(
            ['37', '35-0', '35', '4-1-0', '4-1', '4', '2-2', '1'],
            filter_patches(None, '7-9-1', patches, reverse=True)
        )

    def test_filter_backward(self):
        patches = ['1', '2-2', '3', '7-9-9', '6']
        self.assertEqual(
            ['7-9-9', '6', '3', '2-2', '1'],
            filter_backward(None, None, patches)
        )

    def test_get_patches(self):
        patches = get_patches(os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            'patches_no_action'
        ))
        self.assertEqual(
            ['1', '1-1', '4', '37'],
            filter_forward(None, None, patches)
        )

    def test_apply_calls(self):
        patches_path = os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            'patches_no_action'
        )
        apply(patches_path, None)

    def test_revert_calls(self):
        patches_path = os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            'patches_no_action'
        )
        revert(patches_path, None)

from install.install import is_table_exist, patch_table_name
from db.wrapper import get_connection, transaction, fetchall_dicts
from db.query_builder import select

class DbPatchesTestCase(unittest.TestCase):

    patches_path = os.path.join(
        os.path.realpath(os.path.dirname(__file__)),
        'patches_db'
    )

    @transaction()
    def get_patches_list(self, curs=None):
        curs.execute(*select(patch_table_name, order_by=['-id']))
        return fetchall_dicts(curs)

    def test_patches(self):
        try:
            apply(self.patches_path, None)
            self.assertEqual(len(get_patches(self.patches_path)), len(self.get_patches_list()))
        finally:
            revert(self.patches_path, None)

    @transaction()
    def test_table_not_exist(self, curs=None):
        self.assertFalse(is_table_exist('fake_table', curs))

    @transaction()
    def test_table_exist(self, curs=None):
        try:
            curs.execute('CREATE TABLE fake_test_table (id int)')
            self.assertTrue(is_table_exist('fake_test_table', curs))
        finally:
            curs.execute('DROP TABLE fake_test_table')

    def test_get_last_applied(self):
        try:
            apply(self.patches_path, None)
            last_applied = get_last_applied(patch_table_name)
            self.assertEqual('2', last_applied['name'])
        finally:
            revert(self.patches_path, None)

if __name__ == '__main__':
    unittest.main()