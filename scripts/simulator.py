#!/usr/bin/env python3

import json  # noqa
import time  # noqa
import argparse
import asyncio
import signal
import collections
import logging
import sys
import datetime as date
import hashlib
from uuid import uuid1

from mfba.network import (
    BaseServer,
    LocalTransport,
    Message,
    Node,
    Quorum,
)
from mfba.common import (
    log,
)
from mfba.consensus import (
    FBAConsensus as Consensus,
    Ballot,
) 
import time


NodeConfig = collections.namedtuple(
    'NodeConfig',
    (
        'name',
        'endpoint',
        'threshold',
    ),
)
MESSAGE = None
count = 0

async def check_message_in_storage(node):
    global MESSAGE
    global count
    global previous_block
    global loop
    global no_of_nodes
    global threshold

    if check_message_in_storage.is_running:
        return

    check_message_in_storage.is_running = True

    found = list()
    #log.main.info('%s: checking input message was stored: %s', node.name, MESSAGE)
    while len(found) < len(servers):
        for node_name, server in servers.items():
            if node_name in found:
                continue

            storage = server.consensus.storage

            is_exists = storage.is_exists(MESSAGE)
            if is_exists:

                '''log.main.warning(
                    '> %s: is_exists=%s state=%s',
                    node_name,
                    is_exists,
                    server.consensus.ballot.state,
                    # json.dumps(storage.ballot_history.get(MESSAGE.message_id), indent=2),
                      # json.dumps(storage.ballot_history.get(MESSAGE.message_id)),
                )'''
                found.append(node_name)

            await asyncio.sleep(0.01)

    await asyncio.sleep(3)

    #print(count)
    check_message_in_storage.is_running = False
    with open('text.txt', 'r') as f:
        x = f.readlines()
    if count == len(x):
        total_time = (time.time() - start_time)
        loop.stop()
        k = open('node%s.txt'%no_of_nodes, 'a')
        k.write("no of nodes=%s  threshold = %s time = %s" %(no_of_nodes,threshold,total_time*10))
        k.write("\n")
        return
    else:
        dat = x[count]
        count += 1
        block_to_add,newblock = next_block(previous_block,dat)
        blockchain.append(block_to_add)
        previous_block = block_to_add
        j = json.dumps(newblock,indent=5)
        f= open('bct.json', 'a')
        print(j, file=f)
        f.write('\n')
        f.close()

    MESSAGE = Message.new(dat)
    servers['n0'].transport.send(nodes['n0'].endpoint, MESSAGE.serialize(client0_node))
    log.main.info('inject message %s -> n0: %s', client0_node.name, MESSAGE)

    return


check_message_in_storage.is_running = False
def cancel_task_handler():    
    for task in asyncio.Task.all_tasks():
        task.cancel()    
    sys.exit(1)

def check_threshold(v):
    v = int(v)
    if v < 1 or v > 100:
        raise argparse.ArgumentTypeError(
            '%d is an invalid thresdhold, it must be 0 < trs <= 100' % v,
        )

    return v
class TestConsensus(Consensus):
    def reached_all_confirm(self, ballot_message):
        asyncio.ensure_future(check_message_in_storage(self.node))

        return

def hashing_block(i,t,d,h):
    sha = hashlib.sha256()
    string = str(i) + str(t) + str(d) + str(h)
    sha.update(string.encode('utf-8'))
    return sha.hexdigest()
class Server(BaseServer):
    node = None
    consensus = None

    def __init__(self, node, consensus, *a, **kw):
        assert isinstance(node, Node)
        assert isinstance(consensus, Consensus)

        super(Server, self).__init__(*a, **kw)

        self.node = node
        self.consensus = consensus

    def __repr__(self):
        return '<Server: node=%(node)s consensus=%(consensus)s>' % self.__dict__

    def message_receive(self, data_list):
        super(Server, self).message_receive(data_list)

        for i in data_list:
            log.server.debug('%s: hand over message to consensus: %s', self.name, i)
            self.consensus.receive(i)

        return
class Block:
  def __init__(self, index, timestamp, data, previous_hash):
    self.index = index
    self.timestamp = timestamp
    self.data = data
    self.previous_hash = previous_hash
    self.hash = self.hash_block()
  
  def hash_block(self):
    sha = hashlib.sha256()
    string = str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash)
    sha.update(string.encode('utf-8'))
    return sha.hexdigest()

def create_genesis_block():
    newblock = ({
        "index": 0,
        "timestamp": str(date.datetime.now()),
        "previous hash": " ",
        "hash": hashing_block(0, date.datetime.now(), "Genesis Block", "0"),
        })
    j = json.dumps(newblock,indent=5)
    f= open('bct.json', 'w')
    print(j, file=f)
    f.write('\n')
    f.close()
    return Block(0, date.datetime.now(), "Genesis Block", "0")

def next_block(last_block,data_):
    global client0_node_hash
    this_index = last_block.index + 1
    this_timestamp = date.datetime.now()
    this_data = data_
    this_hash = last_block.hash
    block_hash = hashing_block(this_index, this_timestamp, this_data, this_hash)
    newblock = ({
        "index": this_index,
        "timestamp": str(this_timestamp),
        "previous hash": this_hash,
        "data": this_data[:-1],
        "hash": block_hash,
        "validator": client0_node_hash
        })


    return Block(this_index, this_timestamp, this_data, this_hash), newblock


parser = argparse.ArgumentParser()
parser.add_argument('-s', dest='silent', action='store_true', help='turn off the debug messages')
parser.add_argument('-nodes', type=int, default=4, help='number of validator nodes in the same quorum; default 4')
parser.add_argument('-trs', type=check_threshold, default=80, help='threshold; 0 < trs <= 100')


if __name__ == '__main__':
    start_time = time.time()
    log_level = logging.DEBUG
    if '-s' in sys.argv[1:]:
        log_level = logging.INFO

    log.set_level(log_level)
    options = parser.parse_args()
    log.main.debug('options: %s', options)
    no_of_nodes = options.nodes
    threshold = options.trs
    client0_config = NodeConfig('client0', None, None)
    client0_node = Node(client0_config.name, client0_config.endpoint, None)
    sha = hashlib.sha256()
    strinn = "client0"
    sha.update(strinn.encode('utf-8'))
    client0_node_hash = sha.hexdigest()
    log.main.debug('client node created: %s', client0_node)
    client1_config = NodeConfig('client1', None, None)
    client1_node = Node(client1_config.name, client1_config.endpoint, None)
    log.main.debug('client node created: %s', client1_node)

    nodes_config = dict()
    for i in range(options.nodes):
        name = 'n%d' % i
        endpoint = 'sock://memory:%d' % i
        nodes_config[name] = NodeConfig(name, endpoint, options.trs)

    log.main.debug('node configs created: %s', nodes_config)

    quorums = dict()
    for name, config in nodes_config.items():
        validator_configs = filter(lambda x: x.name != name, nodes_config.values())

        quorums[name] = Quorum(
            config.threshold,
            list(map(lambda x: Node(x.name, x.endpoint, None), validator_configs)),
        )
    log.main.debug('quorums created: %s', quorums)

    nodes = dict()
    transports = dict()
    consensuses = dict()
    servers = dict()
    bct = dict()

    loop = asyncio.get_event_loop()

    for name, config in nodes_config.items():
        nodes[name] = Node(name, config.endpoint, quorums[name])
        log.main.debug('nodes created: %s', nodes)

        transports[name] = LocalTransport(name, config.endpoint, loop)
        log.main.debug('transports created: %s', transports)

        consensuses[name] = TestConsensus(nodes[name], quorums[name], transports[name])
        log.main.debug('consensuses created: %s', consensuses)

        servers[name] = Server(nodes[name], consensuses[name], name, transport=transports[name])
        log.main.debug('servers created: %s', servers)

    for server in servers.values():
        server.start()

    # send message to `server0`
    blockchain = [create_genesis_block()]
    previous_block = blockchain[0]
    #for i in range(10):
    f = open("text.txt","r")
    x = f.readlines()
    block_to_add,newblock = next_block(previous_block,x[0])
    blockchain.append(block_to_add)
    previous_block = block_to_add
    j = json.dumps(newblock,indent=5)
    f= open('bct.json', 'a')
    print(j, file=f)
    f.write('\n')
    f.close()

    count = 1
    MESSAGE = Message.new(x[0])
    servers['n0'].transport.send(nodes['n0'].endpoint, MESSAGE.serialize(client0_node))
    log.main.info('inject message %s -> n0: %s', client0_node.name, MESSAGE)

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        log.main.debug('goodbye~')
        sys.exit(1)
    finally:
        loop.close()


