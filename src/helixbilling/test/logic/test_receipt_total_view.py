# -*- coding: utf-8 -*-
import unittest
import datetime

from common import LogicTestCase

from helixcore.mapping import actions
from helixcore.db.cond import Eq

from helixbilling.conf.db import transaction
#from helixbilling.logic.actions import handle_action
from helixbilling.domain.objects import Currency, Balance, ReceiptTotalView, Receipt, Bonus, ChargeOff


class BalanceTestCase(LogicTestCase):
    def setUp(self):
        super(BalanceTestCase, self).setUp()
        self._fixture()

    @transaction()
    def _fixture(self, curs=None):
        self.currency = Currency(name='USD', designation='$') #IGNORE:W0201
        actions.insert(curs, self.currency)
        self.currency = actions.reload(curs, self.currency)

    @transaction()
    def create_balance(self, client_id, active=1, curs=None):
        balance = Balance(
            client_id=client_id,
            active=active,
            currency_id=getattr(self.currency, 'id')
        )
        actions.insert(curs, balance)
        return balance

    @transaction()
    def add_receipt(self, client_id, amount, curs=None):
        actions.insert(curs, Receipt(client_id=client_id, amount=amount))

    @transaction()
    def add_bonus(self, client_id, amount, curs=None):
        actions.insert(curs, Bonus(client_id=client_id, amount=amount))

    @transaction()
    def add_chargeoff(self, client_id, product_id, amount, curs=None):
        actions.insert(curs, ChargeOff(client_id=client_id, product_id=product_id,
            locked_date=datetime.datetime.now(), amount=amount))

    @transaction()
    def get_receipt_total(self, client_id, curs=None):
        pass
#        return actions.get(curs, BalanceTotalView, Eq('client_id', client_id))

    def check_view(self, obj, expect_values):
        for k, v in expect_values.iteritems():
            self.assertEqual(v, getattr(obj, k))

    def test_view(self):
        pass
#        client_one = 'one'
#        self.create_balance(client_one)
#        self.check_view(self.get_balance_total(client_one),
#            {'client_id': client_one, 'receipt_total': 0, 'bonus_total': 0, 'chargeoff_total': 0})
#
#        self.add_receipt(client_one, 50)
#        self.add_receipt(client_one, 10)
#        self.check_view(self.get_balance_total(client_one),
#            {'client_id': client_one, 'receipt_total': 60, 'bonus_total': 0, 'chargeoff_total': 0})
#
#        self.add_bonus(client_one, 3)
#        self.add_bonus(client_one, 17)
#        self.check_view(self.get_balance_total(client_one),
#            {'client_id': client_one, 'receipt_total': 60, 'bonus_total': 20, 'chargeoff_total': 0})

#        client_two = 'two'
#        self.create_balance(client_two)
#        self.check_view(self.get_balance_total(client_two),
#            {'client_id': client_two, 'receipt_total': 0, 'bonus_total': 0, 'chargeoff_total': 0})
#        self.add_bonus(client_two, 20)
#        self.add_bonus(client_two, 70)
#        self.check_view(self.get_balance_total(client_two),
#            {'client_id': client_two, 'receipt_total': 0, 'bonus_total': 90, 'chargeoff_total': 0})
#
#        client_three = 'three'
#        self.create_balance(client_three)
#        self.check_view(self.get_balance_total(client_three),
#            {'client_id': client_three, 'receipt_total': 0, 'bonus_total': 0, 'chargeoff_total': 0})
#        self.add_chargeoff(client_three, 'a', 4)
#        self.add_chargeoff(client_three, 'b', 6)
#        self.check_view(self.get_balance_total(client_three),
#            {'client_id': client_three, 'receipt_total': 0, 'bonus_total': 0, 'chargeoff_total': 10})


if __name__ == '__main__':
    unittest.main()