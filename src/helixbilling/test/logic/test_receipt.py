# -*- coding: utf-8 -*-
import datetime

from helixcore.mapping.actions import insert

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.domain.objects import Currency, Balance

from common import LogicTestCase

class ReceiptTestCase(LogicTestCase):
    
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
        
#    def test_enroll_receipt_ok(self):
#        data = {
#            'client_id': self.balance.client_id,
#            'amount': (45, 88),
#        }
#        handle_action('enroll_receipt', data)
#        balance = self._get_balance(data['client_id'])
#        
#        self.assertTrue(balance.id > 0)
#        self.assertEquals(balance.client_id, data['client_id'])
#        self.assertTrue(isinstance(balance.created_date, datetime.datetime))
#        self.assertEquals(balance.available_amount, 0)
#        self.assertEquals(balance.locked_amount, 0)
#        self.assertEquals(balance.overdraft_limit, 50050) #500.50
#        self.assertEquals(balance.currency_id, self._get_currency('USD').id)
