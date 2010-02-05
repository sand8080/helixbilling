from functools import partial

import helixcore.mapping.actions as mapping
from helixcore.db.wrapper import EmptyResultSetError, ObjectAlreadyExists
from helixcore.db.sql import Eq, And
from helixcore.server.response import response_ok
from helixcore.server.exceptions import ActionNotAllowedError, AuthError,\
    DataIntegrityError
from helixcore.server.errors import RequestProcessingError

from helixbilling.conf.db import transaction
from helixbilling.domain.objects import Currency, Balance, Receipt, BalanceLock, Bonus, ChargeOff, Operator
import helixbilling.logic.product_status as product_status
from helixbilling.domain import security
from helixbilling.error import BalanceNotFound, CurrencyNotFound

from helper import compute_locks, decimal_to_cents
from action_log import logged, logged_bulk
from decimal import Decimal
import selector
from helixbilling.logic.helper import cents_to_decimal
from helixbilling.logic.filters import BalanceFilter


def detalize_error(err_cls, category, f_name):
    def decorator(func):
        def decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except err_cls, e:
                raise RequestProcessingError(category, e.message,
                    details=[{'field': f_name, 'message': e.message}])
        return decorated
    return decorator


def authentificate(method):
    @detalize_error(AuthError, RequestProcessingError.Category.auth, 'login')
    def decroated(self, data, curs):
        operator = self.get_operator(curs, data)
        data['operator_id'] = operator.id
        del data['login']
        del data['password']
        data.pop('custom_operator_info', None)
        return method(self, data, operator, curs)
    return decroated


class Handler(object):
    '''
    Handles all API actions. Method names are called like actions.
    '''
    def ping(self, data): #IGNORE:W0613
        return response_ok()

    def get_operator(self, curs, data):
        return selector.get_auth_opertator(curs, data['login'], data['password'])

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

    def _decimal_texts_to_cents(self, data, currency, amount_fields):
        result = dict(data)
        for a_field in amount_fields:
            if a_field in result:
                result[a_field] = decimal_to_cents(currency, Decimal(data[a_field]))
        return result

#    def _money_to_db(self, data, currency, amount_fields):
#        result = dict(data)
#        for f in amount_fields:
#            if f in result:
#                result[f] = compose_amount(currency, *result[f])
#        return result

    # --- currencies ---
    @transaction()
    def view_currencies(self, data, curs=None): #IGNORE:W0613
        return response_ok(currencies=selector.select_data(curs, Currency, None, None, 0))

    # --- operator ---
    @transaction()
    @detalize_error(ObjectAlreadyExists, RequestProcessingError.Category.data_integrity, 'login')
    def add_operator(self, data, curs=None):
        data['password'] = security.encrypt_password(data['password'])
        data.pop('custom_operator_info', None)
        mapping.insert(curs, Operator(**data))
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(DataIntegrityError, RequestProcessingError.Category.data_integrity, 'new_login')
    def modify_operator(self, data, operator, curs=None):
        if 'new_password' in data:
            data['new_password'] = security.encrypt_password(data['new_password'])
        loader = partial(selector.get_operator, curs, operator.id, for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    # --- balance ---
    @transaction()
    @authentificate
    @detalize_error(CurrencyNotFound, RequestProcessingError.Category.data_integrity, 'currency')
    @detalize_error(ObjectAlreadyExists, RequestProcessingError.Category.data_integrity, 'customer_id')
    def add_balance(self, data, operator, curs=None): #IGNORE:W0613
        currency = selector.get_currency_by_code(curs, data['currency'])
        data['currency_id'] = currency.id
        del data['currency']
        amount_fields = ['overdraft_limit']
        balance = Balance(**self._decimal_texts_to_cents(data, currency, amount_fields))
        mapping.insert(curs, balance)
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    def modify_balance(self, data, operator, curs=None):
        c_id = data['customer_id']
        balance = selector.get_balance(curs, operator, c_id, for_update=True)
        currency = selector.get_currency_by_balance(curs, balance)
        amount_fields = ['new_overdraft_limit']
        self.update_obj(curs, self._decimal_texts_to_cents(data, currency, amount_fields),
            partial(lambda x: x, balance))
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    def delete_balance(self, data, operator, curs=None):
        obj = selector.get_balance(curs, operator, data['customer_id'], for_update=True)
        mapping.delete(curs, obj)
        return response_ok()

    def _balances_info(self, balances, currencies_idx):
        b_info = []
        for balance in balances:
            currency = currencies_idx[balance.currency_id]
            c_to_d = partial(cents_to_decimal, currency)
            b_info.append({
                'customer_id': balance.customer_id,
                'active': balance.active,
                'currency_code': currency.code,
                'creation_date': '%s' % balance.creation_date.isoformat(),
                'available_real_amount': '%s' % c_to_d(balance.available_real_amount),
                'available_virtual_amount': '%s' % c_to_d(balance.available_virtual_amount),
                'overdraft_limit': '%s' % c_to_d(balance.overdraft_limit),
                'locked_amount': '%s' % c_to_d(balance.locked_amount),
                'locking_order': balance.locking_order,
            })
        return b_info

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    def get_balance(self, data, operator, curs=None):
        c_id = data['customer_id']
        balance = selector.get_balance(curs, operator, c_id)
        currencies_idx = selector.get_currencies_indexed_by_id(curs)
        b_info = self._balances_info([balance], currencies_idx)[0]
        return response_ok(**b_info)

    def _view_objects(self, curs, data, operator, loader, counter):
        f_params = data['filter_params']
        p_params = data['paging_params']
        objects = loader(curs, operator, f_params, p_params)
        total = counter(curs, operator, f_params)
        return objects, total

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    def view_balances(self, data, operator, curs=None):
        f = BalanceFilter(operator, data['filter_params'], data['paging_params'])
        balances, total = f.filter_counted(curs)
        currencies_idx = selector.get_currencies_indexed_by_id(curs)
        b_info = self._balances_info(balances, currencies_idx)
        return response_ok(balances=b_info, total=total)

    # --- receipt ---
    def check_receipt_amount(self, data):
        val = Decimal(data['amount'])
        if not val:
            raise ActionNotAllowedError("Receipt with amount '%s' can't be enrolled" % val)

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    @detalize_error(ActionNotAllowedError, RequestProcessingError.Category.data_integrity, 'amount')
    def enroll_receipt(self, data, operator, curs=None):
        c_id = data['customer_id']
        balance = selector.get_balance(curs, operator, c_id, for_update=True)
        currency = selector.get_currency_by_balance(curs, balance)

        amount_fields = ['amount']
        prep_data = self._decimal_texts_to_cents(data, currency, amount_fields)
        self.check_receipt_amount(prep_data)
        receipt = Receipt(**prep_data)
        mapping.insert(curs, receipt)

        balance.available_real_amount += receipt.amount #IGNORE:E1101
        mapping.update(curs, balance)

        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_ids')
    def view_receipts(self, data, operator, curs=None):
#        receipts, total = self._view_objects(curs, data, operator, selector.get_receipts,
#            selector.get_receipts_count)
#        return response_ok(receipts=receipts, total=total)

#        balance = selector.get_balance(curs, operator, c_id)
#        currency = selector.get_currency_by_balance(curs, balance)
#        receipts =
#        f_params = data['filter_params']
#        p_params = data['paging_params']
#        balances = selector.get_balances(curs, operator, f_params, p_params)
#        total = selector.get_balances_count(curs, operator, f_params)

#
#        cond = Eq('customer_id', data['customer_id'])
#        date_filters = (
#            ('start_date', 'end_date', 'created_date'),
#        )
#        cond = And(cond, selector.get_date_filters(date_filters, data))
#
#        receipts, total = selector.select_receipts(curs, currency, cond, data['limit'], data['offset'])
        return response_ok(receipts=[], total=0)

#    # --- enroll bonus ---
#    @transaction()
#    @logged
#    @authentificate
#    def enroll_bonus(self, data, curs=None, billing_manager_id=None):
#        balance = selector.get_balance(curs, billing_manager_id, data['customer_id'],
#            active_only=True, for_update=True)
#        currency = selector.get_currency_by_balance(curs, balance)
#        data_copy = self.decimal_texts_to_cents(data, currency, ['amount'])
#
#        bonus = Bonus(**data_copy)
#        mapping.insert(curs, bonus)
#
#        balance.available_virtual_amount += bonus.amount #IGNORE:E1101
#        mapping.update(curs, balance)
#        return response_ok()
#
#    # --- lock ---
#    def _lock(self, billing_manager_id, data_list, curs):
#        for data in data_list:
#            balance = selector.get_balance(curs, billing_manager_id, data['customer_id'], active_only=True, for_update=True)
#            currency = selector.get_currency_by_balance(curs, balance)
#            data_copy = self.decimal_texts_to_cents(data, currency, ['amount'])
#            locks = compute_locks(currency, balance, data_copy['amount'])
#            del data_copy['amount']
#
#            lock = BalanceLock(
#                real_amount=locks['available_real_amount'],
#                virtual_amount=locks['available_virtual_amount'],
#                **data_copy
#            )
#            mapping.insert(curs, lock)
#
#            balance.available_real_amount -= lock.real_amount #IGNORE:E1101
#            balance.available_virtual_amount -= lock.virtual_amount #IGNORE:E1101
#            balance.locked_amount += lock.real_amount #IGNORE:E1101
#            balance.locked_amount += lock.virtual_amount #IGNORE:E1101
#            mapping.update(curs, balance)
#
#    @logged
#    @authentificate
#    def lock(self, data, curs=None, billing_manager_id=None):
#        """
#        data = {
#            'login': Text(),
#            'password': Text(),
#            'customer_id': Text(),
#            'product_id': Text(),
#            'amount': nonnegative_amount_validator
#        }
#        """
#        self._lock(billing_manager_id, [data], curs)
#        return response_ok()
#
#    @transaction()
#    @logged_bulk
#    @authentificate
#    def lock_list(self, data, curs=None, billing_manager_id=None):
#        """
#        data = {
#            'login': Text(),
#            'password': Text(),
#            'locks': [
#                {'customer_id': Text(), 'product_id': Text()}
#                ...
#            ]
#        }
#        """
#        self._lock(billing_manager_id, data['locks'], curs)
#        return response_ok()
#
#    def _unlock(self, billing_manager_id, data_list, curs=None):
#        balances = {}
#        # locking all balances
#        for data in data_list:
#            balance = selector.get_balance(curs, billing_manager_id, data['customer_id'],
#                active_only=True, for_update=True)
#            balances[balance.customer_id] = balance
#
#        for data in data_list:
#            try:
#                lock = selector.try_get_lock(curs, data['customer_id'], data['product_id'], for_update=True)
#            except EmptyResultSetError:
#                raise ActionNotAllowedError(
#                    'Cannot unlock money for product %s: '
#                    'amount was not locked for this product'
#                    % data['product_id']
#                )
#
#            mapping.delete(curs, lock)
#
#            balance = balances[lock.customer_id]
#            balance.available_real_amount += lock.real_amount
#            balance.available_virtual_amount += lock.virtual_amount
#            balance.locked_amount -= lock.real_amount #IGNORE:E1101
#            balance.locked_amount -= lock.virtual_amount #IGNORE:E1101
#
#            mapping.update(curs, balance)
#
#    @transaction()
#    @logged
#    @authentificate
#    def unlock(self, data, curs=None, billing_manager_id=None):
#        """
#        data = {
#            'login': Text(),
#            'password': Text(),
#            'customer_id': Text(),
#            'product_id': Text(),
#        }
#        """
#        self._unlock(billing_manager_id, [data], curs)
#        return response_ok()
#
#    @transaction()
#    @logged_bulk
#    @authentificate
#    def unlock_list(self, data, curs=None, billing_manager_id=None):
#        """
#        data = {
#            'login': Text(),
#            'password': Text(),
#            'unlocks': [
#                {'customer_id': Text(), 'product_id': Text(),}
#                ...
#            ]
#        }
#        """
#        self._unlock(billing_manager_id, data['unlocks'], curs)
#        return response_ok()
#
#    def _chargeoff(self, billing_manager_id, data_list, curs=None):
#        balances = {}
#        for data in data_list:
#            balance = selector.get_balance(curs, billing_manager_id,
#                data['customer_id'], active_only=True, for_update=True)
#            balances[balance.customer_id] = balance
#
#        for data in data_list:
#            try:
#                lock = selector.try_get_lock(curs, data['customer_id'], data['product_id'], for_update=True)
#            except EmptyResultSetError:
#                raise ActionNotAllowedError(
#                    'Cannot charge off money for product %s: '
#                    'amount was not locked for this product'
#                    % data['product_id']
#                )
#
#            chargeoff = ChargeOff(locked_date=lock.locked_date,
#                real_amount=lock.real_amount, virtual_amount=lock.virtual_amount, **data)
#
#            mapping.delete(curs, lock)
#            mapping.insert(curs, chargeoff)
#
#            balance.locked_amount -= lock.real_amount #IGNORE:E1101
#            balance.locked_amount -= lock.virtual_amount #IGNORE:E1101
#
#            mapping.update(curs, balance)
#
#    @transaction()
#    @logged
#    @authentificate
#    def chargeoff(self, data, curs=None, billing_manager_id=None):
#        """
#        data = {
#            'login': Text(),
#            'password': Text(),
#            'customer_id': Text(),
#            'product_id': Text(),
#            'amount': (positive int, non negative int)
#        }
#        """
#        self._chargeoff(billing_manager_id, [data], curs)
#        return response_ok()
#
#    @transaction()
#    @logged_bulk
#    @authentificate
#    def chargeoff_list(self, data, curs=None, billing_manager_id=None):
#        """
#        data = {
#            'login': Text(),
#            'password': Text(),
#            'chargeoffs': [
#                {'customer_id': Text(), 'product_id': Text(), 'amount': (positive int, non negative int)}
#                ...
#            ]
#        }
#        """
#        self._chargeoff(billing_manager_id, data['chargeoffs'], curs)
#        return response_ok()
#
#    #view operations
#
#    @transaction()
#    @authentificate
#    def product_status(self, data, curs=None, billing_manager_id=None):
#        balance = selector.get_balance(curs, billing_manager_id, data['customer_id'],
#            active_only=False, for_update=False)
#        currency = selector.get_currency_by_balance(curs, balance)
#
#        response = {'product_status': product_status.unknown}
#        try:
#            lock = selector.try_get_lock(curs, data['customer_id'], data['product_id'], for_update=False)
#            response['product_status'] = product_status.locked
#            response['locked_date'] = lock.locked_date
#            response['real_amount'] = decompose_amount(currency, lock.real_amount)
#            response['virtual_amount'] = decompose_amount(currency, lock.virtual_amount)
#        except EmptyResultSetError: #IGNORE:W0704
#            pass
#
#        try:
#            chargeoff = selector.try_get_chargeoff(curs, data['customer_id'], data['product_id'], for_update=False)
#            response['product_status'] = product_status.charged_off
#            response['locked_date'] = chargeoff.locked_date
#            response['chargeoff_date'] = chargeoff.chargeoff_date
#            response['real_amount'] = decompose_amount(currency, chargeoff.real_amount)
#            response['virtual_amount'] = decompose_amount(currency, chargeoff.virtual_amount)
#        except EmptyResultSetError: #IGNORE:W0704
#            pass
#        return response_ok(**response)
#
#    @transaction()
#    @authentificate
#    def view_bonuses(self, data, curs=None, billing_manager_id=None):
#        balance = selector.get_balance(curs, billing_manager_id, data['customer_id'], active_only=False)
#        currency = selector.get_currency_by_balance(curs, balance)
#
#        cond = Eq('customer_id', data['customer_id'])
#        date_filters = (
#            ('start_date', 'end_date', 'created_date'),
#        )
#        cond = And(cond, selector.get_date_filters(date_filters, data))
#
#        bonuses, total = selector.select_bonuses(curs, currency, cond, data['limit'], data['offset'])
#        return response_ok(bonuses=bonuses, total=total)
#
#    @transaction()
#    @authentificate
#    def view_chargeoffs(self, data, curs=None, billing_manager_id=None):
#        balance = selector.get_balance(curs, billing_manager_id, data['customer_id'], active_only=False)
#        currency = selector.get_currency_by_balance(curs, balance)
#
#        cond = Eq('customer_id', data['customer_id'])
#        if 'product_id' in data:
#            cond = And(cond, Eq('product_id', data['product_id']))
#
#        date_filters = (
#            ('locked_start_date', 'locked_end_date', 'locked_date'),
#            ('chargeoff_start_date', 'chargeoff_end_date', 'chargeoff_date'),
#        )
#        cond = And(cond, selector.get_date_filters(date_filters, data))
#
#        chargeoffs, total = selector.select_chargeoffs(curs, currency, cond, data['limit'], data['offset'])
#        return response_ok(chargeoffs=chargeoffs, total=total)
#
#    @transaction()
#    @authentificate
#    def view_balance_locks(self, data, curs=None, billing_manager_id=None):
#        balance = selector.get_balance(curs, billing_manager_id, data['customer_id'], active_only=False)
#        currency = selector.get_currency_by_balance(curs, balance)
#
#        cond = Eq('customer_id', data['customer_id'])
#        if 'product_id' in data:
#            cond = And(cond, Eq('product_id', data['product_id']))
#
#        date_filters = (
#            ('locked_start_date', 'locked_end_date', 'locked_date'),
#        )
#        cond = And(cond, selector.get_date_filters(date_filters, data))
#
#        balance_locks, total = selector.select_balance_locks(curs, currency, cond, data['limit'], data['offset'])
#        return response_ok(balance_locks=balance_locks, total=total)
