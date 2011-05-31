from helixcore import security
from helixcore.db.wrapper import ObjectNotFound, ObjectCreationError

from helixbilling import error_code


class HelixbillingError(Exception):
    code = error_code.HELIXBILLING_ERROR


class HelixbillingObjectNotFound(HelixbillingError, ObjectNotFound):
    def __init__(self, class_name, **kwargs):
        sanitized_kwargs = security.sanitize_credentials(kwargs)
        super(HelixbillingObjectNotFound, self).__init__('%s not found by params: %s' %
            (class_name, sanitized_kwargs))
        self.code = error_code.HELIXBILLING_OBJECT_NOT_FOUND


class HelixbillingObjectAlreadyExists(HelixbillingError, ObjectCreationError):
    def __init__(self, *args, **kwargs):
        super(HelixbillingObjectAlreadyExists, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXBILLING_OBJECT_ALREADY_EXISTS


class CurrencyNotFound(HelixbillingObjectNotFound):
    def __init__(self, **kwargs):
        super(CurrencyNotFound, self).__init__('Currency', **kwargs)


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
