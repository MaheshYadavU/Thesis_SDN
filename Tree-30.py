from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

net = Mininet(controller=None, link=TCLink)

# Adding controllers
c1 = net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6633)
c2 = net.addController('c2', controller=RemoteController, ip='127.0.0.1', port=6634)
c3 = net.addController('c3', controller=RemoteController, ip='127.0.0.1', port=6635)

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

# Creating tree topology
for i in range(1, 15):
    net.addLink(switches[i], switches[(i-1)//2])

# Connecting hosts to switches
for i in range(7):
    net.addLink(hosts[i*4], switches[2*i])
    net.addLink(hosts[i*4+1], switches[2*i])
    net.addLink(hosts[i*4+2], switches[2*i+1])
    net.addLink(hosts[i*4+3], switches[2*i+1])
net.start()
CLI(net)
net.stop()
