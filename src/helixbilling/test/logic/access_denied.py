from helixcore import error_code
from helixcore.security import auth


def access_denied(_, __, ___, ____):
    return {'status': 'error', 'message': 'TEST ACCESS DENIED',
        'code': error_code.HELIX_AUTH_ERROR}


def login_failure(_, __):
    return {'status': 'error', 'message': 'TEST LOGIN FAILED',
        'code': error_code.HELIX_AUTH_ERROR}


auth.Authentifier.check_access = access_denied
auth.Authentifier.login = login_failure