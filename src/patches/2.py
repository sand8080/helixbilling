
def apply(curs):
    print 'Creating table currency'
    curs.execute(
    '''
        CREATE TABLE currency (
            id serial, 
            name varchar NOT NULL, 
            designation varchar NOT NULL, 
            cent_factor int NOT NULL DEFAULT 100,
            PRIMARY KEY(id),
            UNIQUE(name),
            CHECK(cent_factor > 0)
        )
    ''')

def revert(curs):
    print 'Dropping table currency'
    curs.execute('DROP TABLE currency')

