import datetime
import unittest

from common import TestCaseWithBalance

from helixcore.db.wrapper import EmptyResultSetError
from helixcore.server.exceptions import ActionNotAllowedError

from helixbilling.logic.actions import handle_action


class EnrollReceiptTestCase(TestCaseWithBalance):
    def test_enroll_receipt_ok(self):
        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': self.balance.client_id,
            'amount': (45, 88),
        }
        handle_action('enroll_receipt', data)
        balance = self._get_balance(data['client_id'])
        manager = self.get_billing_manager_by_login(self.test_billing_manager_login)
        self.assertEqual(manager.id, balance.billing_manager_id)

        self.assertTrue(balance.id > 0)
        self.assertEquals(balance.client_id, data['client_id'])
        self.assertTrue(isinstance(balance.created_date, datetime.datetime))
        self.assertEquals(balance.available_real_amount, 4588)
        self.assertEquals(balance.locked_amount, 0)

        receipt = self._get_receipts(self.balance.client_id)[0] #IGNORE:E1101
        self.assertEquals(receipt.client_id, data['client_id'])
        self.assertEquals(receipt.amount, 4588)

    def test_enroll_receipt_no_balance(self):
        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': 'inexistent',
            'amount': (1000000, 0),
        }
        self.assertRaises(EmptyResultSetError, handle_action, 'enroll_receipt', data)

    def test_enroll_to_inactive_balance(self):
        self._make_balance_passive(self.balance)
        data = {
            'login': self.test_billing_manager_login,
            'password': self.test_billing_manager_password,
            'client_id': self.balance.client_id,
            'amount': (45, 88),
        }
        self.assertRaises(ActionNotAllowedError, handle_action, 'enroll_receipt', data)


if __name__ == '__main__':
    unittest.main()