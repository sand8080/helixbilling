import unittest

from common import LogicTestCase

from helixcore.mapping.actions import insert

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.domain.objects import Currency, Balance
import helixbilling.logic.product_status as product_status

class ProductStatusTestCase(LogicTestCase):

    def setUp(self):
        LogicTestCase.setUp(self)
        self._fixture()

    @transaction()
    def _fixture(self, curs=None):
        self.currency = Currency(name='USD', designation='$') #IGNORE:W0201
        insert(curs, self.currency)

        balance = Balance(
            client_id='123', active=1,
            currency_id=self.currency.id, #IGNORE:E1101
            available_amount=5000,
            overdraft_limit=7000
        )
        self.balance = balance #IGNORE:W0201
        insert(curs, self.balance)

    def test_product_status_locked(self):
        lock_amount = (60, 00)
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': '555',
            'amount': lock_amount,
        }
        handle_action('lock', data)
        lock = self._get_lock(self.balance.client_id, data['product_id']) #IGNORE:E1101

        del data['amount']
        response = handle_action('product_status', data)
        self.assertEquals(product_status.locked, response['product_status'])
        self.assertEquals(lock.locked_date, response['locked_date'])
        self.assertEquals(lock_amount, response['amount'])

    def test_product_status_charged_off(self):
        lock_amount = (60, 00)
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': '555',
            'amount': lock_amount,
        }
        handle_action('lock', data)

        del data['amount']
        handle_action('chargeoff', data)
        chargeoff = self._get_chargeoff(self.balance.client_id, data['product_id']) #IGNORE:E1101

        response = handle_action('product_status', data)
        self.assertEquals(product_status.charged_off, response['product_status'])
        self.assertEquals(chargeoff.locked_date, response['locked_date'])
        self.assertEquals(chargeoff.chargeoff_date, response['chargeoff_date'])
        self.assertEquals(lock_amount, response['amount'])

    def test_product_status_unknown(self):
        lock_amount = (60, 00)
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': '555',
            'amount': lock_amount,
        }
        handle_action('lock', data)

        del data['amount']
        data['product_id'] = '556'
        response = handle_action('product_status', data)
        self.assertEquals(product_status.unknown, response['product_status'])


if __name__ == '__main__':
    unittest.main()