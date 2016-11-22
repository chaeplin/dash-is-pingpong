#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io, os, sys
import simplejson as json
import datetime
import time
import zmq
import array
import binascii
import struct
import redis
import logging
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from libs.config import *

def checksynced():
    try:
        synced = access.mnsync('status')['IsSynced']
        return synced

    except:
        return False

# logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs/' + os.path.basename(__file__) + '.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

# rpc 
serverURL = 'http://' + rpcuser + ':' + rpcpassword + '@' + rpcbindip + ':' + str(rpcport)
access = AuthServiceProxy(serverURL)

# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

# check redis
logging.info('[is_block_to_list] start')
try:
    r.ping()

except Exception as e:
    logging.info(e.args[0])
    sys.exit()

# check dashd
while(not checksynced()):
    logging.info('not synced')
    time.sleep(30)

logging.info('[is_block_to_list] start')

# zmq
zmqContext = zmq.Context()
zmqSubSocket = zmqContext.socket(zmq.SUB)
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, b"hashblock")
#zmqSubSocket.setsockopt(zmq.SUBSCRIBE, b"hashtx")
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, b"hashtxlock")
zmqSubSocket.connect("tcp://%s:%i" % (rpcbindip, zmqport))

# main
try:
    while True:
        msg = zmqSubSocket.recv_multipart()
        topic = str(msg[0].decode("utf-8"))
        body  = str(binascii.hexlify(msg[1]).decode("utf-8"))
        sequence = "Unknown"

        if len(msg[-1]) == 4:
          msgSequence = struct.unpack('<I', msg[-1])[-1]
          sequence = str(msgSequence)

        if topic == "hashblock":
            r.lpush(r_LI_BL_RECEIVED, body)
            logging.info('block   ----------> %s - %s' % (sequence, body))

        elif topic == "hashtxlock":
            r.lpush(r_LI_IS_RECEIVED, body)
            logging.info('islock  ----------> %s - %s' % (sequence, body))

except Exception as e:
    logging.info(e.args[0])
    zmqContext.destroy()
    sys.exit()

except KeyboardInterrupt:
    logging.info('[is_block_to_list] intterupted by keyboard')
    sys.exit()

