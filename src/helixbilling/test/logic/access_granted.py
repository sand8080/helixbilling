from helixcore.security import auth


GRANTED_SESSION_ID = 'test_access_granted_session'

def access_granted(_, __, ___, ____):
    return {'status': 'ok', 'session_id': GRANTED_SESSION_ID,
        'user_id': 777, 'environment_id': 8888}

def login_success(_, __):
    return {'status': 'ok', 'session_id': GRANTED_SESSION_ID}

auth.Authentifier.check_access = access_granted
auth.Authentifier.login = login_success