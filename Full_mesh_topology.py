#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import RemoteController, Controller
from mininet.cli import CLI
from mininet.log import setLogLevel

def leaf_spine_topology():
    net = Mininet()

    # Add Controllers
    c1 = net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6633)
    c2 = net.addController('c2', controller=RemoteController, ip='127.0.0.1', port=6634)

    # Add Spine Switches
    spine1 = net.addSwitch('spine1')
    spine2 = net.addSwitch('spine2')

    # Add Leaf Switches
    leaf1 = net.addSwitch('leaf1')
    leaf2 = net.addSwitch('leaf2')
    leaf3 = net.addSwitch('leaf3')
    leaf4 = net.addSwitch('leaf4')

    # Connect Spine to Leafs
    net.addLink(spine1, leaf1)
    net.addLink(spine1, leaf2)
    net.addLink(spine2, leaf3)
    net.addLink(spine2, leaf4)

    # Add Hosts and connect to Leaf Switches
    hosts = []
    for i in range(1, 11):
        host = net.addHost(f'h{i}', ip=f'10.0.0.{i}/24')
        hosts.append(host)
    
    # Assign Hosts to Leafs
    net.addLink(hosts[0], leaf1)  # h1 to leaf1
    net.addLink(hosts[1], leaf1)  # h2 to leaf1
    net.addLink(hosts[2], leaf2)  # h3 to leaf2
    net.addLink(hosts[3], leaf2)  # h4 to leaf2
    net.addLink(hosts[4], leaf3)  # h5 to leaf3
    net.addLink(hosts[5], leaf3)  # h6 to leaf3
    net.addLink(hosts[6], leaf4)  # h7 to leaf4
    net.addLink(hosts[7], leaf4)  # h8 to leaf4
    net.addLink(hosts[8], spine1)  # h9 directly to spine1
    net.addLink(hosts[9], spine2)  # h10 directly to spine2

    # Start the network
    net.start()

    print("Leaf-Spine Topology with 2 Spine Switches, 4 Leaf Switches, and 10 Hosts")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    leaf_spine_topology()

