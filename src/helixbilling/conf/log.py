import logging
from logging.handlers import RotatingFileHandler
from settings import log_filename, log_level, log_console, log_format,\
    log_max_bytes, log_backup_count

def init_logger():
    l = logging.getLogger('helixbilling')
    l.setLevel(log_level)

    fmt = logging.Formatter(log_format)

    file_handler = RotatingFileHandler(log_filename, 'a', log_max_bytes, log_backup_count, 'UTF-8')
    file_handler.setFormatter(fmt)

    l.addHandler(file_handler)

    if log_console:
        cons_handler = logging.StreamHandler()
        cons_handler.setLevel(log_level)
        cons_handler.setFormatter(fmt)
        l.addHandler(cons_handler)
    return l

logger = init_logger()
