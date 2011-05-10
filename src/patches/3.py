def apply(curs):
    print 'Creating table used_currency'
    curs.execute(
    '''
        CREATE TABLE used_currency (
            id serial,
            environment_id integer NOT NULL,
            currencies_ids integer[] DEFAULT ARRAY[]::integer[],
            UNIQUE(environment_id)
        )
    ''')


def revert(curs):
    print 'Dropping table used_currency'
    curs.execute('DROP TABLE IF EXISTS used_currency')
