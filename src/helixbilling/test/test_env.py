import os
import logging

from helixbilling.conf import settings


settings.DSN = {
    'user': 'helixtest',
    'database': 'test_helixbilling',
    'host': 'localhost',
    'password': 'qazwsx'
}

settings.server_host = 'localhost'
settings.server_port = 10998

settings.log_filename = os.path.join(os.path.realpath(os.path.dirname(__file__)),
    'helixbilling.log')
settings.log_level = logging.DEBUG
settings.log_console = True
settings.auth_server_url = 'http://localhost:10999'

patches_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), '..', '..', 'patches')
