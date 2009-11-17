from functools import partial
import iso8601 #@UnresolvedImport

import helixcore.db.query_builder as query_builder
import helixcore.mapping.actions as mapping
from helixcore.db import sql
from helixcore.db.wrapper import fetchall_dicts, fetchone_dict, EmptyResultSetError
from helixcore.server.exceptions import DataIntegrityError, AuthError, ActionNotAllowedError

from helixbilling.domain.objects import Receipt, ChargeOff, BalanceLock, BillingManager, \
    Currency, Balance
from helixbilling.domain import security

import helper


def select(curs, MAPPED_CLASS, cond, limit, offset):
    '''
    @return: list of fetched dicts
    '''
    columns = list(MAPPED_CLASS.__slots__)
    columns.remove('id')
    req, params = query_builder.select(
        MAPPED_CLASS.table, columns=columns, cond=cond,
        limit=limit, offset=offset,
        order_by='id'
    )
    curs.execute(req, params)
    return fetchall_dicts(curs)


def _select_with_amount(curs, currency, cond, limit, offset, MAPPED_CLASS, AMOUNT_FIELDS):
    '''
    @return: tuple( list of receipt dicts, total_receipts_number )
    '''
    select_result = select(curs, MAPPED_CLASS, cond, limit, offset)
    dicts = decompose_amounts(select_result, currency, AMOUNT_FIELDS)
    count = get_count(curs, MAPPED_CLASS.table, cond)
    return (dicts, count)


select_receipts = partial(_select_with_amount, MAPPED_CLASS=Receipt, AMOUNT_FIELDS=['amount'])
select_chargeoffs = partial(_select_with_amount, MAPPED_CLASS=ChargeOff, AMOUNT_FIELDS=['real_amount', 'virtual_amount'])
select_balance_locks = partial(_select_with_amount, MAPPED_CLASS=BalanceLock, AMOUNT_FIELDS=['real_amount', 'virtual_amount'])


def get_count(curs, table, cond):
    req, params = query_builder.select(table, columns=[sql.Columns.COUNT_ALL], cond=cond)
    curs.execute(req, params)
    count_dict = fetchone_dict(curs)
    _, count = count_dict.popitem()
    return count


def decompose_amounts(dicts, currency, data_field_names):
    result = []
    for d in dicts:
        copy = dict(d)
        for data_field_name in data_field_names:
            copy[data_field_name] = helper.decompose_amount(currency, copy[data_field_name])
        result.append(copy)
    return result


def get_billing_manager(curs, id, for_update=False): #IGNORE:W0622
    return mapping.get_obj_by_field(curs, BillingManager, 'id', id, for_update)


def get_billing_manager_by_login(curs, login, for_update=False):
    return mapping.get_obj_by_field(curs, BillingManager, 'login', login, for_update)


def get_auth_billing_manager(curs, login, password, for_update=False):
    try:
        return mapping.get_obj_by_fields(curs, BillingManager,
            {'login': login, 'password': security.encrypt_password(password)}, for_update)
    except EmptyResultSetError:
        raise AuthError('Access denied.')


def get_currency_by_code(curs, code, for_update=False):
    try:
        return mapping.get_obj_by_field(curs, Currency, 'code', code, for_update)
    except EmptyResultSetError:
        raise DataIntegrityError('Currency  %s is not found' % code)


def get_currency_by_balance(curs, balance, for_update=False):
    return mapping.get_obj_by_field(curs, Currency, 'id', balance.id, for_update)


def get_balance(curs, client_id, active_only=True, for_update=False):
    try:
        balance = mapping.get_obj_by_field(curs, Balance, 'client_id', client_id, for_update)
        if active_only and balance.active == 0:
            raise ActionNotAllowedError('Balance of client %s is inactive' % client_id)
        return balance
    except EmptyResultSetError:
        raise DataIntegrityError('Balance of client %s is not found' % client_id)


def try_get_lock(curs, client_id, product_id, for_update=False):
    '''
    @return: BalanceLock on success, raises EmptyResultSetError if no such lock
    '''
    return mapping.get_obj_by_fields(curs, BalanceLock,
        {'client_id': client_id, 'product_id': product_id}, for_update)
#    except EmptyResultSetError:
#        raise DataIntegrityError(' of client %s is not found' % client_id)


def try_get_chargeoff(curs, client_id, product_id, for_update=False):
    '''
    @return: ChargeOff on success, raises EmptyResultSetError if no such charge-off
    '''
    return mapping.get_obj_by_fields(curs, ChargeOff,
        {'client_id': client_id, 'product_id': product_id}, for_update)


def get_date_filters(date_filters, data):
    '''
    adds date filtering parameters from data to cond.
    @param date_filters: is tuple of
        (start_date_filter_name, end_date_filter_name, db_filtering_field_name)
    @param data: dict of request data
    @return: db filtering condition
    '''
    cond = sql.NullLeaf()
    for start_date, end_date, db_field in date_filters:
        if start_date in data:
            cond = sql.And(cond, sql.MoreEq(db_field, iso8601.parse_date(data[start_date])))
        if end_date in data:
            cond = sql.And(cond, sql.Less(db_field, iso8601.parse_date(data[end_date])))
    return cond
