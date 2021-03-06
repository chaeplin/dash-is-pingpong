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
import nanotime
import pickle
import subprocess
import logging

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from libs.config import *

def get_nanotime():
    return int(nanotime.now().unixtime() * 1000000000)

def checksynced():
    try:
        synced = access.mnsync('status')['IsSynced']
        return synced

    except:
        return False

#def refund(addr, val):
#    try:
#        cmd = "/usr/local/bin/dash-cli instantsendtoaddress " + addr + " " + str(val)
#        with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout as f:
#            result = f.read().splitlines()
#            return result[0].decode("utf-8")
#
#    except Exception as e:
#        return None


def refund(addr, val):
    try:
        r = access.instantsendtoaddress(addr, val, '', '', True)
        return r

    except Exception as e:
        return None

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
logging.info('[refund] start')
try:
    r.ping()

except Exception as e:
    logging.info(e.args[0])
    sys.exit()

# check dashd
while(not checksynced()):
    logging.info('not synced')
    time.sleep(30)

logging.info('[refund] start')

#


#
try:

    while 1:
        quelist = (r_LI_REFUND)
        jobque = r.brpop(quelist, 0)

        if jobque:
            redis_val = json.loads(jobque[1])
            addr = redis_val['from']
            val  = redis_val['val']
            txid = redis_val['txid']
            outval = val

            if val <= 1:
                outval = 1
            elif val > 10:
                outval = 5

            height = r.get(r_KEY_BLOCK_HEIGHT)
            logging.info('refund %s - %s to %s' % (txid, outval, addr))
            refundresult = refund(addr, outval)
            logging.info('refund refundresult : %s' % (refundresult))
            if refundresult:
                redis_val['outtxid']   = refundresult
                redis_val['outto']     = addr
                redis_val['outval']    = outval
                redis_val['outheight'] = height
                r.zadd(r_SS_REFUND_RESULT, height, json.dumps(redis_val, sort_keys=True)) 
    
            else:
                r.lpush(r_LI_REFUND_FAILED, json.dumps(redis_val, sort_keys=True))

            time.sleep(0.2)

except Exception as e:
    logging.info(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    logging.info('[refund] intterupted by keyboard')
    sys.exit()

