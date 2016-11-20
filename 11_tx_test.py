#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import time
import sys
import simplejson as json
import redis
import os

from libs.config import *
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

import pprint

# rpc 
serverURL = 'http://' + rpcuser + ':' + rpcpassword + '@' + rpcbindip + ':' + str(rpcport)
access = AuthServiceProxy(serverURL)


txs = [
    'b4a640a42f7190d6e4c028ccf0d3a7df625243c0ccb7d69a8fc5b38422eb6833',
    '2a13f342b4c9e4d7345a2831b1b937604c606b2315fc01d9be9b13e8ed1052f6',
    '4c5dba04583eab0e128554de6f43e5f6c624b94944af94607aee692deb46c31a',
    'e4b33589dcd339e96cc8f84397e9c5c9ebdf4b5320c64aa988fc06873b5b003a',
    '91498ad73af0be9b296f9cd665ee70dc0529b82da94cb61630181ad619b5e3b8',
    'f4bc76c58017c487cdd283fbfdb68fca55e3492b8dcaf9819e414400e3981e0c'
]

def rpc_get_input_addr(txid, index):
    try:
        from_addr = access.getrawtransaction(txid, 1)['vout'][index]['scriptPubKey']['addresses'][0]
        return from_addr

    except Exception as e:
        print(e.args[0])
        return None

def rpc_getrawtransaction(txid):
    print('rpc_rawtx:    ---> %s' % txid)
    try:
        txjson = access.getrawtransaction(txid, 1)

        if len(txjson['vin']) == 1 and 'coinbase' in txjson['vin'][0]:
            print('   --> coinbase')
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
        print(e.args[0])
        return None


try:
    for tx in txs:
        print(tx)
        print(rpc_getrawtransaction(tx))

except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    sys.exit(1)