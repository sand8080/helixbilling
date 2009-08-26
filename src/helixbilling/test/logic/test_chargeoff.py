import datetime
import unittest

from common import LogicTestCase

from helixcore.mapping import actions
from helixcore.db.wrapper import EmptyResultSetError

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.logic.exceptions import ActionNotAllowedError
from helixbilling.domain.objects import Currency, Balance, BalanceLock

class ChargeOffTestCase(LogicTestCase):

    def setUp(self):
        LogicTestCase.setUp(self)
        self._fixture()

    @transaction()
    def _fixture(self, curs=None):
        self.currency = Currency(name='USD', designation='$') #IGNORE:W0201
        actions.insert(curs, self.currency)

        balance = Balance(
            client_id='PVH 123', active=1,
            currency_id=self.currency.id, #IGNORE:E1101
            available_amount=5000, overdraft_limit=7000,
            locked_amount=2500
        )
        self.balance = balance #IGNORE:W0201
        actions.insert(curs, self.balance)

        self.product_id = '33 cow' #IGNORE:W0201
        lock = BalanceLock(
            client_id=self.balance.client_id, #IGNORE:E1101
            product_id=self.product_id,
            amount=2500
        )
        self.lock = lock #IGNORE:W0201
        actions.insert(curs, self.lock)
        self.lock = actions.reload(curs, self.lock)

    def test_chargeoff_ok(self):
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': self.product_id,
        }
        handle_action('chargeoff', data)
        balance = self._get_balance(data['client_id'])

        self.assertEquals(balance.locked_amount, 0)
        #same available amount
        self.assertEquals(balance.available_amount, self.balance.available_amount) #IGNORE:E1101

        #no lock
        self.assertRaises(EmptyResultSetError, self._get_lock, balance.client_id, data['product_id']) #IGNORE:E1101

        chargeoff = self._get_chargeoff(balance.client_id, data['product_id'])

        self.assertEquals(chargeoff.client_id, data['client_id'])
        self.assertEquals(chargeoff.amount, self.lock.amount) #IGNORE:E1103
        self.assertEquals(chargeoff.locked_date, self.lock.locked_date) #IGNORE:E1103
        self.assertTrue(isinstance(chargeoff.chargeoff_date, datetime.datetime))

    def test_chargeoff_not_locked(self):
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': '555',
        }
        self.assertRaises(ActionNotAllowedError, handle_action, 'chargeoff', data)


if __name__ == '__main__':
    unittest.main()