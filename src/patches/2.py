def apply(curs):  #IGNORE:W0622
    print 'Creating table billing_manager'
    curs.execute(
    '''
        CREATE TABLE billing_manager (
            id serial,
            login varchar NOT NULL,
            password varchar NOT NULL,
            PRIMARY KEY(id),
            UNIQUE(login)
        )
    ''')


def revert(curs):
    print 'Dropping table billing_manager'
    curs.execute('DROP TABLE billing_manager')
