import datetime

from helixbilling.test.db_based_test import DbBasedTestCase

from helixcore.db.sql import Eq, And
from helixcore.mapping import actions

from helixbilling.conf.db import transaction
from helixbilling.domain.objects import Currency, Balance, Receipt, BalanceLock, Bonus, ChargeOff


class LogicTestCase(DbBasedTestCase):
    '''
    abstract class. All logic test cases may inherit rom this
    '''
    @transaction()
    def _add_currency(self, curs=None):
        actions.insert(curs, Currency(name='USD', designation='$'))

    @transaction()
    def _get_currency(self, name, curs=None):
        return actions.get(curs, Currency, Eq('name', name))

    @transaction()
    def _add_balance(self, client_id, currency_id, active=1, available_real_amount=0,
        available_virtual_amount=0, overdraft_limit=0, locking_order=None,
        locked_amount=0, curs=None):
        if locking_order is None:
            locking_order = ['available_real_amount', 'available_virtual_amount']
        actions.insert(curs, Balance(client_id=client_id, currency_id=currency_id, active=active,
            available_real_amount=available_real_amount, available_virtual_amount=available_virtual_amount,
            overdraft_limit=overdraft_limit, locking_order=locking_order, locked_amount=locked_amount))

    @transaction()
    def _get_balance(self, client_id, curs=None):
        return actions.get(curs, Balance, Eq('client_id', client_id))

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
    def add_chargeoff(self, client_id, product_id, real_amount, virtual_amount, curs=None):
        actions.insert(curs, ChargeOff(client_id=client_id, product_id=product_id,
            locked_date=datetime.datetime.now(), real_amount=real_amount, virtual_amount=virtual_amount))


class ViewTestCase(TestCaseWithBalance):
    def check_view(self, obj, expect_values):
        for k, v in expect_values.iteritems():
            self.assertEqual(v, getattr(obj, k))