from helixcore.mapping.actions import insert, update, delete
from helixcore.db.wrapper import EmptyResultSetError
from helixcore.db.cond import Eq, And

from helixbilling.conf.db import transaction

from helixbilling.domain.objects import Currency, Balance, Receipt, BalanceLock, Bonus, ChargeOff
from helixbilling.logic.response import response_ok
from helixbilling.logic.exceptions import ActionNotAllowedError, DataIntegrityError
import helixbilling.logic.product_status as product_status

from helper import get_currency_by_name, get_currency_by_balance, get_balance, try_get_lock, try_get_chargeoff, get_date_filters
from helper import compose_amount, decompose_amount
from selectors import select_receipts, select_chargeoffs, select_balance_locks
from action_log import logged, logged_bulk


class Handler(object):
    '''
    Handles all API actions. Method names are called like actions.
    '''

    def ping(self, data): #IGNORE:W0613
        return response_ok()

    # --- currency ---

    @transaction()
    @logged
    def add_currency(self, data, curs=None):
        curr = Currency(**data)
        insert(curs, curr)
        return response_ok()

    @transaction()
    @logged
    def modify_currency(self, data, curs=None):
        curr = get_currency_by_name(curs, data['name'], True)
        curr.update(data)
        update(curs, curr)
        return response_ok()

    @transaction()
    @logged
    def delete_currency(self, data, curs=None):
        curr = get_currency_by_name(curs, data['name'], True)
        delete(curs, curr)
        return response_ok()

    # --- balance ---

    def _check_locking_order(self, data):
        if 'locking_order' not in data:
            return
        locking_order = data['locking_order']
        if locking_order is None:
            return
        else:
            max_len = 2
            if len(locking_order) > max_len:
                raise ActionNotAllowedError('locking_order len > %d' % max_len)
            locks_available = ['available_real_amount', 'available_virtual_amount']
            if len([f for f in locking_order if f not in locks_available]) > 0:
                raise ActionNotAllowedError('Only %s fields available to lock' % locks_available)

    @transaction()
    @logged
    def create_balance(self, data, curs=None):
        currency = get_currency_by_name(curs, data['currency_name'], False)

        del data['currency_name']
        data['currency_id'] = currency.id
        data['overdraft_limit'] = compose_amount(currency, 'overdraft limit', *data['overdraft_limit'])
        self._check_locking_order(data)
        balance = Balance(**data)
        insert(curs, balance)
        return response_ok()

    @transaction()
    @logged
    def modify_balance(self, data, curs=None):
        self._check_locking_order(data)
        balance = get_balance(curs, data['client_id'], active_only=False, for_update=True)
        if 'overdraft_limit' in data:
            currency = get_currency_by_balance(curs, balance)
            data['overdraft_limit'] = compose_amount(currency, 'overdraft limit', *data['overdraft_limit'])
        balance.update(data)
        update(curs, balance)
        return response_ok()

    @transaction()
    @logged
    def enroll_receipt(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=True, for_update=True)
        currency = get_currency_by_balance(curs, balance)

        data['amount'] = compose_amount(currency, 'receipt', *data['amount'])

        receipt = Receipt(**data)
        insert(curs, receipt)

        balance.available_real_amount += receipt.amount #IGNORE:E1101
        update(curs, balance)
        return response_ok()

    def _lock(self, data_list, curs):
        for data_orig in data_list:
            data = dict(data_orig)

            balance = get_balance(curs, data['client_id'], active_only=True, for_update=True)
            currency = get_currency_by_balance(curs, balance)
            lock_amount = compose_amount(currency, 'lock', *data['amount'])
            real_lock_amount, virtual_lock_amount = self._compute_locks(currency, balance, lock_amount)

            del(data['amount'])
            lock = BalanceLock(real_amount=real_lock_amount, virtual_amount=virtual_lock_amount, **data)
            insert(curs, lock)

            balance.available_real_amount -= lock.real_amount #IGNORE:E1101
            balance.available_virtual_amount -= lock.virtual_amount #IGNORE:E1101
            balance.locked_amount += lock.real_amount #IGNORE:E1101
            balance.locked_amount += lock.virtual_amount #IGNORE:E1101

            update(curs, balance)

    def _compute_locks(self, currency, balance, lock_amount):
        """
        returns (lock_real_amount, lock_virtual_amount)
        excepiton raises if money not enought
        """
        if balance.available_real_amount + balance.available_virtual_amount - lock_amount < -balance.overdraft_limit:
            raise ActionNotAllowedError(
                'Cannot lock %(1)s.%(2)s %(0)s: '
                'the amount violates current overdraft limit of %(3)s.%(4)s %(0)s. '
                'Available amount on balance is %(5)s.%(6)s %(0)s' %
                dict(zip(
                    map(str, range(7)),
                    tuple(currency.designation) +
                    decompose_amount(currency, lock_amount) +
                    decompose_amount(currency, balance.overdraft_limit) +
                    decompose_amount(currency, balance.available_real_amount) +
                    decompose_amount(currency, balance.available_virtual_amount)
                ))
            )
        return lock_amount, 0

    @transaction()
    @logged
    def lock(self, data, curs=None):
        self._lock([data], curs)
        return response_ok()

    @transaction()
    @logged_bulk
    def lock_list(self, data, curs=None):
        """
        data = {
            'locks': [
                {'client_id': Text(), 'product_id': Text()}
                ...
            ]
        }
        """
        self._lock(data['locks'], curs)
        return response_ok()

    def _unlock(self, data_list, curs=None):
        balances = {}
        # locking all balances
        for data in data_list:
            balance = get_balance(curs, data['client_id'], active_only=True, for_update=True)
            balances[balance.client_id] = balance

        for data in data_list:
            try:
                lock = try_get_lock(curs, data['client_id'], data['product_id'], for_update=True)
            except EmptyResultSetError:
                raise DataIntegrityError(
                    'Cannot unlock money for product %s: '
                    'amount was not locked for this product'
                    % data['product_id']
                )

            delete(curs, lock)

            balance = balances[lock.client_id]
            balance.available_real_amount += lock.real_amount
            balance.available_virtual_amount += lock.virtual_amount
            balance.locked_amount -= lock.real_amount #IGNORE:E1101
            balance.locked_amount -= lock.virtual_amount #IGNORE:E1101

            update(curs, balance)

    @transaction()
    @logged
    def unlock(self, data, curs=None):
        """
        data = {
            'client_id': Text(),
            'product_id': Text(),
        }
        """
        self._unlock([data], curs)
        return response_ok()

    @transaction()
    @logged_bulk
    def unlock_list(self, data, curs=None):
        """
        data = {
            'unlocks': [
                {'client_id': Text(), 'product_id': Text(),}
                ...
            ]
        }
        """
        self._unlock(data['unlocks'], curs)
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
            response['amount'] = decompose_amount(currency, lock.real_amount + lock.virtual_amount)
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
    @logged
    def make_bonus(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=True, for_update=True)
        currency = get_currency_by_balance(curs, balance)

        data['amount'] = compose_amount(currency, 'bonus', *data['amount'])

        bonus = Bonus(**data)
        insert(curs, bonus)

        balance.available_real_amount += bonus.amount #IGNORE:E1101
        update(curs, balance)
        return response_ok()

    def _chargeoff(self, data_list, curs=None):
        balances = {}
        for data in data_list:
            balance = get_balance(curs, data['client_id'], active_only=True, for_update=True)
            balances[balance.client_id] = balance

        for data in data_list:
            try:
                lock = try_get_lock(curs, data['client_id'], data['product_id'], for_update=True)
            except EmptyResultSetError:
                raise ActionNotAllowedError(
                    'Cannot charge off money for product %s: '
                    'amount was not locked for this product'
                    % data['product_id']
                )

            lock_amount = lock.real_amount + lock.virtual_amount
            chargeoff = ChargeOff(locked_date=lock.locked_date, amount=lock_amount, **data)

            delete(curs, lock)
            insert(curs, chargeoff)

            balance.locked_amount -= lock.real_amount #IGNORE:E1101
            balance.locked_amount -= lock.virtual_amount #IGNORE:E1101

            update(curs, balance)

    @transaction()
    @logged
    def chargeoff(self, data, curs=None):
        """
        data = {
            'client_id': Text(),
            'product_id': Text(),
            'amount': (positive int, non negative int)
        }
        """
        self._chargeoff([data], curs)
        return response_ok()

    @transaction()
    @logged_bulk
    def chargeoff_list(self, data, curs=None):
        """
        data = {
            'chargeoffs': [
                {'client_id': Text(), 'product_id': Text(), 'amount': (positive int, non negative int)}
                ...
            ]
        }
        """
        self._chargeoff(data['chargeoffs'], curs)
        return response_ok()

    #list operations

    @transaction()
    def list_receipts(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=False) #IGNORE:W0612
        currency = get_currency_by_balance(curs, balance)

        cond = Eq('client_id', data['client_id'])
        date_filters = (
            ('start_date', 'end_date', 'created_date'),
        )
        cond = And(cond, get_date_filters(date_filters, data))

        receipts, total = select_receipts(curs, currency, cond, data['offset'], data['limit'])
        return response_ok(receipts=receipts, total=total)

    @transaction()
    def list_chargeoffs(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=False) #IGNORE:W0612
        currency = get_currency_by_balance(curs, balance)

        cond = Eq('client_id', data['client_id'])
        if 'product_id' in data:
            cond = And(cond, Eq('product_id', data['product_id']))

        date_filters = (
            ('locked_start_date', 'locked_end_date', 'locked_date'),
            ('chargeoff_start_date', 'chargeoff_end_date', 'chargeoff_date'),
        )
        cond = And(cond, get_date_filters(date_filters, data))

        chargeoffs, total = select_chargeoffs(curs, currency, cond, data['offset'], data['limit'])
        return response_ok(chargeoffs=chargeoffs, total=total)

    @transaction()
    def list_balance_locks(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=False) #IGNORE:W0612
        currency = get_currency_by_balance(curs, balance)

        cond = Eq('client_id', data['client_id'])
        if 'product_id' in data:
            cond = And(cond, Eq('product_id', data['product_id']))

        date_filters = (
            ('locked_start_date', 'locked_end_date', 'locked_date'),
        )
        cond = And(cond, get_date_filters(date_filters, data))

        balance_locks, total = select_balance_locks(curs, currency, cond, data['offset'], data['limit'])
        return response_ok(balance_locks=balance_locks, total=total)
