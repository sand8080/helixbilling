
def apply(curs):
    print 'Creating table balance'
    curs.execute(
    '''
        CREATE TABLE balance (
            id serial,
            active smallint NOT NULL DEFAULT 1,
            client_id varchar NOT NULL,
            currency_id int NOT NULL,
            created_date timestamp with time zone NOT NULL DEFAULT now(),
            available_real_amount int DEFAULT 0,
            available_virtual_amount int DEFAULT 0,
            locking_order varchar[] DEFAULT NULL,
            locked_amount int DEFAULT 0,
            overdraft_limit int DEFAULT 0,
            PRIMARY KEY(id),
            FOREIGN KEY(currency_id) REFERENCES currency(id) ON DELETE RESTRICT,
            UNIQUE(client_id)
        )
    ''')

#    print 'Creating index balance_client_id_idx on balance'
#    curs.execute(
#    '''
#        CREATE UNIQUE INDEX balance_client_id_idx ON balance(client_id);
#    ''')

def revert(curs):
#    print 'Dropping index balance_client_id_idx on balance'
#    curs.execute('DROP INDEX balance_client_id_idx')

    print 'Dropping table balance'
    curs.execute('DROP TABLE balance')

