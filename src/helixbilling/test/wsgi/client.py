from helixcore.test.util import ClientApplication


class Client(ClientApplication):
    def __init__(self, host, port, login, password):
        super(Client, self).__init__(host, port, login, password)

    def ping(self):
        return self.request({'action': 'ping'})
