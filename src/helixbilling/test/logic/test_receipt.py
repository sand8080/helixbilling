import datetime
import unittest

import helixbilling.test.test_environment #IGNORE:W0611

from common import LogicTestCase

from helixcore.mapping.actions import insert

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.logic.exceptions import DataIntegrityError
from helixbilling.domain.objects import Currency, Balance

class ReceiptTestCase(LogicTestCase):

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
        self.assertEquals(balance.available_amount, 4588)
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

if __name__ == '__main__':
    unittest.main()