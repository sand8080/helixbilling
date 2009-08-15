import iso8601
import helixcore.db.query_builder as query_builder
from helixcore.db.cond import And, Eq, MoreEq, Less
from helixcore.db.wrapper import fetchall_dicts, fetchone_dict

from helixbilling.domain.objects import Receipt
from helixbilling.conf.log import logger

from helper import decompose_amount

def select_receipts(curs, currency, client_id, offset, limit, start_date_str=None, end_date_str=None):
    '''
    @param start_date_ts: string (ISO8601) of start date or None
    @param end_date_ts: string (ISO8601) of end date or None
    @return: tuple( list of receipt dicts, total_receipts_number )
    '''
    cond = Eq('client_id', client_id)
    if start_date_str is not None:
        cond = And(cond, MoreEq('created_date', iso8601.parse_date(start_date_str)))
    if end_date_str is not None:
        cond = And(cond, Less('created_date', iso8601.parse_date(end_date_str)))

    columns = ('client_id', 'created_date', 'amount')
    req, params = query_builder.select(Receipt.table, columns=columns, cond=cond, limit=limit, offset=offset, for_update=False, order_by='id')
    logger.debug("select_receipts: SQL: '%s', params: %s" % (req, params))

    curs.execute(req, params)
    dicts = fetchall_dicts(curs)

    for i in xrange(0, len(dicts)):
        dicts[i]['amount'] = decompose_amount(currency, dicts[i]['amount'])
    logger.debug("select_receipts: result: %s" % str(dicts))

    req, params = query_builder.select(Receipt.table, columns=[query_builder.Columns.COUNT_ALL], cond=cond)
    logger.debug("select_receipts: count SQL: '%s', params: %s" % (req, params))

    curs.execute(req, params)
    count_dict = fetchone_dict(curs)
    count = count_dict.popitem()[1]
    logger.debug("select_receipts: count: %d" % count)

    return (dicts, count)
