def apply(curs):
    print 'Creating table receipt'
    curs.execute(
    '''
        CREATE TABLE receipt (
            id serial,
            operator_id integer NOT NULL,
            FOREIGN KEY(operator_id) REFERENCES operator(id),
            customer_id varchar NOT NULL,
            amount NUMERIC,
            creation_date timestamp with time zone NOT NULL DEFAULT now(),
            PRIMARY KEY(id)
        )
    ''')

    print 'Creating index receipt_operator_id_customer_id_idx on receipt'
    curs.execute(
    '''
        CREATE INDEX receipt_operator_id_customer_id_idx ON receipt(operator_id, customer_id)
    ''')


def revert(curs):
    print 'Dropping index receipt_operator_id_customer_id_idx on receipt'
    curs.execute('DROP INDEX receipt_operator_id_customer_id_idx')

    print 'Dropping table receipt'
    curs.execute('DROP TABLE receipt')

