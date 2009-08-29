import datetime

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
    def _get_chargeoff(self, client_id, product_id, curs=None):
        return actions.get(curs, ChargeOff, And(Eq('client_id', client_id), Eq('product_id', product_id)))

    @transaction()
    def _make_balance_passive(self, balance, curs=None):
        balance.active = 0
        actions.update(curs, balance)


class TestCaseWithCurrency(LogicTestCase):
    def setUp(self):
        super(TestCaseWithCurrency, self).setUp()
        self._fixture()

    @transaction()
    def _fixture(self, curs=None):
        self.currency = Currency(name='USD', designation='$') #IGNORE:W0201
        actions.insert(curs, self.currency)
        self.currency = actions.reload(curs, self.currency)


class TestCaseWithBalance(TestCaseWithCurrency):
    def setUp(self):
        super(TestCaseWithBalance, self).setUp()
        self.balance = self.create_balance(client_id='123') #IGNORE:W0201

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
    def reload_balance(self, balance, curs=None):
        return actions.reload(curs, balance, for_update=True)

    @transaction()
    def update_balance(self, balance, curs=None):
        actions.update(curs, balance)
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


class ViewTestCase(TestCaseWithBalance):
    def check_view(self, obj, expect_values):
        for k, v in expect_values.iteritems():
            self.assertEqual(v, getattr(obj, k))