from helixbilling.conf import settings
settings.DSN = 'dbname=helixtest host=localhost user=helixbilling password=qazwsx'

import logging
settings.log_filename = '/tmp/helixbilling.log'
settings.log_level = logging.DEBUG
settings.log_console = True
