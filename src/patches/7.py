def apply(curs): #IGNORE:W0622
    print 'Creating table bonus'
    curs.execute(
    '''
        CREATE TABLE bonus (
            id serial,
            PRIMARY KEY(id),
            operator_id integer NOT NULL,
            FOREIGN KEY(operator_id) REFERENCES operator(id),
            customer_id varchar NOT NULL,
            creation_date timestamp with time zone NOT NULL DEFAULT now(),
            amount int
        )
    ''')

    print 'Creating index bonus_operator_id_customer_id_idx on bonus'
    curs.execute(
    '''
        CREATE INDEX bonus_operator_id_customer_id_idx ON bonus(operator_id, customer_id)
    ''')


def revert(curs):
    print 'Dropping index bonus_operator_id_customer_id_idx on bonus'
    curs.execute('DROP INDEX bonus_operator_id_customer_id_idx')

    print 'Dropping table bonus'
    curs.execute('DROP TABLE bonus')

