from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

net = Mininet(controller=None, link=TCLink)

# Adding controllers
c1 = net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6633, protocol='tcp', openflow=13)
c2 = net.addController('c2', controller=RemoteController, ip='127.0.0.1', port=6634, protocol='tcp', openflow=13)
c3 = net.addController('c3', controller=RemoteController, ip='127.0.0.1', port=6635, protocol='tcp', openflow=13)

# Adding switches
switches = []
for i in range(1, 16):
    switch = net.addSwitch(f's{i}', protocols='OpenFlow13')
    switch.start([c1, c2, c3])
    switches.append(switch)

# Adding hosts
hosts = []
for i in range(1, 31):
    host = net.addHost(f'h{i}', ip=f'10.0.0.{i}/24')
    hosts.append(host)

# Creating ring topology (connecting switches in a ring)
for i in range(len(switches)):
    net.addLink(switches[i], switches[(i+1) % len(switches)])

# Connecting hosts to switches
for i in range(15):
    net.addLink(hosts[2*i], switches[i])
    net.addLink(hosts[2*i+1], switches[i])

net.start()
CLI(net)
net.stop()

