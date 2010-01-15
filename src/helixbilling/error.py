#from helixcore.db.wrapper import EmptyResultSetError


class HelixtbillingError(Exception):
    pass


class BalanceNotFound(HelixtbillingError):
    def __init__(self, client_id):
        super(BalanceNotFound, self).__init__('''Balance for client '%s' not found.''' % client_id)


