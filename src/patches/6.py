
def apply(curs):
    print 'Creating table bonus'
    curs.execute(
    '''
        CREATE TABLE bonus (
            id serial,
            client_id int NOT NULL,
            created_date timestamp with time zone NOT NULL DEFAULT now(),
            amount int,
            PRIMARY KEY(id)
        )
    ''')

    print 'Creating index bonus_client_id_idx on bonus'
    curs.execute(
    '''
        CREATE INDEX bonus_client_id_idx ON bonus(client_id);
    ''')

def revert(curs):
    print 'Dropping index bonus_client_id_idx on bonus'
    curs.execute('DROP INDEX bonus_client_id_idx')

    print 'Dropping table bonus'
    curs.execute('DROP TABLE bonus')

