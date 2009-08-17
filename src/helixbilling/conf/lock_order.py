
import helixcore.db.deadlock_detector as deadlock_detector
import helixbilling.domain.objects as objects

deadlock_detector.ALLOWED_TRANSITIONS = [
    (objects.Balance.table, objects.BalanceLock.table), #unlock, charge_off
]
