import helixcore.db.deadlock_detector as deadlock_detector

from helixbilling.db.dataobject import Balance, BalanceLock


deadlock_detector.ALLOWED_TRANSITIONS = [
    (Balance.table, BalanceLock.table), #unlock, chargeoff
]
