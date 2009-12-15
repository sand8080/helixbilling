from helixbilling.conf import settings

settings.DSN = {
    'user': 'helixtest',
    'database': 'test_helixbilling',
    'host': 'localhost',
    'password': 'qazwsx'
}

settings.server_host = 'localhost'
settings.server_port = 10998

import logging
settings.log_filename = '/tmp/helixbilling.log'
settings.log_level = logging.DEBUG
settings.log_level = logging.ERROR
settings.log_console = True

import os
patches_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), '..', '..', 'patches')