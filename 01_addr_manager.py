#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import time
import os, sys
import simplejson as json
from pycoin.key import Key
import redis
import logging

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from libs.config import *

def get_bip32_address_info(key, index):
#    addr = key.subkey(index).address(use_uncompressed=False)
    addr = access.getnewaddress()
    return { "index": index, "addr": addr }

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
logging.info('[addr_manager] start')
try:
    r.ping()
    
except Exception as e:
    logging.info(e.args[0])
    sys.exit()

# 
key = Key.from_text(BIP32_TESTNET_SEED)

# check current index
get_r_KEY_ADDR_GEN_INDEX = r.get(r_KEY_ADDR_GEN_INDEX)

if get_r_KEY_ADDR_GEN_INDEX == None:
    current_index = 0

else:
    current_index = int(get_r_KEY_ADDR_GEN_INDEX)

#
try:

    while 1:
        if r.scard(r_S_NEW_ADDRS) < max_keys_in_r_S_NEW_ADDRS:
            logging.info('[addr_manager] adding keys to key pool')
            while 1:
                addr = get_bip32_address_info(key, current_index)['addr']
                logging.info('[addr_manager] gened addr: [' + str(current_index) + '] : ' + addr)
                r.sadd(r_S_NEW_ADDRS, addr)
                current_index = r.incr(r_KEY_ADDR_GEN_INDEX)

                if r.scard(r_S_NEW_ADDRS) > (max_keys_in_r_S_NEW_ADDRS * 2):
                    break
        
        else:
            logging.info('[addr_manager] enough keys, sleep 60 secs')
            time.sleep(60)
        
except Exception as e:
    logging.info(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    logging.info('[addr_manager] intterupted by keyboard')
    sys.exit()

