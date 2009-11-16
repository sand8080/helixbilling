from functools import partial

import helixcore.mapping.actions as mapping
from helixcore.db.wrapper import EmptyResultSetError
from helixcore.db.sql import Eq, And
from helixcore.server.response import response_ok
from helixcore.server.exceptions import ActionNotAllowedError, DataIntegrityError

from helixbilling.conf.db import transaction
from helixbilling.domain.objects import Currency, Balance, Receipt, BalanceLock, Bonus, ChargeOff, BillingManager
import helixbilling.logic.product_status as product_status
from helixbilling.domain import security

from helper import get_currency_by_code, get_currency_by_balance, get_balance, try_get_lock, try_get_chargeoff, get_date_filters
from helper import compose_amount, decompose_amount, compute_locks
from action_log import logged, logged_bulk
import selector


def authentificate(method):
    def decroated(self, data, curs):
        data['billing_manager_id'] = self.get_billing_manager_id(curs, data)
        del data['login']
        del data['password']
        return method(self, data, curs)
    return decroated


class Handler(object):
    '''
    Handles all API actions. Method names are called like actions.
    '''
    def ping(self, data): #IGNORE:W0613
        return response_ok()

    def get_billing_manager_id(self, curs, data):
        return selector.get_auth_billing_manager(curs, data['login'], data['password']).id

    # billing manager
    @transaction()
    def add_billing_manager(self, data, curs=None):
        data['password'] = security.encrypt_password(data['password'])
        mapping.insert(curs, BillingManager(**data))
        return response_ok()

    def get_fields_for_update(self, data, prefix_of_new='new_'):
        '''
        If data contains fields with previx == prefix_of_new,
        such fields will be added into result dict:
            {'field': 'new_field'}
        '''
        result = {}
        for f in data.keys():
            if f.startswith(prefix_of_new):
                result[f[len(prefix_of_new):]] = f
        return result

    def update_obj(self, curs, data, load_obj_func):
        to_update = self.get_fields_for_update(data)
        if len(to_update):
            obj = load_obj_func()
            for f, new_f in to_update.items():
                setattr(obj, f, data[new_f])
            mapping.update(curs, obj)

    @transaction()
    @authentificate
    def modify_billing_manager(self, data, curs=None):
        if 'new_password' in data:
            data['new_password'] = security.encrypt_password(data['new_password'])
        loader = partial(selector.get_billing_manager, curs, data['billing_manager_id'], for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    def delete_billing_manager(self, data, curs=None):
        obj = selector.get_billing_manager(curs, data['billing_manager_id'])
        mapping.delete(curs, obj)
        return response_ok()

    # --- currencies ---
    @transaction()
    @logged
    def view_currencies(self, data, curs=None): #IGNORE:W0613
        return response_ok(currencies=selector.select(curs, Currency, None, None, 0))

    # --- balance ---
    @transaction()
    @logged
    def create_balance(self, data, curs=None):
        data_copy = dict(data)
        currency = get_currency_by_code(curs, data_copy['currency_name'])
        del data_copy['currency_name']
        data_copy['currency_id'] = currency.id
        data_copy['overdraft_limit'] = compose_amount(currency, 'overdraft limit', *data_copy['overdraft_limit'])
        balance = Balance(**data_copy)
        mapping.insert(curs, balance)
        return response_ok()

    @transaction()
    @logged
    def modify_balance(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=False, for_update=True)
        if 'overdraft_limit' in data:
            currency = get_currency_by_balance(curs, balance)
            data['overdraft_limit'] = compose_amount(currency, 'overdraft limit', *data['overdraft_limit'])
        balance.update(data)
        mapping.update(curs, balance)
        return response_ok()

    @transaction()
    @logged
    def delete_balance(self, data, curs=None):
        obj = get_balance(curs, data['client_id'], active_only=False, for_update=True)
        mapping.delete(curs, obj)
        return response_ok()

    # --- receipt ---
    @transaction()
    @logged
    def enroll_receipt(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=True, for_update=True)
        currency = get_currency_by_balance(curs, balance)

        data['amount'] = compose_amount(currency, 'receipt', *data['amount'])

        receipt = Receipt(**data)
        mapping.insert(curs, receipt)

        balance.available_real_amount += receipt.amount #IGNORE:E1101
        mapping.update(curs, balance)
        return response_ok()

    def _lock(self, data_list, curs):
        for data in data_list:
            data_copy = dict(data)
            balance = get_balance(curs, data_copy['client_id'], active_only=True, for_update=True)
            currency = get_currency_by_balance(curs, balance)
            lock_amount = compose_amount(currency, 'lock', *data_copy['amount'])
            locks = compute_locks(currency, balance, lock_amount)

            del data_copy['amount']
            lock = BalanceLock(
                real_amount=locks['available_real_amount'],
                virtual_amount=locks['available_virtual_amount'],
                **data_copy
            )
            mapping.insert(curs, lock)

            balance.available_real_amount -= lock.real_amount #IGNORE:E1101
            balance.available_virtual_amount -= lock.virtual_amount #IGNORE:E1101
            balance.locked_amount += lock.real_amount #IGNORE:E1101
            balance.locked_amount += lock.virtual_amount #IGNORE:E1101

            mapping.update(curs, balance)

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

            mapping.delete(curs, lock)

            balance = balances[lock.client_id]
            balance.available_real_amount += lock.real_amount
            balance.available_virtual_amount += lock.virtual_amount
            balance.locked_amount -= lock.real_amount #IGNORE:E1101
            balance.locked_amount -= lock.virtual_amount #IGNORE:E1101

            mapping.update(curs, balance)

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
            response['real_amount'] = decompose_amount(currency, lock.real_amount)
            response['virtual_amount'] = decompose_amount(currency, lock.virtual_amount)
        except EmptyResultSetError: #IGNORE:W0704
            pass

        try:
            chargeoff = try_get_chargeoff(curs, data['client_id'], data['product_id'], for_update=False)
            response['product_status'] = product_status.charged_off
            response['locked_date'] = chargeoff.locked_date
            response['chargeoff_date'] = chargeoff.chargeoff_date
            response['real_amount'] = decompose_amount(currency, chargeoff.real_amount)
            response['virtual_amount'] = decompose_amount(currency, chargeoff.virtual_amount)
        except EmptyResultSetError: #IGNORE:W0704
            pass

        return response_ok(**response)

    @transaction()
    @logged
    def enroll_bonus(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=True, for_update=True)
        currency = get_currency_by_balance(curs, balance)

        data['amount'] = compose_amount(currency, 'bonus', *data['amount'])

        bonus = Bonus(**data)
        mapping.insert(curs, bonus)

        balance.available_virtual_amount += bonus.amount #IGNORE:E1101
        mapping.update(curs, balance)
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

            chargeoff = ChargeOff(locked_date=lock.locked_date,
                real_amount=lock.real_amount, virtual_amount=lock.virtual_amount, **data)

            mapping.delete(curs, lock)
            mapping.insert(curs, chargeoff)

            balance.locked_amount -= lock.real_amount #IGNORE:E1101
            balance.locked_amount -= lock.virtual_amount #IGNORE:E1101

            mapping.update(curs, balance)

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

    #view operations

    @transaction()
    def view_receipts(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=False) #IGNORE:W0612
        currency = get_currency_by_balance(curs, balance)

        cond = Eq('client_id', data['client_id'])
        date_filters = (
            ('start_date', 'end_date', 'created_date'),
        )
        cond = And(cond, get_date_filters(date_filters, data))

        receipts, total = selector.select_receipts(curs, currency, cond, data['limit'], data['offset'])
        return response_ok(receipts=receipts, total=total)

    @transaction()
    def view_chargeoffs(self, data, curs=None):
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

        chargeoffs, total = selector.select_chargeoffs(curs, currency, cond, data['limit'], data['offset'])
        return response_ok(chargeoffs=chargeoffs, total=total)

    @transaction()
    def view_balance_locks(self, data, curs=None):
        balance = get_balance(curs, data['client_id'], active_only=False) #IGNORE:W0612
        currency = get_currency_by_balance(curs, balance)

        cond = Eq('client_id', data['client_id'])
        if 'product_id' in data:
            cond = And(cond, Eq('product_id', data['product_id']))

        date_filters = (
            ('locked_start_date', 'locked_end_date', 'locked_date'),
        )
        cond = And(cond, get_date_filters(date_filters, data))

        balance_locks, total = selector.select_balance_locks(curs, currency, cond, data['limit'], data['offset'])
        return response_ok(balance_locks=balance_locks, total=total)
