from functools import partial

import helixcore.mapping.actions as mapping
from helixcore.db.wrapper import EmptyResultSetError, ObjectAlreadyExists
from helixcore.db.sql import Eq, And
from helixcore import utils
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
from helixbilling.logic.helper import cents_to_decimal, decimal_texts_to_cents
from helixbilling.logic.filters import BalanceFilter, ReceiptFilter, BonusFilter,\
    BalanceLockFilter


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

    def objects_info(self, objects, viewer):
        result = []
        for o in objects:
            result.append(viewer(o))
        return result

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
        balance = Balance(**decimal_texts_to_cents(data, currency, amount_fields))
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
        self.update_obj(curs, decimal_texts_to_cents(data, currency, amount_fields),
            partial(lambda x: x, balance))
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    def delete_balance(self, data, operator, curs=None):
        obj = selector.get_balance(curs, operator, data['customer_id'], for_update=True)
        mapping.delete(curs, obj)
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    def get_balance(self, data, operator, curs=None):
        c_id = data['customer_id']
        balance = selector.get_balance(curs, operator, c_id)
        currencies_idx = selector.get_currencies_indexed_by_id(curs)
        return response_ok(**self.balance_viewer(currencies_idx, balance))

    def balance_viewer(self, currencies_idx, balance):
        currency = currencies_idx[balance.currency_id]
        return {
            'customer_id': balance.customer_id,
            'active': balance.active,
            'currency_code': currency.code,
            'creation_date': '%s' % balance.creation_date.isoformat(),
            'available_real_amount': '%s' % cents_to_decimal(currency, balance.available_real_amount),
            'available_virtual_amount': '%s' % cents_to_decimal(currency, balance.available_virtual_amount),
            'overdraft_limit': '%s' % cents_to_decimal(currency, balance.overdraft_limit),
            'locked_amount': '%s' % cents_to_decimal(currency, balance.locked_amount),
            'locking_order': balance.locking_order,
        }

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    def view_balances(self, data, operator, curs=None):
        f = BalanceFilter(operator, data['filter_params'], data['paging_params'])
        balances, total = f.filter_counted(curs)
        currencies_idx = selector.get_currencies_indexed_by_id(curs)
        viewer = partial(self.balance_viewer, currencies_idx)
        return response_ok(balances=self.objects_info(balances, viewer), total=total)

    def check_amount_is_positive(self, data, f_name='amount'):
        val = Decimal(data[f_name])
        if val <= 0:
            raise ActionNotAllowedError("'%s' amount can't be processed" % val)

    def view_income_money(self, curs, data, operator, filter_cls):
        filter_params = data['filter_params']
        paging_params = data['paging_params']
        f = filter_cls(operator, filter_params, paging_params)
        objects, total = f.filter_counted(curs)

        filter_params = utils.filter_dict(('customer_ids', 'customer_id'), filter_params)
        balances = BalanceFilter(operator, filter_params, {}).filter_objs(curs)
        balances_c_id_idx = dict([(b.customer_id, b) for b in balances])
        currencies_idx = selector.get_currencies_indexed_by_id(curs)

        def viewer(obj):
            balance = balances_c_id_idx[obj.customer_id]
            currency = currencies_idx[balance.currency_id]
            return {
                'customer_id': obj.customer_id,
                'creation_date': obj.creation_date.isoformat(),
                'amount': '%s' % cents_to_decimal(currency, obj.amount),
                'currency': currency.code,
            }
        return (self.objects_info(objects, viewer), total)

    # --- receipt ---
    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    @detalize_error(ActionNotAllowedError, RequestProcessingError.Category.data_integrity, 'amount')
    def enroll_receipt(self, data, operator, curs=None):
        c_id = data['customer_id']
        balance = selector.get_balance(curs, operator, c_id, for_update=True)
        currency = selector.get_currency_by_balance(curs, balance)

        amount_fields = ['amount']
        prep_data = decimal_texts_to_cents(data, currency, amount_fields)
        self.check_amount_is_positive(prep_data)
        receipt = Receipt(**prep_data)
        mapping.insert(curs, receipt)

        balance.available_real_amount += receipt.amount #IGNORE:E1101
        mapping.update(curs, balance)
        return response_ok()

    @transaction()
    @authentificate
    def view_receipts(self, data, operator, curs=None):
        receipts, total = self.view_income_money(curs, data, operator, ReceiptFilter)
        return response_ok(receipts=receipts, total=total)

    # --- bonus ---
    @transaction()
    @authentificate
    def enroll_bonus(self, data, operator, curs=None):
        c_id = data['customer_id']
        balance = selector.get_balance(curs, operator, c_id, for_update=True)
        currency = selector.get_currency_by_balance(curs, balance)

        amount_fields = ['amount']
        prep_data = decimal_texts_to_cents(data, currency, amount_fields)
        self.check_amount_is_positive(prep_data)
        bonus = Bonus(**prep_data)
        mapping.insert(curs, bonus)

        balance.available_virtual_amount += bonus.amount #IGNORE:E1101
        mapping.update(curs, balance)
        return response_ok()

    @transaction()
    @authentificate
    def view_bonuses(self, data, operator, curs=None):
        bonuses, total = self.view_income_money(curs, data, operator, BonusFilter)
        return response_ok(bonuses=bonuses, total=total)

    # --- lock ---
    def _balance_lock(self, curs, operator, data_list):
        currencies_idx = selector.get_currencies_indexed_by_id(curs)
        c_ids = [d['customer_id'] for d in data_list]
        f = BalanceFilter(operator, {'customer_ids': c_ids}, {})
        # ordering by id excepts deadlocks
        balances = f.filter_objs(curs, for_update=True)
        balances_idx = dict([(b.customer_id, b) for b in balances])
        customers_no_balance = set(c_ids) - set(balances_idx.keys())
        if customers_no_balance:
            raise BalanceNotFound(', '.join(customers_no_balance))

        for data in data_list:
            c_id = data['customer_id']
            balance = balances_idx[c_id]
            currency = currencies_idx[balance.currency_id]
            self.check_amount_is_positive(data)

            cents_amount = decimal_to_cents(currency, Decimal(data['amount']))
            locks = compute_locks(currency, balance, cents_amount)
            lock = BalanceLock(**{'operator_id': operator.id, 'customer_id': c_id,
                'order_id': data['order_id'],
                'order_type': data.get('order_type'),
                'real_amount': locks.get('available_real_amount', 0),
                'virtual_amount': locks.get('available_virtual_amount', 0),
            })
            mapping.insert(curs, lock)

            balance.available_real_amount -= lock.real_amount #IGNORE:E1101
            balance.available_virtual_amount -= lock.virtual_amount #IGNORE:E1101
            balance.locked_amount += lock.real_amount #IGNORE:E1101
            balance.locked_amount += lock.virtual_amount #IGNORE:E1101
            mapping.update(curs, balance)

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    @detalize_error(ObjectAlreadyExists, RequestProcessingError.Category.data_integrity, 'product_id')
    @detalize_error(ActionNotAllowedError, RequestProcessingError.Category.data_integrity, 'amount')
    def balance_lock(self, data, operator, curs=None):
        self._balance_lock(curs, operator, [data])
        return response_ok()

    @transaction()
    @authentificate
    def balance_lock_list(self, data, operator, curs=None):
        self._balance_lock(curs, operator, data['locks'])
        return response_ok()

    @transaction()
    @authentificate
    def view_balance_locks(self, data, operator, curs=None):
        filter_params = data['filter_params']
        paging_params = data['paging_params']

        f = BalanceLockFilter(operator, filter_params, paging_params)
        balance_locks, total = f.filter_counted(curs)

        filter_params = utils.filter_dict(('customer_ids', 'customer_id'), filter_params)
        balances = BalanceFilter(operator, filter_params, {}).filter_objs(curs)
        balances_c_id_idx = dict([(b.customer_id, b) for b in balances])
        currencies_idx = selector.get_currencies_indexed_by_id(curs)

        def viewer(balance_lock):
            balance = balances_c_id_idx[balance_lock.customer_id]
            currency = currencies_idx[balance.currency_id]
            return {
                'customer_id': balance_lock.customer_id,
                'order_id': balance_lock.order_id,
                'order_type': balance_lock.order_type,
                'real_amount': '%s' % cents_to_decimal(currency, balance_lock.real_amount),
                'virtual_amount': '%s' % cents_to_decimal(currency, balance_lock.virtual_amount),
                'currency': currency.code,
                'locking_date': balance_lock.locking_date.isoformat(),
            }
        return response_ok(balance_locks=self.objects_info(balance_locks, viewer), total=total)
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
