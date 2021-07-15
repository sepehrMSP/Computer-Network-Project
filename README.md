# Computer-Network-Project

## Goal

In this project we intend to implement a P2P network. This network is a binary of nodes. Nodes are listed in the tree in the order in which they were added. Each node has some previlages for Data entry/exit to its sub-tree which is controled by firewall. Every user is connect to the network by requesting the admin with a special protocol. We will implement the later protocols in different layers of the network.

## Introduction

P2P networks are kind of networks in which every node is considered as client as well as server. In this kind of network, unlike client-server networks, there is no centeral server. Tor, Bitcoin and Torrent are some of wellknown P2P networks. Note that in practice there does not exist a fully P2P network and there are some node that guarantee the stability of the network and their removal will lead to disprution.

## Implementation

All users are run on the local host. Every user has a port by which incomming packets are accepted. For sending every packer from `A` to `B`, `A` must connect to the specific port of the `B` and the connection must be closed after finishing of the data transfer. Therefore, there should be two threads for every user:

- A thread for receiving messages listening on the user specified port. 
- A thread for doing commands of the user that are read by the terminal.

A arbitrary strategy can be taken for choosing the port that is utilized for sending by user. For example, if a user utilizes port `i` for receiving new packets, port `i+1` can be used for sending data. It is possible to assume that the ports are not reserved w.r.t nodes and can have randomly distributed values.

## Network connection
In a network, each node has a unique identifier. This ID is specified by the user. The admin port is a public value that everyone's own (select it at will). The administrator on the port is listening to the connection with the new user who wants to be added to the network. Assmue a user wants to access the network, in this case after entering the message
`CONNECT AS new_id ON THE PORT port`
At the user terminal, a TCP connection is established with the administrator. The following request is then sent to the administrator:
`new_id REQUESTS FOR CONNECTING TO THE NETWROK ON PORT port`
With this message, the user with the `new_id` tells the administrator that he connects you to the network and is listening on the `port` for incoming messages. Then, In response, the administrator sends the port and the node ID that the new user must connect to (according to the following message).
`CONNECT TO parent_id WITH MY PORT parent_port`
If there are no nodes in the network, the value manager `-1` for both the ID and the port to the user and the user can identify itself as the root of the users' tree. Note that the manager must be added to manage new nodes to the network so that the tree remains binary and has the least depth. The port that the administrator sends to the user is, if possible, the connection of his father to the network. Once the port user is a node to be connected, he or she will reconnect to the previous administrator, and if you do not have root, establish a new connection to your parent on the network. After closing, it makes type 41 (will be described later), set its source ID its ID, its destination ID the parent ID and in data, puts port number which is listening on and close the connection after sending the package.


## Semi-Transfer layer!
In order to have infrastructure for application communication in this network, the `Packet` class must be implemented. This class has 4 attributes:
- `type`: `int`
- `source ID`: `int`
- `destination ID`: `int`
- `data`: `string`

All messages transmitted on the network (except communication messages) must be instances of this class. After making a sample and completing its components, the object is sent via communication. The different types of packages are listed in the table below.
|Type| Packet  |
|--|--|
|  Message | 0 |
|RoutingRequest|10|
|RoutingResponse|11|
|ParentAdvertise|20|
|Advertise|21|
| DestinationNotFoundMessage|31|
|ConnectionRequest|41|

A very important feature in packets is that if the `destination id` is set in a packet equal to `-1`, the packet must be sent to all nodes and each node must send it to all nodes associated with them (except the node that Receive and send the package) and all nodes must return the required response to the sender according to the content of the package.
## Recognize each node from the network 
Each user should have a list of nodes that are aware of their existence in the network. The user can only send messages to nodes that are aware of their existence. The following are the factors that make node `A` known by node `B`:
- All nodes are aware of their parent node. 
- If `A` is a child of `B`, node `B` will be notified when `A` is added. 
- If a message packet is sent from `A` to `B`, `B` will be notified of `A`'s presence. If the destination address is `-1` All nodes (except the source node) are the destination of the message. 
- By sending a chat start message, all nodes in the chat to the list of nodes recognized by the message receiving node Are added. 

If the following statement is written in the terminal of node `A`, a list of other node IDs identified by `A` should be printed in its terminal.
`SHOW KNOWN CLIENTS`
Also, if a packet wants to be sent from node `A` but its destination is unknown, sending should not happen. In this case, the following message is printed in terminal `A`. (`destination_id` is the unknown to A):

`Unknown destination destination_id`

