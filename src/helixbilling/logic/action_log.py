import cjson
from helixcore.mapping.actions import insert
from helixbilling.domain.objects import ActionLog

def logged(fun):
    def decorated(obj, data, curs):
        client_id = data.get('client_id')
        action_name = fun.__name__
        request=cjson.encode(data)

        result = fun(obj, data, curs)

        log = ActionLog(client_id=client_id, action=action_name, request=request, response=cjson.encode(result))
        insert(curs, log)
        return result
    return decorated
