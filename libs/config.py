# seed for generate address
BIP32_TESTNET_SEED = 'DRKPuUb97UQHNUHs5ktawTeAdwMsBaHCsLA1JW8iYpK5orXyiKPba3MyTP4sttpzhWdVKNej2TxkhR3WNrQqWGMg64ood5HaXL5Avi9ad5vaqc8U'

# max keys in r_NEW_ADDR_SET
max_keys_in_r_S_NEW_ADDRS = 100

# redis key prefix
key_prefix = 'DASHISPINGPONG:'

# redis key for index of key generation
r_KEY_ADDR_GEN_INDEX = key_prefix + 'KEY_ADDR_GEN_INDEX'

# SET Unused address pool
r_S_NEW_ADDRS  = key_prefix + 'S_NEW_ADDRS'
r_S_USED_ADDRS = key_prefix + 'S_USED_ADDRS'

# redis job list for IS
# 02 zmq IS and BLOCK
r_LI_IS_RECEIVED = key_prefix + 'LI_IX_RECEIVED'
r_LI_BL_RECEIVED = key_prefix + 'LI_BL_RECEIVED'

# 03 block height
r_KEY_BLOCK_HEIGHT = key_prefix + 'KEY_BLOCK_HEIGHT'

# 03 IS tx to job
# job queue
r_LI_REFUND      = key_prefix + 'LI_REFUND'
# all list of refund
r_SS_REFUNDTX    = key_prefix + 'SS_REFUNDTX'

# 03 BLOCK tx to queue
r_SS_QUEUE_TX    = key_prefix + 'SS_QUEUE_TX'

# 04
r_LI_REFUND_FAILED = key_prefix + 'LI_REFUND_FAILED'
r_SS_REFUND_RESULT = key_prefix + 'SS_REFUND_RESULT'

# receiving address
#RX_ADDR = 'yPYh6TFFUFoEQYsrhfDnsAUS1AHKuSYVZN'
RX_ADDR = 'yWrTyTHavPkgboceyhzX1SHfHEqQcaA6R8'

# rpc
rpcuser     = 'xx' 
rpcpassword = 'xxx--xxxx='

rpcbindip   = '127.0.0.1'
rpcport     = 19998

# zmq
zmqport     = 28332