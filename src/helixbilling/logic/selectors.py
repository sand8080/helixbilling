import helixcore.db.query_builder as query_builder
from helixcore.db.wrapper import fetchall_dicts, fetchone_dict

from helixbilling.domain.objects import Receipt, ChargeOff, BalanceLock
from helixbilling.conf.log import logger

import helper

from functools import partial

def _select(curs, currency, cond, offset, limit, MAPPED_CLASS, FUNC_NAME, AMOUNT_FIELD):
    '''
    @return: tuple( list of receipt dicts, total_receipts_number )
    '''
    columns = list(MAPPED_CLASS.__slots__)
    columns.remove('id')
    req, params = query_builder.select(
        MAPPED_CLASS.table, columns=columns, cond=cond,
        limit=limit, offset=offset,
        order_by='id'
    )
    logger.debug(FUNC_NAME + ': SQL: "%s", params: %s' % (req, params))

    curs.execute(req, params)
    dicts = decompose_amounts(fetchall_dicts(curs), currency, AMOUNT_FIELD)
    logger.debug(FUNC_NAME +  ': result: %s' % str(dicts))

    count = get_count(curs, MAPPED_CLASS.table, cond)
    return (dicts, count)

select_receipts = partial(_select, MAPPED_CLASS=Receipt, FUNC_NAME='select_receipts', AMOUNT_FIELD='amount')
select_chargeoffs = partial(_select, MAPPED_CLASS=ChargeOff, FUNC_NAME='select_chargeoffs', AMOUNT_FIELD='amount')
select_balance_locks = partial(_select, MAPPED_CLASS=BalanceLock, FUNC_NAME='select_balance_locks', AMOUNT_FIELD='amount')

def get_count(curs, table, cond):
    req, params = query_builder.select(table, columns=[query_builder.Columns.COUNT_ALL], cond=cond)
    logger.debug('select from %s: count SQL: "%s", params: %s' % (table, req, params))
    curs.execute(req, params)
    count_dict = fetchone_dict(curs)
    _, count = count_dict.popitem()
    logger.debug('select from %s: count: %d' % (table, count))
    return count

def decompose_amounts(dicts, currency, data_field_name):
    result = []
    for d in dicts:
        copy = dict(d)
        copy[data_field_name] = helper.decompose_amount(currency, copy[data_field_name])
        result.append(copy)
    return result