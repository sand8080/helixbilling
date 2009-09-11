import datetime
import unittest

from common import LogicTestCase

from helixcore.mapping.actions import insert
from helixcore.server.exceptions import DataIntegrityError, ActionNotAllowedError

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.domain.objects import Currency, Balance

class BonusTestCase(LogicTestCase):

    def setUp(self):
        LogicTestCase.setUp(self)
        self._fixture()

    @transaction()
    def _fixture(self, curs=None):
        self.currency = Currency(name='USD', designation='$') #IGNORE:W0201
        insert(curs, self.currency)

        balance = Balance(client_id='123', active=1, currency_id=self.currency.id) #IGNORE:E1101
        self.balance = balance #IGNORE:W0201
        insert(curs, self.balance)

    def test_enroll_bonus_ok(self):
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'amount': (45, 88),
        }
        handle_action('enroll_bonus', data)
        balance = self._get_balance(data['client_id'])

        self.assertTrue(balance.id > 0)
        self.assertEquals(balance.client_id, data['client_id'])
        self.assertTrue(isinstance(balance.created_date, datetime.datetime))
        self.assertEquals(balance.available_virtual_amount, 4588)
        self.assertEquals(balance.locked_amount, 0)

        bonus = self._get_bonuses(self.balance.client_id)[0] #IGNORE:E1101
        self.assertEquals(bonus.client_id, data['client_id'])
        self.assertEquals(bonus.amount, 4588)

    def test_enroll_bonus_no_balance(self):
        data = {
            'client_id': 'inexistent',
            'amount': (1000000, 0),
        }
        self.assertRaises(DataIntegrityError, handle_action, 'enroll_bonus', data)

    def test_enroll_bonus_not_active(self):
        self._make_balance_passive(self.balance)
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'amount': (45, 88),
        }
        self.assertRaises(ActionNotAllowedError, handle_action, 'enroll_bonus', data)

if __name__ == '__main__':
    unittest.main()