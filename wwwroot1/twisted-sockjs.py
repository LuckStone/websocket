from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from txsockjs.factory import SockJSMultiFactory
from txsockjs.utils import broadcast

class ChatProtocol(Protocol):
    def connectionMade(self):
        if not hasattr(self.factory, "transports"):
            self.factory.transports = set()
        self.factory.transports.add(self.transport)
        self.transport.write('hello')

    def dataReceived(self, data):
        print data
        broadcast('reply: ' + data, self.factory.transports)

    def connectionLost(self, reason):
        self.factory.transports.remove(self.transport)

f = SockJSMultiFactory()
f.addFactory(Factory.forProtocol(ChatProtocol), "chat")

reactor.listenTCP(8080, f)
reactor.run()
