
def apply(curs):
    print 'Creating table receipt'
    curs.execute(
    '''
        CREATE TABLE receipt (
            id serial,
            client_id varchar NOT NULL,
            created_date timestamp with time zone NOT NULL DEFAULT now(),
            amount int,
            PRIMARY KEY(id)
        )
    ''')

    print 'Creating index receipt_client_id_idx on receipt'
    curs.execute(
    '''
        CREATE INDEX receipt_client_id_idx ON receipt(client_id);
    ''')

def revert(curs):
    print 'Dropping index receipt_client_id_idx on receipt'
    curs.execute('DROP INDEX receipt_client_id_idx')

    print 'Dropping table receipt'
    curs.execute('DROP TABLE receipt')

