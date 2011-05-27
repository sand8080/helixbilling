def apply(curs):
    print 'Creating table balance'
    curs.execute(
    '''
        CREATE TABLE balance (
            id serial,
            PRIMARY KEY(id),
            environment_id integer NOT NULL,
            is_active boolean NOT NULL DEFAULT True,
            user_id integer NOT NULL,
            currency_id int NOT NULL,
            FOREIGN KEY(currency_id) REFERENCES currency(id),
            real_amount NUMERIC DEFAULT 0,
            virtual_amount NUMERIC DEFAULT 0,
            locking_order varchar[] DEFAULT NULL,
            locked_amount NUMERIC DEFAULT 0,
            overdraft_limit NUMERIC DEFAULT 0
        )
    ''')

    print 'Creating index balance_environment_id_idx on balance'
    curs.execute(
    '''
        CREATE INDEX balance_environment_id_idx ON balance(environment_id)
    ''')

    print 'Creating index balance_environment_id_user_id_idx on balance'
    curs.execute(
    '''
        CREATE INDEX balance_environment_id_user_id_idx ON balance(environment_id, user_id)
    ''')

    print 'Creating unique index balance_environment_id_user_id_currency_id_idx on balance'
    curs.execute(
    '''
        CREATE UNIQUE INDEX balance_environment_id_user_id_currency_id_idx ON
            balance(environment_id, user_id, currency_id)
    ''')


def revert(curs):
    print 'Dropping index balance_environment_id_idx on balance'
    curs.execute('DROP INDEX IF EXISTS balance_environment_id_idx')

    print 'Dropping index balance_environment_id_user_id_idx on balance'
    curs.execute('DROP INDEX IF EXISTS balance_environment_id_user_id_idx')

    print 'Dropping unique index balance_environment_id_user_id_currency_id_idx on balance'
    curs.execute('DROP INDEX IF EXISTS balance_environment_id_user_id_currency_id_idx')

    print 'Dropping table balance'
    curs.execute('DROP TABLE IF EXISTS balance')

