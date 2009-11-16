from functools import partial

import helixcore.db.query_builder as query_builder
import helixcore.mapping.actions as mapping
from helixcore.db import sql
from helixcore.db.wrapper import fetchall_dicts, fetchone_dict
from helixcore.server.exceptions import DataIntegrityError, AuthError

from helixbilling.domain.objects import Receipt, ChargeOff, BalanceLock, BillingManager
from helixbilling.domain import security
from helixbilling.conf.log import logger

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
    logger.debug('select from %s: count SQL: "%s", params: %s' % (table, req, params))
    curs.execute(req, params)
    count_dict = fetchone_dict(curs)
    _, count = count_dict.popitem()
    logger.debug('select from %s: count: %d' % (table, count))
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
    except DataIntegrityError:
        raise AuthError('Access denied.')
