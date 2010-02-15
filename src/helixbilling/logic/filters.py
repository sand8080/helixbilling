from helixcore.db.sql import And, Eq, In, Select, Columns, MoreEq, LessEq, Any
from helixcore.db.wrapper import SelectedMoreThanOneRow, fetchone_dict
import helixcore.mapping.actions as mapping

from helixbilling.domain.objects import (Balance, Receipt, Bonus, BalanceLock,
    ChargeOff, ActionLog)
from helixbilling.error import ObjectNotFound, BalanceNotFound


class ObjectsFilter(object):
    cond_map = []

    def __init__(self, operator, filter_params, paging_params, ordering_params, obj_class):
        self.operator = operator
        self.filter_params = filter_params
        self.paging_params = paging_params
        self.ordering_params = ordering_params if ordering_params else 'id'
        self.obj_class = obj_class

    def _cond_by_filter_params(self):
        cond = Eq('operator_id', self.operator.id)
        for p_name, db_f_name, c in self.cond_map:
            if p_name in self.filter_params:
                if c == Any:
                    cond = And(cond, c(self.filter_params[p_name], db_f_name))
                else:
                    cond = And(cond, c(db_f_name, self.filter_params[p_name]))
        return cond

    def _get_paging_params(self):
        return self.paging_params.get('limit'), self.paging_params.get('offset', 0)

    def filter_objs(self, curs, for_update=False):
        cond = self._cond_by_filter_params()
        limit, offset = self._get_paging_params()
        return mapping.get_list(curs, self.obj_class, cond=cond, order_by=self.ordering_params,
            limit=limit, offset=offset, for_update=for_update)

    def filter_objs_count(self, curs):
        cond = self._cond_by_filter_params()
        q = Select(self.obj_class.table, columns=[Columns.COUNT_ALL], cond=cond)
        curs.execute(*q.glue())
        count_dict = fetchone_dict(curs)
        _, count = count_dict.popitem()
        return int(count)

    def filter_one_obj(self, curs, for_update=False):
        objs = self.filter_objs(curs, for_update=for_update)
        if len(objs) > 1:
            raise SelectedMoreThanOneRow
        elif len(objs) == 0:
            raise ObjectNotFound
        else:
            return objs[0]

    def filter_counted(self, curs):
        return self.filter_objs(curs), self.filter_objs_count(curs)


class BalanceFilter(ObjectsFilter):
    cond_map = [
        ('customer_id', 'customer_id', Eq),
        ('customer_ids', 'customer_id', In),
        ('active', 'active', Eq),
    ]

    def __init__(self, operator, filter_params, paging_params, ordering_params):
        super(BalanceFilter, self).__init__(operator, filter_params, paging_params,
            ordering_params, Balance)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(BalanceFilter, self).filter_one_obj(curs, for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise BalanceNotFound(self.filter_params.get('customer_id'))


class ReceiptFilter(ObjectsFilter):
    cond_map = [
        ('customer_id', 'customer_id', Eq),
        ('customer_ids', 'customer_id', In),
        ('from_creation_date', 'creation_date', MoreEq),
        ('to_creation_date', 'creation_date', LessEq),
    ]

    def __init__(self, operator, filter_params, paging_params, ordering_params):
        if ordering_params is None:
            ordering_params = '-creation_date'
        super(ReceiptFilter, self).__init__(operator, filter_params, paging_params,
            ordering_params, Receipt)


class BonusFilter(ObjectsFilter):
    cond_map = [
        ('customer_id', 'customer_id', Eq),
        ('customer_ids', 'customer_id', In),
        ('from_creation_date', 'creation_date', MoreEq),
        ('to_creation_date', 'creation_date', LessEq),
    ]

    def __init__(self, operator, filter_params, paging_params, ordering_params):
        if ordering_params is None:
            ordering_params = '-creation_date'
        super(BonusFilter, self).__init__(operator, filter_params, paging_params,
            ordering_params, Bonus)


class BalanceLockFilter(ObjectsFilter):
    cond_map = [
        ('customer_id', 'customer_id', Eq),
        ('customer_ids', 'customer_id', In),
        ('order_id', 'order_id', Eq),
        ('order_ids', 'order_id', In),
        ('order_type', 'order_type', Eq),
        ('order_types', 'order_type', In),
        ('from_locking_date', 'locking_date', MoreEq),
        ('to_locking_date', 'locking_date', LessEq),
    ]

    def __init__(self, operator, filter_params, paging_params, ordering_params):
        if ordering_params is None:
            ordering_params = '-locking_date'
        super(BalanceLockFilter, self).__init__(operator, filter_params, paging_params,
            ordering_params, BalanceLock)


class ChargeOffFilter(ObjectsFilter):
    cond_map = [
        ('customer_id', 'customer_id', Eq),
        ('customer_ids', 'customer_id', In),
        ('order_id', 'order_id', Eq),
        ('order_ids', 'order_id', In),
        ('order_type', 'order_type', Eq),
        ('order_types', 'order_type', In),
        ('from_locking_date', 'locking_date', MoreEq),
        ('to_locking_date', 'locking_date', LessEq),
        ('from_chargeoff_date', 'chargeoff_date', MoreEq),
        ('to_chargeoff_date', 'chargeoff_date', LessEq),
    ]

    def __init__(self, operator, filter_params, paging_params, ordering_params):
        if ordering_params is None:
            ordering_params = '-chargeoff_date'
        super(ChargeOffFilter, self).__init__(operator, filter_params, paging_params,
            ordering_params, ChargeOff)


class ActionLogFilter(ObjectsFilter):
    cond_map = [
        ('customer_id', 'customer_ids', Any),
        ('action', 'action', Eq),
        ('from_request_date', 'request_date', MoreEq),
        ('to_request_date', 'request_date', LessEq),
        ('remote_addr', 'remote_addr', Eq),
    ]

    def __init__(self, operator, filter_params, paging_params, ordering_params):
        super(ActionLogFilter, self).__init__(operator, filter_params, paging_params,
            ordering_params, ActionLog)
