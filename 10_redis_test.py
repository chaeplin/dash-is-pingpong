#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import time
import sys
import simplejson as json
import redis
import os

from libs.config import *

import pprint

# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

pp = pprint.PrettyPrinter(indent=4)

try:
    r.ping()

except Exception as e:
    logging.info(e.args[0])
    sys.exit()

#
#
#r.delete(r_LI_IS_RECEIVED)
#r.delete(r_LI_BL_RECEIVED)
#r.delete(r_LI_REFUND)
#r.delete(r_SS_REFUNDTX)
#r.delete(r_SS_QUEUE_TX)
#r.delete(r_LI_REFUND_FAILED)
#r.delete(r_SS_REFUND_RESULT)
#sys.exit()
#
#

try:

    print()
    print('r_LI_IS_RECEIVED')
    pp.pprint(r.lrange(r_LI_IS_RECEIVED, 0, -1))

    print()
    print('r_LI_BL_RECEIVED')
    pp.pprint(r.lrange(r_LI_BL_RECEIVED, 0, -1))

    print()
    print('r_LI_REFUND')
    pp.pprint(r.lrange(r_LI_REFUND, 0, -1))

    print()
    print('r_SS_REFUNDTX')
    pp.pprint(r.zrange(r_SS_REFUNDTX, 0, -1, withscores=False))

    print()
    print('r_SS_QUEUE_TX')
    pp.pprint(r.zrange(r_SS_QUEUE_TX, 0, -1, withscores=False))

    print()
    print('r_KEY_BLOCK_HEIGHT')
    pp.pprint(r.get(r_KEY_BLOCK_HEIGHT))

    print()
    print('r_LI_REFUND_FAILED')
    pp.pprint(r.lrange(r_LI_REFUND_FAILED, 0, -1))

    print()
    print('r_SS_REFUND_RESULT')
    pp.pprint(r.zrange(r_SS_REFUND_RESULT, 0, -1, withscores=False))

except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    sys.exit(1)

