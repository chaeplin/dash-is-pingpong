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

def rpc_getblock(block):
    print('rpc_getblock: ---> %s' % block)
    try:
        blockjson = access.getblock(block, True)
        height = blockjson['height']
        r.set(r_KEY_BLOCK_HEIGHT, height)
        print('  --> height: %s' % height)

        for tx in blockjson['tx']:
            refundtx = rpc_getrawtransaction(tx)
            if refundtx:
                print('  refundtx ---> ' + str(refundtx))
                r.zadd(r_SS_QUEUE_TX, height, json.dumps(refundtx, sort_keys=True))
                r.zadd(r_SS_REFUNDTX, get_nanotime(), refundtx['txid'])

        # check r_SS_QUEUE_TX and move to r_LI_REFUND
        mm = json.loads(json.dumps(r.zrangebyscore(r_SS_QUEUE_TX, '-inf', float(height -6))))
        if mm:
            print('   --> refundtx to job list')
            for x in mm:
                r.lpush(r_LI_REFUND, json.dumps(json.loads(x), sort_keys=True))

            r.zremrangebyscore(r_SS_QUEUE_TX, '-inf', float(height -6))

    except Exception as e:
        print(e.args)
        pass

def rpc_get_input_addr(txid, index):
    try:
        from_addr = access.getrawtransaction(txid, 1)['vout'][index]['scriptPubKey']['addresses'][0]
        return from_addr

    except Exception as e:
        print(e.args)
        return None

def rpc_getrawtransaction(txid):
    try:
        txjson = access.getrawtransaction(txid, 1)
        if len(txjson['vin']) == 1 and 'coinbase' in txjson['vin'][0]:
            print('   --> coinbase')
            return None

        if r.zscore(r_SS_REFUNDTX, txid) != None:
            print('  ---> tx is in refund list')
            return None

        from_addr = rpc_get_input_addr(txjson['vin'][0]['txid'], txjson['vin'][0]['vout'])

        for vo in txjson['vout']:
            rx_addr  = vo['scriptPubKey']['addresses'][0]
            rx_value = vo['value']

            if rx_addr == RX_ADDR:
                reveived = {}
                reveived['txid'] = txid
                reveived['from'] = from_addr
                reveived['to']   = rx_addr
                reveived['val']  = rx_value

                return reveived

        return None

    except Exception as e:
        print(e.args)
        return None

# rpc 
serverURL = 'http://' + rpcuser + ':' + rpcpassword + '@' + rpcbindip + ':' + str(rpcport)
access = AuthServiceProxy(serverURL)

# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

# check redis
print('[dequeue] start')
try:
    r.ping()

except Exception as e:
    print(e.args[0])
    sys.exit()

# check dashd
while(not checksynced()):
    print('not synced')
    time.sleep(30)

print('[dequeue] start')

#
try:

    while 1:
        quelist = (r_LI_BL_RECEIVED, r_LI_IS_RECEIVED)
        jobque = r.brpop(quelist, 0)
        
        if jobque:
            redis_key = jobque[0]
            redis_val = jobque[1]

            if redis_key.decode("utf-8") == r_LI_IS_RECEIVED:
                print('rpc_rawtx:    ---> %s' % redis_val)
                refundis = rpc_getrawtransaction(redis_val.decode("utf-8"))
                if refundis:
                    print('  refundis ---> ' + str(refundis))
                    r.lpush(r_LI_REFUND, json.dumps(refundis, sort_keys=True))
                    r.zadd(r_SS_REFUNDTX, get_nanotime(), redis_val.decode("utf-8"))

            elif redis_key.decode("utf-8") == r_LI_BL_RECEIVED:
                rpc_getblock(redis_val.decode("utf-8"))

except Exception as e:
    print(e.args)
    sys.exit()

except KeyboardInterrupt:
    print('[dequeue] intterupted by keyboard')
    sys.exit()

