from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

# Create Mininet object with no default controller
net = Mininet(controller=None, link=TCLink)

# Adding controllers (3 controllers for redundancy and load balancing)
c1 = net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6633, protocol='tcp', openflow=13)
c2 = net.addController('c2', controller=RemoteController, ip='127.0.0.1', port=6634, protocol='tcp', openflow=13)
c3 = net.addController('c3', controller=RemoteController, ip='127.0.0.1', port=6635, protocol='tcp', openflow=13)

# Adding 30 switches (Tree Topology)
switches = []
for i in range(1, 31):
    switch = net.addSwitch(f's{i}', protocols='OpenFlow13')
    switches.append(switch)

# Creating tree topology (connecting switches in a parent-child relationship)
# We have 30 switches, where each switch (except the root) is connected to its parent.
for i in range(1, 30):
    net.addLink(switches[i], switches[(i-1)//2])

# Adding 50 hosts
hosts = []
for i in range(1, 51):
    host = net.addHost(f'h{i}', ip=f'10.0.0.{i}/24')
    hosts.append(host)

# Connecting hosts to switches (distribute 50 hosts across the switches)
# Distribute hosts evenly across the switches, making sure each switch connects to multiple hosts.
# We'll connect the first 16 switches (one per switch) with 2 or more hosts each.
for i in range(50):
    net.addLink(hosts[i], switches[(i // 3) + 1])  # Distribute hosts across 16 switches (this should distribute fairly evenly)

# Start the network
net.start()

# Assign controllers to the switches (all switches use all three controllers)
for switch in switches:
    switch.start([c1, c2, c3])

# Open the CLI for user interaction
CLI(net)

# Stop the network
net.stop()

