import datetime
import unittest

from common import TestCaseWithBalance

from helixbilling.logic.actions import handle_action
from helixbilling.logic.exceptions import DataIntegrityError, ActionNotAllowedError


class ReceiptTestCase(TestCaseWithBalance):
    def test_enroll_receipt_ok(self):
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'amount': (45, 88),
        }
        handle_action('enroll_receipt', data)
        balance = self._get_balance(data['client_id'])

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
            'client_id': 'inexistent',
            'amount': (1000000, 0),
        }
        self.assertRaises(DataIntegrityError, handle_action, 'enroll_receipt', data)

        self._make_balance_passive(self.balance)
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'amount': (45, 88),
        }
        self.assertRaises(ActionNotAllowedError, handle_action, 'enroll_receipt', data)


if __name__ == '__main__':
    unittest.main()