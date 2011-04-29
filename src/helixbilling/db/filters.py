from helixcore.db.sql import Eq, MoreEq, LessEq, Any, In
from helixcore.db.filters import (InSessionFilter, ObjectsFilter,
    EnvironmentObjectsFilter)

from helixbilling.db.dataobject import (Currency, UsedCurrency, ActionLog,
    Balance)
from helixcore.db.wrapper import ObjectNotFound, SelectedMoreThanOneRow
from helixbilling.error import BalanceNotFound


class CurrencyFilter(ObjectsFilter):
    cond_map = [
        ('id', 'id', Eq),
    ]

    def __init__(self, filter_params, paging_params, ordering_params):
        super(CurrencyFilter, self).__init__(filter_params, paging_params,
            ordering_params, Currency)


class UsedCurrencyFilter(InSessionFilter):
    cond_map = [
        ('environment_id', 'environment_id', Eq),
    ]

    def __init__(self, session, filter_params, paging_params, ordering_params):
        super(UsedCurrencyFilter, self).__init__(session, filter_params,
            paging_params, ordering_params, UsedCurrency)


class ActionLogFilter(EnvironmentObjectsFilter):
    cond_map = [
        ('action', 'action', Eq),
        ('session_id', 'session_id', Eq),
        ('actor_user_id', 'actor_user_id', Eq),
        ('from_request_date', 'request_date', MoreEq),
        ('to_request_date', 'request_date', LessEq),
        # OR condition
        (('subject_users_ids', 'actor_user_id'),
            ('subject_users_ids', 'actor_user_id'), (Any, Eq)),
    ]

    def __init__(self, environment_id, filter_params, paging_params, ordering_params):
        super(ActionLogFilter, self).__init__(environment_id,
            filter_params, paging_params, ordering_params, ActionLog)


class BalanceFilter(InSessionFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('user_id', 'user_id', Eq),
        ('users_ids', 'users_id', In),
        ('is_active', 'is_active', Eq),
    ]

    def __init__(self, session, filter_params, paging_params, ordering_params):
        super(BalanceFilter, self).__init__(session, filter_params,
            paging_params, ordering_params, Balance)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(BalanceFilter, self).filter_one_obj(curs,
                for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise BalanceNotFound(**self.filter_params)

#
#class ReceiptFilter(ObjectsFilter):
#    cond_map = [
#        ('customer_id', 'customer_id', Eq),
#        ('customer_ids', 'customer_id', In),
#        ('from_creation_date', 'creation_date', MoreEq),
#        ('to_creation_date', 'creation_date', LessEq),
#    ]
#
#    def __init__(self, operator, filter_params, paging_params, ordering_params):
#        if ordering_params is None:
#            ordering_params = '-creation_date'
#        super(ReceiptFilter, self).__init__(operator, filter_params, paging_params,
#            ordering_params, Receipt)
#
#
#class BonusFilter(ObjectsFilter):
#    cond_map = [
#        ('customer_id', 'customer_id', Eq),
#        ('customer_ids', 'customer_id', In),
#        ('from_creation_date', 'creation_date', MoreEq),
#        ('to_creation_date', 'creation_date', LessEq),
#    ]
#
#    def __init__(self, operator, filter_params, paging_params, ordering_params):
#        if ordering_params is None:
#            ordering_params = '-creation_date'
#        super(BonusFilter, self).__init__(operator, filter_params, paging_params,
#            ordering_params, Bonus)
#
#
#class BalanceLockFilter(ObjectsFilter):
#    cond_map = [
#        ('customer_id', 'customer_id', Eq),
#        ('customer_ids', 'customer_id', In),
#        ('order_id', 'order_id', Eq),
#        ('order_ids', 'order_id', In),
#        ('order_type', 'order_type', Eq),
#        ('order_types', 'order_type', In),
#        ('from_locking_date', 'locking_date', MoreEq),
#        ('to_locking_date', 'locking_date', LessEq),
#    ]
#
#    def __init__(self, operator, filter_params, paging_params, ordering_params):
#        if ordering_params is None:
#            ordering_params = '-locking_date'
#        super(BalanceLockFilter, self).__init__(operator, filter_params, paging_params,
#            ordering_params, BalanceLock)
#
#
#class ChargeOffFilter(ObjectsFilter):
#    cond_map = [
#        ('customer_id', 'customer_id', Eq),
#        ('customer_ids', 'customer_id', In),
#        ('order_id', 'order_id', Eq),
#        ('order_ids', 'order_id', In),
#        ('order_type', 'order_type', Eq),
#        ('order_types', 'order_type', In),
#        ('from_locking_date', 'locking_date', MoreEq),
#        ('to_locking_date', 'locking_date', LessEq),
#        ('from_chargeoff_date', 'chargeoff_date', MoreEq),
#        ('to_chargeoff_date', 'chargeoff_date', LessEq),
#    ]
#
#    def __init__(self, operator, filter_params, paging_params, ordering_params):
#        if ordering_params is None:
#            ordering_params = '-chargeoff_date'
#        super(ChargeOffFilter, self).__init__(operator, filter_params, paging_params,
#            ordering_params, ChargeOff)
#
#
#class ActionLogFilter(ObjectsFilter):
#    cond_map = [
#        ('customer_id', 'customer_ids', Any),
#        ('action', 'action', Eq),
#        ('from_request_date', 'request_date', MoreEq),
#        ('to_request_date', 'request_date', LessEq),
#        ('remote_addr', 'remote_addr', Eq),
#    ]
#
#    def __init__(self, operator, filter_params, paging_params, ordering_params):
#        super(ActionLogFilter, self).__init__(operator, filter_params, paging_params,
#            ordering_params, ActionLog)
