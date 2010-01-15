import datetime
import unittest

from common import TestCaseWithBalance
from helixcore.db.wrapper import EmptyResultSetError
from helixcore.server.exceptions import ActionNotAllowedError

from helixbilling.logic.actions import handle_action


class EnrollBonusTestCase(TestCaseWithBalance):
    def test_enroll_bonus_ok(self):
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': self.balance.client_id,
            'amount': (45, 88),
        }
        handle_action('enroll_bonus', data)
        balance = self._get_validated_balance(self.test_login, data['client_id'])

        self.assertTrue(balance.id > 0)
        self.assertEquals(balance.client_id, data['client_id'])
        self.assertTrue(isinstance(balance.created_date, datetime.datetime))
        self.assertEquals(balance.available_virtual_amount, 4588)
        self.assertEquals(balance.locked_amount, 0)

        bonus = self._get_bonuses(self.balance.client_id)[0]
        self.assertEquals(bonus.client_id, data['client_id'])
        self.assertEquals(bonus.amount, 4588)

    def test_enroll_bonus_no_balance(self):
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': 'inexistent',
            'amount': (1000000, 0),
        }
        self.assertRaises(EmptyResultSetError, handle_action, 'enroll_bonus', data)

    def test_enroll_bonus_not_active(self):
        self._make_balance_passive(self.balance)
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': self.balance.client_id,
            'amount': (45, 88),
        }
        self.assertRaises(ActionNotAllowedError, handle_action, 'enroll_bonus', data)


if __name__ == '__main__':
    unittest.main()