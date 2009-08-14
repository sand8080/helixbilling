# -*- coding: utf-8 -*-
import datetime, pytz
import unittest

import helixbilling.test.test_environment #IGNORE:W0611

from common import LogicTestCase

from helixcore.mapping.actions import insert

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.domain.objects import Currency, Balance, Receipt


class ListReceiptsTestCase(LogicTestCase):

    def setUp(self):
        LogicTestCase.setUp(self)
        self._fixture()

    @transaction()
    def _fixture(self, curs=None):
        self.currency = Currency(name='USD', designation='$') #IGNORE:W0201
        insert(curs, self.currency)

        balance = Balance(client_id=123, active=1, currency_id=self.currency.id) #IGNORE:E1101
        self.balance = balance #IGNORE:W0201
        insert(curs, self.balance)

    @transaction()
    def _make_receipt(self, client_id, created_date, amount, curs=None):
        receipt = Receipt(client_id=client_id, created_date=created_date, amount=amount) #IGNORE:E1101
        insert(curs, receipt)
        return receipt

    def _check_receipt(self, receipt_obj, sel_dict):
        self.assertEquals(receipt_obj.created_date, sel_dict['created_date'])
        self.assertEquals(receipt_obj.amount, sel_dict['amount'][0]*100 + sel_dict['amount'][1])

    def test_list_receipts_ok(self):
        start_date = datetime.datetime(2009, 4, 1, tzinfo=pytz.utc)
        end_date = datetime.datetime(2009, 4, 25, tzinfo=pytz.utc)

        self._make_receipt(899, datetime.datetime(2009, 1, 2, tzinfo=pytz.utc), 5099) #other client
        self._make_receipt(self.balance.client_id, datetime.datetime(2009, 2, 21, tzinfo=pytz.utc), 5000) #IGNORE:E1101 - too early
        r_low = self._make_receipt(self.balance.client_id, start_date, 6200) #IGNORE:E1101
        r_mid = self._make_receipt(self.balance.client_id, datetime.datetime(2009, 4, 22, 8, 33, 44, tzinfo=pytz.utc), 7060) #IGNORE:E1101
        r_hi = self._make_receipt(self.balance.client_id, datetime.datetime(2009, 4, 24, 23, 59, 59, tzinfo=pytz.utc), 7060) #IGNORE:E1101
        self._make_receipt(self.balance.client_id, end_date, 1080) #IGNORE:E1101 - too late

        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
        }
        output = handle_action('list_receipts', data)
        selected_receipts = output['receipts']

        self.assertEquals(len(selected_receipts), 3)
        self._check_receipt(r_low, selected_receipts[0])
        self._check_receipt(r_mid, selected_receipts[1])
        self._check_receipt(r_hi, selected_receipts[2])

    def test_list_receipts_none(self):
        start_date = datetime.datetime(2009, 4, 1, tzinfo=pytz.utc)
        end_date = datetime.datetime(2009, 4, 25, tzinfo=pytz.utc)

        self._make_receipt(899, datetime.datetime(2009, 1, 2, tzinfo=pytz.utc), 5099) #other client
        self._make_receipt(self.balance.client_id, datetime.datetime(2009, 2, 21, tzinfo=pytz.utc), 5000) #IGNORE:E1101 - too early
        self._make_receipt(self.balance.client_id, end_date, 1080) #IGNORE:E1101 - too late

        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
        }
        output = handle_action('list_receipts', data)
        selected_receipts = output['receipts']

        self.assertEquals(len(selected_receipts), 0)

if __name__ == '__main__':
    unittest.main()