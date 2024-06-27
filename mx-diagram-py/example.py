from multiversx_sdk import ApiNetworkProvider
from transaction_diagram import TransactionVisualization

idx='1'
proxi = ApiNetworkProvider('https://devnet-api.multiversx.com')
hashes={
    '1': "0419c52371b6ea5e6c4985be96da87dca29896a1b2c4856c18ddd36767deb18f",                #submit batch tx
    '2': "6f572f8e770c5d74b24323f6d0df624e9bd8d23ed3ec5088f814ea6b6381e551",                #update tx
    '3': "3d5c1a2adbd6b362c749c1dfcde7aee269feeea8e5185aa15e08cef70cc39886",                #reward tx
    '4': "c6faf67c6655cae8114e4b86e4d8499108eed26bb868a1c0da6219aab2317381",                #swap fixed output tx
    '5': "dca161006f32db5df9ce2171be3046fa5553a0550708aba470f7e6be234c00be",                #swap fixed input tx
    '6': "2864dedd4b536d70280d055f6a7b19b3e78360d476ba1beed977c322a2022d5c"                 #aggregate tx
}

hash=hashes[idx]

if idx in {'1', '2', '3'}:
    txVisualization = TransactionVisualization.from_tx_hash_proxy(hash,proxi)       #devnet
else:
    txVisualization = TransactionVisualization.from_tx_hash(hash)                   #mainnet

txVisualization.draw_diagram()
