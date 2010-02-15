from helixcore.server.exceptions import ActionNotAllowedError


class HelixbillingError(Exception):
    pass


class OperatorAlreadyExists(ActionNotAllowedError, HelixbillingError):
    pass


class ObjectNotFound(HelixbillingError):
    pass


class BalanceNotFound(ObjectNotFound):
    def __init__(self, customer_id):
        super(BalanceNotFound, self).__init__('Balance not found for customer %s' % customer_id)


class BalanceDisabled(ActionNotAllowedError):
    def __init__(self, customer_id):
        super(BalanceDisabled, self).__init__('Balance disabled for customer %s' % customer_id)


class CurrencyNotFound(ObjectNotFound):
    def __init__(self, currency):
        super(CurrencyNotFound, self).__init__('Currency %s not found' % currency)


class OperatorNotFound(ObjectNotFound):
    def __init__(self, client_id):
        super(OperatorNotFound, self).__init__("Operator '%s' not found" % client_id)
