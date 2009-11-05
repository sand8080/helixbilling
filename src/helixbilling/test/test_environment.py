from helixbilling.conf import settings
#settings.DSN = 'dbname=helixtest host=localhost user=helixtest password=qazwsx'
settings.DSN = 'dbname=test_helixbilling host=localhost user=helixtest password=qazwsx'

import logging
settings.log_filename = '/tmp/helixbilling.log'
settings.log_level = logging.DEBUG
settings.log_level = logging.ERROR
settings.log_console = True

import os
patches_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), '..', '..', 'patches')