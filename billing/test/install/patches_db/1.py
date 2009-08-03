from db.wrapper import transaction

@transaction()
def apply(curs=None):
    curs.execute('SELECT 1')

@transaction()
def revert(curs=None):
    curs.execute('SELECT 2')

