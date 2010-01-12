def apply(curs):
    print 'Creating table balance'
    curs.execute(
    '''
        CREATE TABLE balance (
            id serial,
            billing_manager_id integer NOT NULL,
            active bool NOT NULL DEFAULT True,
            client_id varchar NOT NULL,
            currency_id int NOT NULL,
            created_date timestamp with time zone NOT NULL DEFAULT now(),
            available_real_amount int DEFAULT 0,
            available_virtual_amount int DEFAULT 0,
            locking_order varchar[] DEFAULT NULL,
            locked_amount int DEFAULT 0,
            overdraft_limit int DEFAULT 0,
            PRIMARY KEY(id),
            FOREIGN KEY(currency_id) REFERENCES currency(id),
            FOREIGN KEY(billing_manager_id) REFERENCES billing_manager(id),
            UNIQUE(client_id)
        )
    ''')

def revert(curs):
    print 'Dropping table balance'
    curs.execute('DROP TABLE balance')

