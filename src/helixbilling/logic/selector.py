from functools import partial
import iso8601 #@UnresolvedImport

import helixcore.mapping.actions as mapping
from helixcore.db import sql
from helixcore.db.wrapper import (fetchall_dicts, fetchone_dict, EmptyResultSetError,
    SelectedMoreThanOneRow)
from helixcore.server.exceptions import (DataIntegrityError, AuthError)

from helixbilling.domain.objects import (Receipt, Bonus, ChargeOff, BalanceLock, Operator,
    Currency, Balance)

from helixbilling.logic import helper
from helixbilling.domain import security
from helixcore.db.sql import Eq, And, In, MoreEq, LessEq
from helixbilling.error import BalanceNotFound
from helixbilling.logic.filters import BalanceFilter


def select_data(curs, MAPPED_CLASS, cond, limit, offset):
    '''
    @return: list of fetched dicts
    '''
    columns = list(MAPPED_CLASS.__slots__)
    columns.remove('id')
    q = sql.Select(
        MAPPED_CLASS.table, columns=columns, cond=cond,
        limit=limit, offset=offset,
        order_by='id'
    )
    curs.execute(*q.glue())
    return fetchall_dicts(curs)


#def _select_with_amount(curs, currency, cond, limit, offset, MAPPED_CLASS, AMOUNT_FIELDS):
#    '''
#    @return: tuple( list of receipt dicts, total_receipts_number )
#    '''
#    select_result = select_data(curs, MAPPED_CLASS, cond, limit, offset)
#    dicts = decompose_amounts(select_result, currency, AMOUNT_FIELDS)
#    count = get_count(curs, MAPPED_CLASS.table, cond)
#    return (dicts, count)
#
#
#select_receipts = partial(_select_with_amount, MAPPED_CLASS=Receipt, AMOUNT_FIELDS=['amount'])
#select_bonuses = partial(_select_with_amount, MAPPED_CLASS=Bonus, AMOUNT_FIELDS=['amount'])
#select_chargeoffs = partial(_select_with_amount, MAPPED_CLASS=ChargeOff, AMOUNT_FIELDS=['real_amount', 'virtual_amount'])
#select_balance_locks = partial(_select_with_amount, MAPPED_CLASS=BalanceLock, AMOUNT_FIELDS=['real_amount', 'virtual_amount'])


def get_count(curs, table, cond):
    q = sql.Select(table, columns=[sql.Columns.COUNT_ALL], cond=cond)
    curs.execute(*q.glue())
    count_dict = fetchone_dict(curs)
    _, count = count_dict.popitem()
    return count


#def decompose_amounts(dicts, currency, data_field_names):
#    result = []
#    for d in dicts:
#        copy = dict(d)
#        for data_field_name in data_field_names:
#            copy[data_field_name] = helper.decompose_amount(currency, copy[data_field_name])
#        result.append(copy)
#    return result


def get_operator(curs, o_id, for_update=False): #IGNORE:W0622
    return mapping.get_obj_by_field(curs, Operator, 'id', o_id, for_update)


def get_operator_by_login(curs, login, for_update=False):
    return mapping.get_obj_by_field(curs, Operator, 'login', login, for_update)


def get_auth_opertator(curs, login, password, for_update=False):
    try:
        return mapping.get_obj_by_fields(curs, Operator,
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


def get_currencies(curs, for_update=False):
    return mapping.get_list(curs, Currency, None, for_update=for_update)


def get_currencies_indexed_by_id(curs):
    currencies = get_currencies(curs)
    return dict([(c.id, c) for c in currencies])


def get_balance(curs, operator, customer_id, for_update=False):
    return BalanceFilter(operator, {'customer_id': customer_id}, {}).filter_one_obj(curs, for_update=for_update)

#
#
#def get_balances(curs, operator, filter_params, paging_params, for_update=False):
#    cond = _balances_filtering_cond(operator, filter_params)
#    limit, offset = _get_paging_params(paging_params)
#    return mapping.get_list(curs, Balance, cond=cond, limit=limit, offset=offset, for_update=for_update)
#
#
#def get_balances_count(curs, operator, filter_params):
#    cond = _balances_filtering_cond(operator, filter_params)
#    return int(get_count(curs, Balance.table, cond))


#def get_balance(curs, operator, customer_id, for_update=False):
#    balances = get_balances(curs, operator, {'customer_ids': [customer_id]}, {}, for_update=for_update)
#    if len(balances) > 1:
#        raise SelectedMoreThanOneRow()
#    elif len(balances) == 0:
#        raise BalanceNotFound(customer_id)
#    else:
#        return balances[0]


#def _receipts_filtering_cond(operator, filter_params):
#    cond = Eq('operator_id', operator.id)
#    cond_map = [
#        ('customer_ids', 'customer_id', In),
#        ('from_creation_date', 'creation_date', MoreEq),
#        ('to_creation_date', 'creation_date', LessEq),
#    ]
#    return _cond_by_filter_params(cond, cond_map, filter_params)
#
#
#def get_receipts(curs, operator, filter_params, paging_params, for_update=False):
#    cond = _balances_filtering_cond(operator, filter_params)
#    limit, offset = _get_paging_params(paging_params)
#    return mapping.get_list(curs, Receipt, cond=cond, limit=limit, offset=offset, for_update=for_update)
#
#
#def get_receipts_count(curs, operator, filter_params):
#    cond = _balances_filtering_cond(operator, filter_params)
#    return int(get_count(curs, Receipt.table, cond))


def try_get_lock(curs, client_id, product_id, for_update=False):
    '''
    @return: BalanceLock on success, raises EmptyResultSetError if no such lock
    '''
    return mapping.get_obj_by_fields(curs, BalanceLock,
        {'client_id': client_id, 'product_id': product_id}, for_update)


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

