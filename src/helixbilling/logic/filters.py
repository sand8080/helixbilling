from helixcore.db.sql import And, Eq, In, Select, Columns, MoreEq, LessEq
from helixcore.db.wrapper import SelectedMoreThanOneRow, fetchone_dict
import helixcore.mapping.actions as mapping

from helixbilling.domain.objects import Balance, Receipt, Bonus, BalanceLock
from helixbilling.error import ObjectNotFound, BalanceNotFound
from helixbilling.logic.helper import decimal_texts_to_cents


class ObjectsFilter(object):
    cond_map = []

    def __init__(self, operator, filter_params, paging_params, obj_class):
        self.operator = operator
        self.filter_params = filter_params
        self.paging_params = paging_params
        self.obj_class = obj_class

    def _cond_by_filter_params(self):
        cond = Eq('operator_id', self.operator.id)
        for p_name, db_f_name, c in self.cond_map:
            if p_name in self.filter_params:
                cond = And(cond, c(db_f_name, self.filter_params[p_name]))
        return cond

    def _get_paging_params(self):
        return self.paging_params.get('limit'), self.paging_params.get('offset', 0)

    def filter_objs(self, curs, for_update=False):
        cond = self._cond_by_filter_params()
        limit, offset = self._get_paging_params()
        return mapping.get_list(curs, self.obj_class, cond=cond, limit=limit,
            offset=offset, for_update=for_update)

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
        ('active', 'active', True),
    ]

    def __init__(self, operator, filter_params, paging_params):
        super(BalanceFilter, self).__init__(operator, filter_params, paging_params, Balance)

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

    def __init__(self, operator, filter_params, paging_params):
        super(ReceiptFilter, self).__init__(operator, filter_params, paging_params, Receipt)


class BonusFilter(ObjectsFilter):
    cond_map = [
        ('customer_id', 'customer_id', Eq),
        ('customer_ids', 'customer_id', In),
        ('from_creation_date', 'creation_date', MoreEq),
        ('to_creation_date', 'creation_date', LessEq),
    ]

    def __init__(self, operator, filter_params, paging_params):
        super(BonusFilter, self).__init__(operator, filter_params, paging_params, Bonus)


class BalanceLockFilter(ObjectsFilter):
    cond_map = [
        ('customer_id', 'customer_id', Eq),
        ('customer_ids', 'customer_id', In),
        ('from_locking_date', 'locking_date', MoreEq),
        ('to_locking_date', 'locking_date', LessEq),
    ]

    def __init__(self, operator, filter_params, paging_params):
        super(BalanceLockFilter, self).__init__(operator, filter_params, paging_params, BalanceLock)
