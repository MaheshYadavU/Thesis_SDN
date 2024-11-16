from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.cli import CLI

net = Mininet(controller=RemoteController)

c1 = net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6633)
c2 = net.addController('c2', controller=RemoteController, ip='127.0.0.1', port=6634)

s1 = net.addSwitch('s1', protocols='OpenFlow13')
s2 = net.addSwitch('s2', protocols='OpenFlow13')

h1 = net.addHost('h1', ip='10.0.1.1/24')
h2 = net.addHost('h2', ip='10.0.1.2/24')
h3 = net.addHost('h3', ip='10.0.2.1/24')
h4 = net.addHost('h4', ip='10.0.2.2/24')
h5 = net.addHost('h5', ip='10.0.3.1/24')
h6 = net.addHost('h6', ip='10.0.3.2/24')
h7 = net.addHost('h7', ip='10.0.4.1/24')
h8 = net.addHost('h8', ip='10.0.4.2/24')

net.addLink(h1, s1)
net.addLink(h2, s1)
net.addLink(h3, s2)
net.addLink(h4, s2)
net.addLink(h5, s2)
net.addLink(h6, s2)
net.addLink(h7, s2)
net.addLink(h8, s2)

net.addLink(s1, s2)

net.build()
c1.start()
c2.start()

s1.start([c1])
s2.start([c2])

net.start()
CLI(net)
net.stop()