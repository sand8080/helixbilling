from helixbilling.test.root_test import RootTestCase

import install

from helixcore.db.cond import Eq, And
from helixcore.mapping import actions

from helixbilling.conf.db import transaction
from helixbilling.domain.objects import Currency, Balance, Receipt, BalanceLock, Bonus, ChargeOff


class LogicTestCase(RootTestCase):
    '''
    abstract class. All logic test cases may inherit rom this
    '''

    def setUp(self):
        install.execute('reinit')

    @transaction()
    def _add_currency(self, curs=None):
        actions.insert(curs, Currency(name='USD', designation='$'))

    @transaction()
    def _get_balance(self, client_id, curs=None):
        return actions.get(curs, Balance, Eq('client_id', client_id))

    @transaction()
    def _get_currency(self, name, curs=None):
        return actions.get(curs, Currency, Eq('name', name))

    @transaction()
    def _get_receipts(self, client_id, curs=None):
        return actions.get_list(curs, Receipt, Eq('client_id', client_id))

    @transaction()
    def _get_bonuses(self, client_id, curs=None):
        return actions.get_list(curs, Bonus, Eq('client_id', client_id))

    @transaction()
    def _get_lock(self, client_id, product_id, curs=None):
        return actions.get(curs, BalanceLock, And(Eq('client_id', client_id), Eq('product_id', product_id)))

    @transaction()
    def _get_charge_off(self, client_id, product_id, curs=None):
        return actions.get(curs, ChargeOff, And(Eq('client_id', client_id), Eq('product_id', product_id)))

    @transaction()
    def _make_balance_passive(self, balance, curs=None):
        balance.active = 0
        actions.update(curs, balance)

class TestCaseWithBalance(LogicTestCase):
    def setUp(self):
        LogicTestCase.setUp(self)
        self._fixture()

    @transaction()
    def _fixture(self, curs=None):
        self.currency = Currency(name='USD', designation='$') #IGNORE:W0201
        actions.insert(curs, self.currency)
        self.currency = actions.reload(curs, self.currency)

        balance = Balance(
            client_id='123', active=1,
            currency_id=getattr(self.currency, 'id')
        )
        self.balance = balance #IGNORE:W0201
        actions.insert(curs, self.balance)
