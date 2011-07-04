from decimal import Decimal
from functools import wraps, partial

from helixcore import mapping
from helixcore import error_code
from helixcore.actions.handler import (AbstractHandler, detalize_error,
    set_subject_users_ids)
from helixcore.db.filters import build_index
from helixcore.db.wrapper import ObjectNotFound, ObjectCreationError
from helixcore.mapping.objects import deserialize_field
from helixcore.server.response import response_ok
from helixcore.security import Session
from helixcore.security.auth import CoreAuthenticator

from helixbilling.conf import settings
from helixbilling.conf.db import transaction
from helixbilling.db.dataobject import (UsedCurrency, Balance, Transaction,
    BalanceLock)
from helixbilling.db.filters import (CurrencyFilter, UsedCurrencyFilter,
    ActionLogFilter, BalanceFilter, BalanceLockFilter, TransactionsFilter)
from helixbilling.error import (CurrencyNotFound, UsedCurrencyNotFound,
    UserNotExists, UserCheckingError, BalanceAlreadyExists, BalanceNotFound,
    BalanceDisabled, HelixbillingError, MoneyNotEnough, BalanceLockNotFound)
from helixbilling.logic import (decimal_texts_to_cents, cents_to_decimal,
    decimal_to_cents, compute_locks)


def _add_log_info(data, session, custom_actor_info=None):
    data['actor_user_id'] = session.user_id
    data['environment_id'] = session.environment_id
    data['session_id'] = session.session_id
    if custom_actor_info:
        data['custom_actor_info'] = custom_actor_info


def authenticate(method):
    @wraps(method)
    def decroated(self, data, curs):
        auth = CoreAuthenticator(settings.auth_server_url)
        session_id = data['session_id']
        custom_actor_info = data.pop('custom_actor_info', None)
        resp = auth.check_access(session_id, 'billing', method.__name__)
        if resp.get('status') == 'ok':
            session = Session(session_id, '%s' % resp['environment_id'],
                '%s' % resp['user_id'])
            if resp.get('access') == 'granted':
                try:
                    result = method(self, data, session, curs=curs)
                except Exception, e:
                    data['environment_id'] = session.environment_id
                    _add_log_info(data, session, custom_actor_info)
                    raise e
            else:
                result = {'status': 'error', 'code': error_code.HELIX_AUTH_ERROR,
                    'message': 'Access denied'}
            _add_log_info(data, session, custom_actor_info)
        return result
    return decroated


class Handler(AbstractHandler):
    '''
    Handles all API actions. Method names are called like actions.
    '''

    def ping(self, data): #IGNORE:W0613
        return response_ok()

    def login(self, data):
        auth = CoreAuthenticator(settings.auth_server_url)
        resp = auth.login(data)
        return resp

    def logout(self, data):
        auth = CoreAuthenticator(settings.auth_server_url)
        resp = auth.logout(data)
        return resp

    def _currencies_info(self, currencies):
        def viewer(currency):
            return {
                'id': currency.id,
                'code': currency.code,
                'cent_factor': currency.cent_factor,
                'name': currency.name,
                'location': currency.location,
            }
        return self.objects_info(currencies, viewer)

    @transaction()
    @authenticate
    def get_currencies(self, data, session, curs=None):
        f = CurrencyFilter({}, {}, data.get('ordering_params'))
        currencies = f.filter_objs(curs)
        def viewer(currency):
            return {
                'id': currency.id,
                'code': currency.code,
                'cent_factor': currency.cent_factor,
                'name': currency.name,
                'location': currency.location,
            }
        return response_ok(currencies=self._currencies_info(currencies))

    @transaction()
    @authenticate
    def get_used_currencies(self, data, session, curs=None):
        f = CurrencyFilter({}, {}, data.get('ordering_params'))
        currs = f.filter_objs(curs)
        f = UsedCurrencyFilter(session, {}, {}, None)
        try:
            u_currs = f.filter_one_obj(curs)
            u_currs_ids = u_currs.currencies_ids
        except ObjectNotFound:
            u_currs_ids = []
        filtered_currs = [curr for curr in currs if curr.id in u_currs_ids]
        return response_ok(currencies=self._currencies_info(filtered_currs))

    @transaction()
    @authenticate
    @detalize_error(CurrencyNotFound, 'new_currencies_codes')
    def modify_used_currencies(self, data, session, curs=None):
        f = CurrencyFilter({}, {}, None)
        currs = f.filter_objs(curs)
        currs_code_idx = build_index(currs, idx_field='code')
        new_currs_codes = data.pop('new_currencies_codes', [])

        for curr_code in new_currs_codes:
            if curr_code not in currs_code_idx:
                raise CurrencyNotFound(code=curr_code)

        new_currs_ids = [curr.id for curr in currs if curr.code in new_currs_codes]
        data['new_currencies_ids'] = new_currs_ids
        f = UsedCurrencyFilter(session, {}, {}, None)
        try:
            loader = partial(f.filter_one_obj, curs, for_update=True)
            self.update_obj(curs, data, loader)
        except ObjectNotFound:
            u_currs = UsedCurrency(environment_id=session.environment_id,
                currencies_ids=new_currs_ids)
            mapping.save(curs, u_currs)
        return response_ok()

    @transaction()
    @authenticate
    def get_action_logs(self, data, session, curs=None):
        return self._get_action_logs(data, session, curs)

    @transaction()
    @authenticate
    def get_action_logs_self(self, data, session, curs=None):
        data['filter_params']['user_id'] = session.user_id
        return self._get_action_logs(data, session, curs)

    def _get_action_logs(self, data, session, curs):
        f_params = data['filter_params']
        u_id = f_params.pop('user_id', None)
        if u_id:
            f_params[('subject_users_ids', 'actor_user_id')] = (u_id, u_id)
        f = ActionLogFilter(session.environment_id, f_params,
            data['paging_params'], data.get('ordering_params'))
        action_logs, total = f.filter_counted(curs)
        def viewer(obj):
            result = obj.to_dict()
            result.pop('environment_id', None)
            result['request_date'] = '%s' % result['request_date']
            return result
        return response_ok(action_logs=self.objects_info(action_logs, viewer),
            total=total)

    @transaction()
    @authenticate
    def get_transactions(self, data, session, curs=None):
        return self._get_transactions(data, session, curs)

    def _get_transactions(self, data, session, curs):
        f = TransactionsFilter(session.environment_id, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        transactions, total = f.filter_counted(curs)
        def viewer(trn):
            result = deserialize_field(trn.to_dict(), 'serialized_info', 'info')
            result.pop('environment_id', None)
            result['creation_date'] = '%s' % result['creation_date']
            result['real_amount'] = '%s' % trn.real_amount
            result['virtual_amount'] = '%s' % trn.virtual_amount
            return result
        return response_ok(transactions=self.objects_info(transactions, viewer),
            total=total)

    def _check_user_exist(self, session, user_id):
        auth = CoreAuthenticator(settings.auth_server_url)
        resp = auth.check_user_exist(session.session_id, user_id)
        if resp['status'] == 'ok':
            if resp['exist'] == True:
                pass
            else:
                raise UserNotExists('User %s not exists' % user_id)
        else:
            raise UserCheckingError(resp.get('message'))

    @set_subject_users_ids('user_id')
    @transaction()
    @authenticate
    @detalize_error(CurrencyNotFound, 'currency_code')
    @detalize_error(UsedCurrencyNotFound, 'currency_code')
    @detalize_error(ObjectCreationError, ['user_id', 'currency_code'])
    @detalize_error(UserCheckingError, 'user_id')
    @detalize_error(UserNotExists, 'user_id')
    def add_balance(self, data, session, curs=None):
        user_id = data['user_id']
        check_user_exist = data.get('check_user_exist', False)
        if check_user_exist:
            self._check_user_exist(session, user_id)
        currs_code_idx = self._get_currs_idx(curs, 'code')
        curr_code = data['currency_code']
        if curr_code not in currs_code_idx:
            raise CurrencyNotFound(currency_code=curr_code)
        curr = currs_code_idx[curr_code]

        try:
            u_curr_f = UsedCurrencyFilter(session, {}, {}, None)
            u_currs = u_curr_f.filter_one_obj(curs)
            u_currs_ids = u_currs.currencies_ids
        except ObjectNotFound:
            u_currs_ids = []

        if curr.id not in u_currs_ids:
            raise UsedCurrencyNotFound(currency_code=curr_code)

        b_data = dict(data)
        b_data.pop('currency_code', None)
        b_data.pop('session_id', None)
        b_data.pop('check_user_exist', None)
        b_data.pop('subject_users_ids', None)

        locking_order = b_data.get('locking_order')
        if locking_order is None:
            b_data['locking_order'] = ['real_amount', 'virtual_amount']

        b_data['environment_id'] = session.environment_id
        b_data['currency_id'] = curr.id
        amount_fields = ['overdraft_limit']
        balance = Balance(**decimal_texts_to_cents(b_data, curr, amount_fields))
        try:
            mapping.insert(curs, balance)
        except ObjectCreationError:
            raise BalanceAlreadyExists()
        return response_ok(id=balance.id)

    @set_subject_users_ids('users_ids')
    @transaction()
    @authenticate
    def modify_balances(self, data, session, curs=None):
        balances_ids = data['ids']
        currency_f = CurrencyFilter({}, {}, None)
        currencies = currency_f.filter_objs(curs)
        currencies_id_idx = build_index(currencies, 'id')

        balance_f = BalanceFilter(session, {'ids': balances_ids}, {}, None)
        balances = balance_f.filter_objs(curs)

        # Setting users ids for logging
        users_ids = [balance.user_id for balance in balances]
        data['users_ids'] = users_ids

        # Handling different currencies for different balances
        new_overdraft_limit = data.pop('new_overdraft_limit', None)
        def loader():
            if new_overdraft_limit is not None:
                for b in balances:
                    d = {'new_overdraft_limit': new_overdraft_limit}
                    amount_fields = ['new_overdraft_limit']
                    currency = currencies_id_idx[b.currency_id]
                    d = decimal_texts_to_cents(d, currency, amount_fields)
                    b.overdraft_limit = d['new_overdraft_limit']
            return balances

        self.update_objs(curs, data, loader)
        return response_ok()

    def _get_currs_idx(self, curs, idx_field):
        curr_f = CurrencyFilter({}, {}, None)
        currs = curr_f.filter_objs(curs)
        return build_index(currs, idx_field=idx_field)

    def _get_balances(self, curs, balance_f):
        balances, total = balance_f.filter_counted(curs)
        currs_id_idx = self._get_currs_idx(curs, 'id')

        def viewer(balance):
            currency = currs_id_idx[balance.currency_id]
            return {
                'id': balance.id,
                'user_id': balance.user_id,
                'is_active': balance.is_active,
                'currency_code': currency.code,
                'real_amount': '%s' % cents_to_decimal(currency, balance.real_amount),
                'virtual_amount': '%s' % cents_to_decimal(currency, balance.virtual_amount),
                'overdraft_limit': '%s' % cents_to_decimal(currency, balance.overdraft_limit),
                'locked_amount': '%s' % cents_to_decimal(currency, balance.locked_amount),
                'locking_order': balance.locking_order,
            }
        return response_ok(balances=self.objects_info(balances, viewer), total=total)

    @transaction()
    @authenticate
    def get_balances_self(self, data, session, curs=None):
        balance_f = BalanceFilter(session, {'user_id': session.user_id}, {},
            ['-currency_id'])
        return self._get_balances(curs, balance_f)

    @transaction()
    @authenticate
    def get_balances(self, data, session, curs=None):
        f_params = data['filter_params']
        self._f_param_currecncy_code_to_id(curs, f_params)

        balance_f = BalanceFilter(session, f_params,
            data['paging_params'], data.get('ordering_params'))
        return self._get_balances(curs, balance_f)

    def _get_active_balance(self, session, curs, data, log_user_id=True, for_update=True):
        balance_f = BalanceFilter(session, {'id': data['balance_id']}, {}, None)
        balance = balance_f.filter_one_obj(curs, for_update=for_update)
        if log_user_id:
            # setting user_id for correct action logging
            data['user_id'] = balance.user_id
        if not balance.is_active:
            raise BalanceDisabled()
        else:
            return balance

    def _make_income_transaction(self, curs, data, session, transaction_type):
        balance = self._get_active_balance(session, curs, data)

        currs_id_idx = self._get_currs_idx(curs, 'id')
        currency = currs_id_idx[balance.currency_id]

        amount_dec = Decimal(data['amount'])
        amount = decimal_to_cents(currency, amount_dec)
        enrolled_amount_dec = cents_to_decimal(currency, amount)

        if amount < 0:
            amount *= -1

        trans_data = {'environment_id': session.environment_id,
            'user_id': balance.user_id, 'balance_id': balance.id,
            'currency_code': currency.code, 'real_amount': 0, 'virtual_amount': 0,
            'type': transaction_type, 'info': data.get('info', {})}

        if transaction_type == 'receipt':
            balance.real_amount += amount
            trans_data['real_amount'] = enrolled_amount_dec
        elif transaction_type == 'bonus':
            balance.virtual_amount += amount
            trans_data['virtual_amount'] = enrolled_amount_dec
        else:
            raise HelixbillingError('Unhandled income transaction type: %s' %
                transaction_type)
        mapping.update(curs, balance)

        trans = Transaction(**trans_data)
        mapping.insert(curs, trans)
        return trans.id

    @set_subject_users_ids('user_id')
    @transaction()
    @authenticate
    @detalize_error(BalanceNotFound, 'balance_id')
    @detalize_error(BalanceDisabled, 'balance_id')
    def add_receipt(self, data, session, curs=None):
        trans_id = self._make_income_transaction(curs, data, session, 'receipt')
        return response_ok(transaction_id=trans_id)

    @set_subject_users_ids('user_id')
    @transaction()
    @authenticate
    @detalize_error(BalanceNotFound, 'balance_id')
    @detalize_error(BalanceDisabled, 'balance_id')
    def add_bonus(self, data, session, curs=None):
        trans_id = self._make_income_transaction(curs, data, session, 'bonus')
        return response_ok(transaction_id=trans_id)

    @set_subject_users_ids('user_id')
    @transaction()
    @authenticate
    @detalize_error(BalanceNotFound, 'balance_id')
    @detalize_error(BalanceDisabled, 'balance_id')
    @detalize_error(MoneyNotEnough, 'amount')
    def lock(self, data, session, curs=None):
        balance = self._get_active_balance(session, curs, data)

        currs_id_idx = self._get_currs_idx(curs, 'id')
        currency = currs_id_idx[balance.currency_id]

        lock_amount_dec = Decimal(data['amount'])
        lock_amount = decimal_to_cents(currency, lock_amount_dec)

        if lock_amount < 0:
            lock_amount *= -1

        amounts_to_lock = compute_locks(balance, lock_amount)
        lock_real = amounts_to_lock.get('real_amount', 0)
        lock_virtual = amounts_to_lock.get('virtual_amount', 0)
        info = data.get('info', {})

        trans_data = {'environment_id': session.environment_id, 'user_id': balance.user_id,
            'balance_id': balance.id, 'currency_code': currency.code,
            'type': 'lock', 'real_amount': cents_to_decimal(currency, lock_real),
            'virtual_amount': cents_to_decimal(currency, lock_virtual),
            'info': info}
        lock_data = {'environment_id': session.environment_id, 'user_id': balance.user_id,
            'balance_id': balance.id, 'real_amount': lock_real,
            'currency_id': currency.id, 'virtual_amount': lock_virtual, 'info': info}

        lock = BalanceLock(**lock_data)
        balance.real_amount -= lock_real
        balance.virtual_amount -= lock_virtual
        balance.locked_amount += lock_real + lock_virtual
        mapping.update(curs, balance)

        trans = Transaction(**trans_data)
        mapping.insert(curs, lock)
        mapping.insert(curs, trans)
        return response_ok(transaction_id=trans.id, lock_id=lock.id)

    def _process_lock(self, session, curs, data, operation, balance_updater):
        lock_f = BalanceLockFilter(session, {'id': data['lock_id'],
            'balance_id': data['balance_id']}, {}, None)
        lock = lock_f.filter_one_obj(curs)

        balance = self._get_active_balance(session, curs, data)

        currs_id_idx = self._get_currs_idx(curs, 'id')
        currency = currs_id_idx[balance.currency_id]

        info = data.get('info', {})

        trans_data = {'environment_id': session.environment_id, 'user_id': balance.user_id,
            'balance_id': balance.id, 'currency_code': currency.code,
            'type': operation, 'real_amount': cents_to_decimal(currency, lock.real_amount),
            'virtual_amount': cents_to_decimal(currency, lock.virtual_amount),
            'info': info}

        balance_updater(balance, lock)
        mapping.update(curs, balance)

        trans = Transaction(**trans_data)
        mapping.delete(curs, lock)
        mapping.insert(curs, trans)
        return response_ok(transaction_id=trans.id)

    @set_subject_users_ids('user_id')
    @transaction()
    @authenticate
    @detalize_error(BalanceLockNotFound, ['lock_id', 'balance_id'])
    @detalize_error(BalanceNotFound, 'balance_id')
    @detalize_error(BalanceDisabled, 'balance_id')
    def unlock(self, data, session, curs=None):
        def balance_updater(balance, lock):
            balance.real_amount += lock.real_amount
            balance.virtual_amount += lock.virtual_amount
            balance.locked_amount -= lock.real_amount + lock.virtual_amount
        return self._process_lock(session, curs, data, 'unlock', balance_updater)

    @set_subject_users_ids('user_id')
    @transaction()
    @authenticate
    @detalize_error(BalanceLockNotFound, ['lock_id', 'balance_id'])
    @detalize_error(BalanceNotFound, 'balance_id')
    @detalize_error(BalanceDisabled, 'balance_id')
    def charge_off(self, data, session, curs=None):
        def balance_updater(balance, lock):
            balance.locked_amount -= lock.real_amount + lock.virtual_amount
        return self._process_lock(session, curs, data, 'charge_off', balance_updater)

    def _f_param_currecncy_code_to_id(self, curs, f_params):
        if 'currency_code' in f_params:
            currency_code = f_params.pop('currency_code')
            currs_code_idx = self._get_currs_idx(curs, 'code')
            curr = currs_code_idx.get(currency_code)
            if curr:
                f_params['currency_id'] = curr.id
            else:
                f_params['currency_id'] = None

    def _get_balance_locks(self, curs, lock_f):
        locks, total = lock_f.filter_counted(curs)
        currs_id_idx = self._get_currs_idx(curs, 'id')

        def viewer(lock):
            currency = currs_id_idx[lock.currency_id]
            lock_info = deserialize_field(lock.to_dict(), 'serialized_info', 'info')
            return {
                'id': lock.id,
                'user_id': lock.user_id,
                'balance_id': lock.balance_id,
                'currency_code': currency.code,
                'creation_date': '%s' % lock.creation_date,
                'real_amount': '%s' % cents_to_decimal(currency, lock.real_amount),
                'virtual_amount': '%s' % cents_to_decimal(currency, lock.virtual_amount),
                'info': lock_info['info'],
            }
        return response_ok(locks=self.objects_info(locks, viewer), total=total)

    @transaction()
    @authenticate
    def get_locks(self, data, session, curs=None):
        f_params = data['filter_params']
        self._f_param_currecncy_code_to_id(curs, f_params)
        lock_f = BalanceLockFilter(session, f_params,
            data['paging_params'], data.get('ordering_params'))
        return self._get_balance_locks(curs, lock_f)

    @transaction()
    @authenticate
    def get_locks_self(self, data, session, curs=None):
        data['filter_params']['user_id'] = session.user_id
        f_params = data['filter_params']
        self._f_param_currecncy_code_to_id(curs, f_params)
        lock_f = BalanceLockFilter(session, f_params,
            data['paging_params'], data.get('ordering_params'))
        return self._get_balance_locks(curs, lock_f)
