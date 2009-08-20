import datetime
import unittest

from common import LogicTestCase

from helixcore.mapping.actions import insert
from helixcore.db.wrapper import EmptyResultSetError

from helixbilling.conf.db import transaction
from helixbilling.logic.actions import handle_action
from helixbilling.logic.exceptions import ActionNotAllowedError, DataIntegrityError
from helixbilling.domain.objects import Currency, Balance


class LockTestCase(LogicTestCase):

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
            available_amount=5000, overdraft_limit=7000
        )
        self.balance = balance #IGNORE:W0201
        insert(curs, self.balance)

    def test_lock_ok(self):
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': 'super-light 555',
            'amount': (60, 00),
        }
        handle_action('lock', data)
        balance = self._get_balance(data['client_id'])

        self.assertEquals(balance.available_amount, -1000)
        self.assertEquals(balance.locked_amount, 6000)

        lock = self._get_lock(self.balance.client_id, data['product_id']) #IGNORE:E1101
        self.assertEquals(lock.client_id, data['client_id'])
        self.assertEquals(lock.amount, 6000)
        self.assertTrue(isinstance(lock.locked_date, datetime.datetime))

    def test_lock_overdraft_violation(self):
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': 'lucky boy',
            'amount': (120, 43),
        }
        self.assertRaises(ActionNotAllowedError, handle_action, 'lock', data)

    def test_unlock_ok(self):
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': '555',
            'amount': (60, 00),
        }
        handle_action('lock', data)

        del data['amount']
        handle_action('unlock', data)

        balance = self._get_balance(data['client_id'])

        self.assertEquals(balance.available_amount, 5000)
        self.assertEquals(balance.locked_amount, 0)
        self.assertRaises(EmptyResultSetError, self._get_lock, self.balance.client_id, data['product_id']) #IGNORE:E1101

    def test_unlock_inexistent(self):
        data = {
            'client_id': self.balance.client_id, #IGNORE:E1101
            'product_id': '555',
            'amount': (60, 00),
        }
        handle_action('lock', data)

        del data['amount']
        data['product_id'] = '444'
        self.assertRaises(DataIntegrityError, handle_action, 'unlock', data)

if __name__ == '__main__':
    unittest.main()