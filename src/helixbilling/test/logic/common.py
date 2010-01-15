from decimal import Decimal
import datetime

from helixbilling.test.db_based_test import ServiceTestCase

from helixcore.db.sql import Eq, And
import helixcore.mapping.actions as mapping

from helixbilling.conf.db import transaction
from helixbilling.domain.objects import Currency, Balance, Receipt, BalanceLock, Bonus, ChargeOff
from helixbilling.logic.helper import cents_to_decimal
from helixbilling.logic.actions import handle_action
from helixbilling.logic import selector


class LogicTestCase(ServiceTestCase):
    '''
    abstract class. All logic test cases may inherit rom this
    '''
    @transaction()
    def _add_currency(self, curs=None):
        mapping.insert(curs, Currency(name='YYY', designation='$'))

    @transaction()
    def _get_currency(self, code, curs=None):
        return mapping.get(curs, Currency, Eq('code', code))

    @transaction()
    def _add_balance(self, client_id, currency_id, active=1, available_real_amount=0,
        available_virtual_amount=0, overdraft_limit=0, locking_order=None,
        locked_amount=0, curs=None):
        if locking_order is None:
            locking_order = ['available_real_amount', 'available_virtual_amount']
        mapping.insert(curs, Balance(client_id=client_id, currency_id=currency_id, active=active,
            available_real_amount=available_real_amount, available_virtual_amount=available_virtual_amount,
            overdraft_limit=overdraft_limit, locking_order=locking_order, locked_amount=locked_amount))

    @transaction()
    def _get_balance(self, client_id, curs=None):
        return mapping.get(curs, Balance, Eq('client_id', client_id))

    @transaction()
    def _get_validated_balance(self, billing_manager_login, client_id, curs=None):
        balance = mapping.get(curs, Balance, Eq('client_id', client_id))
        manager = self.get_billing_manager_by_login(billing_manager_login)
        self.assertEqual(manager.id, balance.billing_manager_id)
        return balance

    @transaction()
    def _get_receipts(self, client_id, curs=None):
        return mapping.get_list(curs, Receipt, Eq('client_id', client_id))

    @transaction()
    def _get_bonuses(self, client_id, curs=None):
        return mapping.get_list(curs, Bonus, Eq('client_id', client_id))

    @transaction()
    def _get_lock(self, client_id, product_id, curs=None):
        return mapping.get(curs, BalanceLock, And(Eq('client_id', client_id), Eq('product_id', product_id)))

    @transaction()
    def _get_chargeoff(self, client_id, product_id, curs=None):
        return mapping.get(curs, ChargeOff, And(Eq('client_id', client_id), Eq('product_id', product_id)))

    @transaction()
    def _make_balance_passive(self, balance, curs=None):
        balance.active = 0
        mapping.update(curs, balance)


class TestCaseWithCurrency(LogicTestCase):
    def setUp(self):
        super(TestCaseWithCurrency, self).setUp()
        self._fixture()

    @transaction()
    def _fixture(self, curs=None):
        self.currency = Currency(code='YYY', name='y currency', location='y country', cent_factor=100) #IGNORE:W0201
        mapping.insert(curs, self.currency)
        self.currency = mapping.reload(curs, self.currency)

    @transaction()
    def get_currency_by_balance(self, balance, curs=None):
        return selector.get_currency_by_balance(curs, balance)

class TestCaseWithBalance(TestCaseWithCurrency):
    def setUp(self):
        super(TestCaseWithBalance, self).setUp()
        self.balance = self.add_balance('123', self.currency) #IGNORE:W0201

    @transaction()
    def add_balance(self, client_id, currency, active=True, overdraft_limit=None,
        locking_order=None, curs=None):
        data = {
            'login': self.test_login,
            'password': self.test_password,
            'client_id': client_id,
            'currency': currency.code,
            'active': active,
        }
        if locking_order is not None:
            data['locking_order'] = locking_order
        if overdraft_limit is not None:
            data['overdraft_limit'] = overdraft_limit

        handle_action('add_balance', data)
        balance = mapping.get(curs, Balance, Eq('client_id', client_id))
        self.assertTrue(balance.id > 0) #IGNORE:E1101
        self.assertEquals(client_id, balance.client_id) #IGNORE:E1101
        self.assertTrue(isinstance(balance.created_date, datetime.datetime)) #IGNORE:E1101
        self.assertEquals(0, balance.available_real_amount)
        self.assertEquals(0, balance.locked_amount)
        if overdraft_limit is None:
            self.assertEquals(Decimal(0), cents_to_decimal(currency, balance.overdraft_limit))
        else:
            self.assertEquals(Decimal(overdraft_limit), cents_to_decimal(currency, balance.overdraft_limit))
        self.assertEquals(currency.id, balance.currency_id)
        self.assertEquals(locking_order, balance.locking_order)
        return balance

    @transaction()
    def reload_balance(self, balance, curs=None):
        return mapping.reload(curs, balance, for_update=True)

    @transaction()
    def update_balance(self, balance, curs=None):
        mapping.update(curs, balance)
        return balance

    @transaction()
    def add_receipt(self, client_id, amount, curs=None):
        mapping.insert(curs, Receipt(client_id=client_id, amount=amount))

    @transaction()
    def add_bonus(self, client_id, amount, curs=None):
        mapping.insert(curs, Bonus(client_id=client_id, amount=amount))

    @transaction()
    def add_chargeoff(self, client_id, product_id, real_amount, virtual_amount, curs=None):
        mapping.insert(curs, ChargeOff(client_id=client_id, product_id=product_id,
            locked_date=datetime.datetime.now(), real_amount=real_amount, virtual_amount=virtual_amount))


class ViewTestCase(TestCaseWithBalance):
    def check_view(self, obj, expect_values):
        for k, v in expect_values.iteritems():
            self.assertEqual(v, getattr(obj, k))