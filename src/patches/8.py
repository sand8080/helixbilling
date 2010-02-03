def apply(curs):
    print 'Creating table chargeoff'
    curs.execute(
    '''
        CREATE TABLE chargeoff (
            id serial,
            PRIMARY KEY(id),
            operator_id integer NOT NULL,
            FOREIGN KEY(operator_id) REFERENCES operator(id),
            customer_id varchar NOT NULL,
            product_id varchar NOT NULL,
            locked_date timestamp with time zone NOT NULL,
            chargeoff_date timestamp with time zone NOT NULL DEFAULT now(),
            real_amount int,
            virtual_amount int
        )
    ''')

    print 'Creating index chargeoff_operator_id_customer_id_product_id_idx on chargeoff'
    curs.execute(
    '''
        CREATE UNIQUE INDEX chargeoff_operator_id_customer_id_product_id_idx ON
            chargeoff(operator_id, customer_id, product_id)
    ''')


def revert(curs):
    print 'Dropping index chargeoff_operator_id_customer_id_product_id_idx on chargeoff'
    curs.execute('DROP INDEX chargeoff_operator_id_customer_id_product_id_idx')

    print 'Dropping table chargeoff'
    curs.execute('DROP TABLE chargeoff')

