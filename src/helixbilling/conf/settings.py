#DSN = 'dbname=helixbilling host=localhost user=helixbilling password=qazwsx'
DSN = 'dbname=_DBC_DBNAME_ host=_DBC_DBSERVER_ user=_DBC_DBUSER_ password=_DBC_DBPASS_'

patch_table_name = 'patches'

server_host = 'localhost'
server_port = 9998

import logging
log_filename = '/var/log/helixbilling.log'
log_level = logging.DEBUG
log_format = "%(asctime)s [%(levelname)s] - %(message)s"
log_console = False
log_max_bytes = 2048000
log_backup_count = 20

import lock_order #IGNORE:W0611 @UnusedImport
