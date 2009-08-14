import iso8601
import helixcore.db.query_builder as query_builder
from helixcore.db.cond import And, Eq, MoreEq, Less
from helixcore.db.wrapper import fetchall_dicts

from helixbilling.domain.objects import Receipt
from helixbilling.conf.log import logger

def select_receipts(curs, client_id, start_date_str=None, end_date_str=None):
    '''
    @param start_date_ts: string (ISO8601) of start date or None
    @param end_date_ts: string (ISO8601) of end date or None
    @return: list of receipt dicts.
    '''
    cond = Eq('client_id', client_id)
    if start_date_str is not None:
        cond = And(cond, MoreEq('created_date', iso8601.parse_date(start_date_str)))
    if end_date_str is not None:
        cond = And(cond, Less('created_date', iso8601.parse_date(end_date_str)))

    columns = ('client_id', 'created_date', 'amount')
    req, params = query_builder.select(Receipt.table, columns=columns, cond=cond, for_update=False, order_by='id')
    logger.debug("select_receipts: SQL: '%s', params: %s" % (req, params))

    curs.execute(req, params)
    return fetchall_dicts(curs)
