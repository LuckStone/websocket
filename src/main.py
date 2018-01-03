import os

from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.web import server
from twisted.web.static import File
from txsockjs.factory import SockJSResource

from core.terminal import SSHProtocol


workroot = os.path.dirname(os.path.abspath(__file__))
wwwroot =  os.path.split(workroot)[0]
wwwroot = os.path.join(wwwroot, "wwwroot")

root = File(wwwroot)
root.putChild("chat", SockJSResource(Factory.forProtocol(SSHProtocol)))
site = server.Site(root)

reactor.listenTCP(9002, site)
reactor.run()

