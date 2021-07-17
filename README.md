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

## Network Connection
In a network, each node has a unique identifier. This ID is specified by the user. The admin port is a public value that everyone's own (select it at will). The administrator on the port is listening to the connection with the new user who wants to be added to the network. Assmue a user wants to access the network, in this case after entering the message

`CONNECT AS new_id ON THE PORT port`

At the user terminal, a TCP connection is established with the administrator. The following request is then sent to the administrator:

`new_id REQUESTS FOR CONNECTING TO THE NETWROK ON PORT port`

With this message, the user with the `new_id` tells the administrator that he connects you to the network and is listening on the `port` for incoming messages. Then, In response, the administrator sends the port and the node ID that the new user must connect to (according to the following message).

`CONNECT TO parent_id WITH MY PORT parent_port`

If there are no nodes in the network, the value manager `-1` for both the ID and the port to the user and the user can identify itself as the root of the users' tree. Note that the manager must be added to manage new nodes to the network so that the tree remains binary and has the least depth. The port that the administrator sends to the user is, if possible, the connection of his father to the network. Once the port user is a node to be connected, he or she will reconnect to the previous administrator, and if you do not have root, establish a new connection to your parent on the network. After closing, it makes type 41 (will be described later), set its source ID its ID, its destination ID the parent ID and in data, puts port number which is listening on and close the connection after sending the package.


## Semi-Transfer Layer!
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
## Recognize Each Node From The Network 
Each user should have a list of nodes that are aware of their existence in the network. The user can only send messages to nodes that are aware of their existence. The following are the factors that make node `A` known by node `B`:
- All nodes are aware of their parent node. 
- If `A` is a child of `B`, node `B` will be notified when `A` is added. 
- If a message packet is sent from `A` to `B`, `B` will be notified of `A`'s presence. If the destination address is `-1` All nodes (except the source node) are the destination of the message. 
- By sending a chat start message, all nodes in the chat to the list of nodes recognized by the message receiving node Are added. 

If the following statement is written in the terminal of node `A`, a list of other node IDs identified by `A` should be printed in its terminal.

`SHOW KNOWN CLIENTS`

Also, if a packet wants to be sent from node `A` but its destination is unknown, sending should not happen. In this case, the following message is printed in terminal `A`. (`destination_id` is the unknown to A):

`Unknown destination destination_id`
## Routing and Packet Transfer
Each node must have node IDs of its subtree. When a node with identifier `A` wants to send a message to a node with identifier `B`, it first checks whether `B` is in its subtree. If it was, it sends the packet to the child  which `B` presents in its subtree, otherwise, it sends the packet to his father. A node that receives a message from its children or father that it is not its own destination repeats the same process and moves the packet to the next node. If a packet reaches the root and does not find the root of the `destination_id` in its children list, it creates a Type `31` packet and puts the following statement in its `data` field and returns it to the source address. The sender of the message should print this message in its terminal (if it is not a dialog mode. This mode is described in the application layer section).

`DESTINATION id_destination NOT FOUND`

## Packets Types
There are different types of packets that are specified in the `packet_type` attribute in the packet class.
### Routing
Assume that user `A` wants to find the path from itself to the user `B` to send the message. For this purpose, the following message is first entered in user `A`'s input:

`ROUTE id_B`

`A` then builds a packet of type `10`, matches the origin and destination, and sends the message according to the previous Section. The packet continues the route to the destination. After `B` receives the message, it creates a packet of type `11` and sets its origin as its ID and the destination as ID of `A`. It also puts its ID in the `data` field. It then sends the packet to `A`. Each node on the path that received the Type `11` packet adds its own ID and whether it is received from its child or father to the `data` field. At the end, after the message reaches `A`, the desired path reaches `A`, and `A` must print it in the terminal.
#### Example
![Figure 1](https://www.geeksforgeeks.org/wp-content/uploads/binary-tree-to-DLL.png)


Assume that In Figure 1, node 7 wants to find its way to 9. First make a packet of type 	`10`. Because it is not in the subtree of 7, he sends it to his father. 3 Receives the packet. Because 9 is not in its subtree, he sends it for 1. 1 knows that 9 is under his child's tree with ID 2, so it sends the packet to 2. 2 also acts like 1 and sends packet for 4 and 4 for 9. 9 receives the packet and sees that it is a routing packet with the `destination_id` equal to its ID. Then it makes a packet of type `11`, sets its `source_id` to 9 and the `destination_id` to the source of the received packet (7). Then in the `data` field, it simply puts its ID:

`9`

Sends the packet for 4. 4 Receives the packet and sees that it is of type `11`. Adds its ID and string `->` to the beginning of the `data` field (because it received the packet from its child) and sends the packet to 2 according to the given routing:

`4->9`

In the same way, 2 and 1 pass a packet of type `11` to 3 and the packet reaches 3 with the following message:

`1->2->4->9`

3 Receive the packet and sends according to routing for 7. The only difference is that because he received 3 the packet of type `11` from its father, it uses `<-` instead of `->` and the following message reaches 7:

`3<-1->2->4->9`

Also, because 7 received the packet from its father, it adds the appropriate phrase to the data field and put it in its terminal:

`7<-3<-1->2->4->9`


### Advertisements
There are two types of advertisements on the network.
#### Advertising ID to The Father Nodes
When a node is connected to its parent node in the network, all nodes that the new node exists in their subtree must be notified of its addition. This is done so that each node that is notified of the addition of a new node, notifies its parent with a type `20` packet. For example, in Figure 1, assume that node 15 is added to the tree as a child of node 6. Node 6 should create a type `20` packet with its `source_id` as its ID and the `destination_id` as node 3 ID. Then in the `data` field, put the ID of node 15 and send the packet to 3. when 3 received the packet and took the necessary measures, sends a same packet to 1 and informs him of the addition of 15 to the sub-tree.

