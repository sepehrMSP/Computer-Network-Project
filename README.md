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

