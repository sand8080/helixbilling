def apply(curs):
    print 'Creating view receipt_total_view'
    curs.execute(
    '''
        CREATE VIEW receipt_total_view (client_id, amount)
        AS
        SELECT
            balance.client_id,
            COALESCE(sum(receipt.amount), 0)
        FROM balance
            left join receipt on (balance.client_id = receipt.client_id)
        GROUP BY balance.client_id
    ''')

    print 'Creating view bonus_total_view'
    curs.execute(
    '''
        CREATE VIEW bonus_total_view (client_id, amount)
        AS
        SELECT
            balance.client_id,
            COALESCE(sum(bonus.amount), 0)
        FROM balance
            left join bonus on (balance.client_id = bonus.client_id)
        GROUP BY balance.client_id
    ''')

    print 'Creating view chargeoff_total_view'
    curs.execute(
    '''
        CREATE VIEW chargeoff_total_view (client_id, amount)
        AS
        SELECT
            balance.client_id,
            COALESCE(sum(charge_off.amount), 0)
        FROM balance
            left join charge_off on (balance.client_id = charge_off.client_id)
        GROUP BY balance.client_id
    ''')
#    curs.execute(
#    '''
#        CREATE VIEW balance_total_view (client_id, receipt_total, bonus_total, chargeoff_total)
#        AS
#        SELECT
#            balance.client_id,
#            COALESCE(sum(receipt.amount), 0),
#            COALESCE(sum(bonus.amount), 0),
#            COALESCE(sum(charge_off.amount), 0)
#        FROM balance
#            left join receipt on (balance.client_id=receipt.client_id)
#            left join bonus on (balance.client_id=bonus.client_id)
#            left join charge_off on (balance.client_id=charge_off.client_id)
#        GROUP BY balance.client_id
#    ''')

def revert(curs):
    print 'Dropping view bonus_total_view'
    curs.execute('DROP VIEW bonus_total_view')

    print 'Dropping view receipt_total_view'
    curs.execute('DROP VIEW receipt_total_view')

    print 'Dropping view chargeoff_total_view'
    curs.execute('DROP VIEW chargeoff_total_view')
