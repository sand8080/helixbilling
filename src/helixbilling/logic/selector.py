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
from helixbilling.error import BalanceNotFound, BalanceDisabled
from helixbilling.logic.filters import BalanceFilter, BalanceLockFilter,\
    ChargeOffFilter


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


def get_count(curs, table, cond):
    q = sql.Select(table, columns=[sql.Columns.COUNT_ALL], cond=cond)
    curs.execute(*q.glue())
    count_dict = fetchone_dict(curs)
    _, count = count_dict.popitem()
    return count


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


def get_active_balance(curs, operator, customer_id, for_update=False):
    balance = get_balance(curs, operator, customer_id, for_update)
    if balance.active is False:
        raise BalanceDisabled(customer_id)
    return balance


def get_balance_lock(curs, operator, customer_id, order_id, for_update=False):
    f = BalanceLockFilter(operator, {'customer_id': customer_id, 'order_id': order_id}, {})
    return f.filter_one_obj(curs, for_update=for_update)

def get_chargeoff(curs, operator, customer_id, order_id, for_update=False):
    f = ChargeOffFilter(operator, {'customer_id': customer_id, 'order_id': order_id}, {})
    return f.filter_one_obj(curs, for_update=for_update)

#def try_get_chargeoff(curs, client_id, product_id, for_update=False):
#    '''
#    @return: ChargeOff on success, raises EmptyResultSetError if no such charge-off
#    '''
#    return mapping.get_obj_by_fields(curs, ChargeOff,
#        {'client_id': client_id, 'product_id': product_id}, for_update)
#
#
#def get_date_filters(date_filters, data):
#    '''
#    adds date filtering parameters from data to cond.
#    @param date_filters: is tuple of
#        (start_date_filter_name, end_date_filter_name, db_filtering_field_name)
#    @param data: dict of request data
#    @return: db filtering condition
#    '''
#    cond = sql.NullLeaf()
#    for start_date, end_date, db_field in date_filters:
#        if start_date in data:
#            cond = sql.And(cond, sql.MoreEq(db_field, iso8601.parse_date(data[start_date])))
#        if end_date in data:
#            cond = sql.And(cond, sql.Less(db_field, iso8601.parse_date(data[end_date])))
#    return cond

