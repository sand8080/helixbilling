import helixcore.db.deadlock_detector as deadlock_detector


deadlock_detector.ALLOWED_TRANSITIONS = [
#    (Balance.table, BalanceLock.table), #unlock, charge_off
]
