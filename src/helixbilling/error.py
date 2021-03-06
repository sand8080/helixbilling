from helixcore.db.wrapper import ObjectCreationError
from helixcore.error import HelixcoreObjectNotFound

from helixbilling import error_code


class HelixbillingError(Exception):
    code = error_code.HELIXBILLING_ERROR


class HelixbillingObjectNotFound(HelixbillingError, HelixcoreObjectNotFound):
    def __init__(self, class_name, **kwargs):
        super(HelixbillingObjectNotFound, self).__init__(class_name, **kwargs)
        self.code = error_code.HELIXBILLING_OBJECT_NOT_FOUND


class HelixbillingObjectAlreadyExists(HelixbillingError, ObjectCreationError):
    def __init__(self, *args, **kwargs):
        super(HelixbillingObjectAlreadyExists, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXBILLING_OBJECT_ALREADY_EXISTS


class UsedCurrencyNotFound(HelixbillingObjectNotFound):
    def __init__(self, **kwargs):
        super(UsedCurrencyNotFound, self).__init__('UsedCurrency', **kwargs)


class UserNotExists(HelixbillingError):
    def __init__(self, *args, **kwargs):
        super(UserNotExists, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXBILLING_USER_NOT_EXISTS


class UserCheckingError(HelixbillingError):
    def __init__(self, *args, **kwargs):
        super(UserCheckingError, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXBILLING_USER_CHECKING_ERROR


class BalanceNotFound(HelixbillingObjectNotFound):
    def __init__(self, **kwargs):
        super(BalanceNotFound, self).__init__('Balance', **kwargs)
        self.code = error_code.HELIXBILLING_BALANCE_NOT_FOUND


class BalanceAlreadyExists(HelixbillingObjectAlreadyExists):
    def __init__(self, *args, **kwargs):
        super(BalanceAlreadyExists, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXBILLING_BALANCE_ALREADY_EXISTS


class BalanceDisabled(HelixbillingError):
    def __init__(self, **kwargs):
        super(BalanceDisabled, self).__init__('Balance disabled', **kwargs)
        self.code = error_code.HELIXBILLING_BALANCE_DISABLED


class MoneyNotEnough(HelixbillingError):
    def __init__(self, *args, **kwargs):
        super(MoneyNotEnough, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXBILLING_MONEY_NOT_ENOUGH


class BalanceLockNotFound(HelixbillingObjectNotFound):
    def __init__(self, **kwargs):
        super(BalanceLockNotFound, self).__init__('BalanceLock', **kwargs)
        self.code = error_code.HELIXBILLING_BALANCE_LOCK_NOT_FOUND
