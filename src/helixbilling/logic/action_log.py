import cjson
from helixcore.mapping.actions import insert
from helixbilling.domain.objects import ActionLog


def logged(fun):
    def decorated(obj, data, curs):
        request=cjson.encode(data)
        action_name = fun.__name__
        client_id = data.get('client_id')

        result = fun(obj, data, curs)

        log = ActionLog(client_id=client_id, action=action_name, request=request, response=cjson.encode(result))
        insert(curs, log)
    return decorated
