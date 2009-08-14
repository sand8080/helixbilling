
from helixcore.mapping.actions import insert, update, delete
from helixcore.db.wrapper import EmptyResultSetError

from helixbilling.conf.db import transaction

from helixbilling.domain.objects import Currency, Balance, Receipt, BalanceLock, Bonus, ChargeOff
from helixbilling.logic.response import response_ok
from helixbilling.logic.exceptions import ActionNotAllowedError, DataIntegrityError
import helixbilling.logic.product_status as product_status

from helper import get_currency_by_name, get_currency_by_balance, get_balance, try_get_lock, try_get_chargeoff
from helper import compose_amount, decompose_amount
from selectors import select_receipts

class Handler(object):
    '''
    Handles all API actions. Method names are called like actions.
    '''

    def ping(self, data): #IGNORE:W0613
        return response_ok()

    # --- currency ---

    @transaction()
    def add_currency(self, data, curs=None):
        curr = Currency(**data)
        insert(curs, curr)
        return response_ok()

    @transaction()
    def modify_currency(self, data, curs=None):
        curr = get_currency_by_name(curs, data['name'], True)
        curr.update(data)
        update(curs, curr)
        return response_ok()

    @transaction()
    def delete_currency(self, data, curs=None):
        curr = get_currency_by_name(curs, data['name'], True)
        delete(curs, curr)
        return response_ok()

    # --- balance ---

    @transaction()
    def create_balance(self, data, curs=None):
        currency = get_currency_by_name(curs, data['currency_name'], False)

        del data['currency_name']
        data['currency_id'] = currency.id
        data['overdraft_limit'] = compose_amount(currency, 'overdraft limit', *data['overdraft_limit'])
        balance = Balance(**data)
        insert(curs, balance)
        return response_ok()

    @transaction()
    def modify_balance(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=False, for_update=True)

        if 'overdraft_limit' in data:
            currency = get_currency_by_balance(curs, balance)
            data['overdraft_limit'] = compose_amount(currency, 'overdraft limit', *data['overdraft_limit'])

        balance.update(data)
        update(curs, balance)
        return response_ok()

    @transaction()
    def enroll_receipt(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=True, for_update=True)
        currency = get_currency_by_balance(curs, balance)

        data['amount'] = compose_amount(currency, 'receipt', *data['amount'])

        receipt = Receipt(**data)
        insert(curs, receipt)

        balance.available_amount += receipt.amount #IGNORE:E1101
        update(curs, balance)
        return response_ok()

    @transaction()
    def lock(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=True, for_update=True)
        currency = get_currency_by_balance(curs, balance)

        data['amount'] = compose_amount(currency, 'lock', *data['amount'])

        if balance.available_amount - data['amount'] < -balance.overdraft_limit:
            raise ActionNotAllowedError('Cannot lock %(1)s.%(2)s %(0)s: the amount violates current overdraft limit of %(3)s.%(4)s %(0)s. Available amount on balance is %(5)s.%(6)s %(0)s' %
                dict(zip(
                    map(str, range(7)),
                    tuple(currency.designation) +
                    decompose_amount(currency, data['amount']) +
                    decompose_amount(currency, balance.overdraft_limit) +
                    decompose_amount(currency, balance.available_amount)
                ))
            )

        lock = BalanceLock(**data)
        insert(curs, lock)

        balance.available_amount -= lock.amount #IGNORE:E1101
        balance.locked_amount += lock.amount #IGNORE:E1101
        update(curs, balance)
        return response_ok()

    @transaction()
    def unlock(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=True, for_update=True)

        try:
            lock = try_get_lock(curs, data['client_id'], data['product_id'], for_update=True)
        except EmptyResultSetError:
            raise DataIntegrityError('Cannot unlock money for product %d: amount was not locked for this product' % data['product_id'])

        delete(curs, lock)

        balance.available_amount += lock.amount #IGNORE:E1101
        balance.locked_amount -= lock.amount #IGNORE:E1101

        update(curs, balance)
        return response_ok()

    @transaction()
    def product_status(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=False, for_update=False)
        currency = get_currency_by_balance(curs, balance)

        response = {'product_status': product_status.unknown}
        try:
            lock = try_get_lock(curs, data['client_id'], data['product_id'], for_update=False)
            response['product_status'] = product_status.locked
            response['locked_date'] = lock.locked_date
            response['amount'] = decompose_amount(currency, lock.amount)
        except EmptyResultSetError: #IGNORE:W0704
            pass

        try:
            chargeoff = try_get_chargeoff(curs, data['client_id'], data['product_id'], for_update=False)
            response['product_status'] = product_status.charged_off
            response['locked_date'] = chargeoff.locked_date
            response['chargeoff_date'] = chargeoff.chargeoff_date
            response['amount'] = decompose_amount(currency, chargeoff.amount)
        except EmptyResultSetError: #IGNORE:W0704
            pass

        return response_ok(**response)

    @transaction()
    def make_bonus(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=True, for_update=True)
        currency = get_currency_by_balance(curs, balance)

        data['amount'] = compose_amount(currency, 'bonus', *data['amount'])

        bonus = Bonus(**data)
        insert(curs, bonus)

        balance.available_amount += bonus.amount #IGNORE:E1101
        update(curs, balance)
        return response_ok()

    @transaction()
    def charge_off(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=True, for_update=True)

        try:
            lock = try_get_lock(curs, data['client_id'], data['product_id'], for_update=True)
        except EmptyResultSetError:
            raise ActionNotAllowedError('Cannot charge off money for product %d: amount was not locked for this product' % data['product_id'])

        chargeoff = ChargeOff(locked_date=lock.locked_date, amount=lock.amount, **data)

        delete(curs, lock)
        insert(curs, chargeoff)

        balance.locked_amount -= lock.amount #IGNORE:E1101
        update(curs, balance)
        return response_ok()

    #list operations

    @transaction()
    def list_receipts(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=False, for_update=False) #IGNORE:W0612
        receipts = select_receipts(curs, data['client_id'], data.get('start_date'), data.get('end_date'))
        return response_ok(receipts=receipts)
