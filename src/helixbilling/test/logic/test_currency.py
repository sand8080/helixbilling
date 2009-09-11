# -*- coding: utf-8 -*-
import unittest

from common import LogicTestCase

from helixcore.db.wrapper import EmptyResultSetError
from helixcore.server.exceptions import DataIntegrityError

from helixbilling.logic.actions import handle_action


class CurrencyTestCase(LogicTestCase):

    def __init__(self, methodName):
        LogicTestCase.__init__(self, methodName)
        self.typical_data = {
            'name': 'USD',
            'designation': '$',
        }

    def test_add_currency_ok(self):
        handle_action('add_currency', self.typical_data)
        curr = self._get_currency(self.typical_data['name'])
        self.assertEquals(curr.name, self.typical_data['name'])
        self.assertEquals(curr.designation, self.typical_data['designation'])
        self.assertTrue(curr.id > 0)

    def test_add_currency_duplicate(self):
        handle_action('add_currency', self.typical_data)
        self.assertRaises(DataIntegrityError, handle_action, 'add_currency', self.typical_data)

    def test_modify_currency_ok(self):
        changed_designation = 'долл.'

        handle_action('add_currency', self.typical_data)

        data = {}
        data.update(self.typical_data)
        data['designation'] = changed_designation
        handle_action('modify_currency', data)

        curr = self._get_currency(data['name'])
        self.assertEquals(curr.name, data['name'])
        self.assertEquals(curr.designation, changed_designation)
        self.assertTrue(curr.id > 0)

    def test_delete_currency_ok(self):
        handle_action('add_currency', self.typical_data)

        handle_action('delete_currency', {'name': self.typical_data['name']})
        self.assertRaises(EmptyResultSetError, self._get_currency, self.typical_data['name'])

if __name__ == '__main__':
    unittest.main()