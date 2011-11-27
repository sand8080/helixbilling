from helixcore.db.sql import Eq, MoreEq, LessEq, Any, In, Like
from helixcore.db.filters import (InSessionFilter,
    EnvironmentObjectsFilter, CurrencyFilter) #@UnusedImport
from helixcore.db.wrapper import ObjectNotFound, SelectedMoreThanOneRow

from helixbilling.db.dataobject import (UsedCurrency, ActionLog,
    Balance, BalanceLock, Transaction)
from helixbilling.error import BalanceNotFound


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


class TransactionsFilter(EnvironmentObjectsFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('ids', 'id', In),
        ('user_id', 'user_id', Eq),
        ('balance_id', 'balance_id', Eq),
        ('type', 'type', Eq),
        ('order_id', 'order_id', Like),
        ('from_creation_date', 'creation_date', MoreEq),
        ('to_creation_date', 'creation_date', LessEq),
    ]

    def __init__(self, environment_id, filter_params, paging_params, ordering_params):
        super(TransactionsFilter, self).__init__(environment_id,
            filter_params, paging_params, ordering_params, Transaction)


class BalanceFilter(InSessionFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('ids', 'id', In),
        ('user_id', 'user_id', Eq),
        ('users_ids', 'user_id', In),
        ('is_active', 'is_active', Eq),
        ('currency_id', 'currency_id', Eq),
        ('from_real_amount', 'real_amount', MoreEq),
        ('to_real_amount', 'real_amount', LessEq),
        ('from_virtual_amount', 'virtual_amount', MoreEq),
        ('to_virtual_amount', 'virtual_amount', LessEq),
        ('from_overdraft_limit', 'overdraft_limit', MoreEq),
        ('to_overdraft_limit', 'overdraft_limit', LessEq),
        ('from_locked_amount', 'locked_amount', MoreEq),
        ('to_locked_amount', 'locked_amount', LessEq),
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


class BalanceLockFilter(InSessionFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('ids', 'id', In),
        ('user_id', 'user_id', Eq),
        ('order_id', 'order_id', Like),
        ('balance_id', 'balance_id', Eq),
        ('currency_id', 'currency_id', Eq),
        ('from_creation_date', 'creation_date', MoreEq),
        ('to_creation_date', 'creation_date', LessEq),
        ('from_real_amount', 'real_amount', MoreEq),
        ('to_real_amount', 'real_amount', LessEq),
        ('from_virtual_amount', 'virtual_amount', MoreEq),
        ('to_virtual_amount', 'virtual_amount', LessEq),
    ]

    def __init__(self, session, filter_params, paging_params, ordering_params):
        super(BalanceLockFilter, self).__init__(session, filter_params,
            paging_params, ordering_params, BalanceLock)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(BalanceLockFilter, self).filter_one_obj(curs,
                for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise BalanceNotFound(**self.filter_params)
