import json
import unittest
from multiversx_sdk import Address, ApiNetworkProvider
from transaction_diagram import DAddress, DContractResultItem, DTransactionEvent, DTransactionTransfer, TransactionVisualization
from multiversx_sdk.testutils.mock_network_provider import MockNetworkProvider
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork

class TestTransactionVisualization(unittest.TestCase):
    def setUp(self) -> None:
        #self.proxi = ApiNetworkProvider('https://devnet-api.multiversx.com')
        self.submit_batch_tx_hash = "0419c52371b6ea5e6c4985be96da87dca29896a1b2c4856c18ddd36767deb18f"
        self.update_tx_hash = "6f572f8e770c5d74b24323f6d0df624e9bd8d23ed3ec5088f814ea6b6381e551"
        self.reward_tx_hash = "3d5c1a2adbd6b362c749c1dfcde7aee269feeea8e5185aa15e08cef70cc39886"
        self.swap_tx_hash = "c6faf67c6655cae8114e4b86e4d8499108eed26bb868a1c0da6219aab2317381"
        self.aggregate_tx_hash = "2864dedd4b536d70280d055f6a7b19b3e78360d476ba1beed977c322a2022d5c"
        self.mockproxi = MockNetworkProvider()
        #Read transactions from json files and add them to the mockproxi:
        with open("./testdata/swap.json", 'r') as file:
            swap_data = json.load(file)
        with open("./testdata/aggregate.json", 'r') as file:
            aggregate_data = json.load(file)
        with open("./testdata/reward.json", 'r') as file:
            reward_data = json.load(file)
        with open("./testdata/update.json", 'r') as file:
            update_data = json.load(file)
        with open("./testdata/submit_batch.json", 'r') as file:
            submit_batch_data = json.load(file)
        self.mockproxi.mock_put_transaction(self.swap_tx_hash,TransactionOnNetwork.from_api_http_response(self.swap_tx_hash,swap_data))
        self.mockproxi.mock_put_transaction(self.aggregate_tx_hash,TransactionOnNetwork.from_api_http_response(self.aggregate_tx_hash,aggregate_data))
        self.mockproxi.mock_put_transaction(self.reward_tx_hash,TransactionOnNetwork.from_api_http_response(self.reward_tx_hash,reward_data))
        self.mockproxi.mock_put_transaction(self.update_tx_hash,TransactionOnNetwork.from_api_http_response(self.update_tx_hash,update_data))
        self.mockproxi.mock_put_transaction(self.submit_batch_tx_hash,TransactionOnNetwork.from_api_http_response(self.submit_batch_tx_hash,submit_batch_data))

    def test_reward_tx(self):
        #txv = TransactionVisualization.from_tx_hash_proxy(self.reward_tx_hash, self.proxi)
        txv = TransactionVisualization.from_tx_hash_proxy(self.reward_tx_hash, self.mockproxi)
        # Original transaction details
        self.assertEqual(txv.original_transaction.hash, self.reward_tx_hash)
        self.assertEqual(txv.original_transaction.function, 'reward')
        self.assertEqual(txv.original_transaction.receiver.to_bech32(), 'erd1qqqqqqqqqqqqqpgq60exvzsrz2qcdclvjzefthw84e05r52wd29q39yfjc')
        self.assertEqual(txv.original_transaction.sender.to_bech32(), 'erd1eckst7vrp9y82hxscjvpzcgpt9fyqvrggk7ky9xppfcqre3qz5vsjqk5kr')
        # Smart contract results
        self.assertEqual(len(txv.smart_contract_results),1)
        scr = DContractResultItem()
        scr.hash = "64dd6db95c5bc0ab2d99a415eadfe4b5ca1f686551134c732eb773c198da88e6"
        scr.sender = Address.from_bech32("erd1qqqqqqqqqqqqqpgq60exvzsrz2qcdclvjzefthw84e05r52wd29q39yfjc")
        scr.receiver = Address.from_bech32("erd1eckst7vrp9y82hxscjvpzcgpt9fyqvrggk7ky9xppfcqre3qz5vsjqk5kr")
        scr.previous_hash ="3d5c1a2adbd6b362c749c1dfcde7aee269feeea8e5185aa15e08cef70cc39886"
        scr.original_hash = "3d5c1a2adbd6b362c749c1dfcde7aee269feeea8e5185aa15e08cef70cc39886"
        self.assertIn(scr, txv.smart_contract_results)
        # Events
        self.assertEqual(len(txv.transaction_events),2)
        evt = DTransactionEvent()
        evt.identifier = "signalError"
        evt.address=Address.from_bech32("erd1qqqqqqqqqqqqqpgq60exvzsrz2qcdclvjzefthw84e05r52wd29q39yfjc")
        self.assertIn(evt,txv.transaction_events)
        evt.identifier = "internalVMErrors"
        evt.address = Address.from_bech32("erd1eckst7vrp9y82hxscjvpzcgpt9fyqvrggk7ky9xppfcqre3qz5vsjqk5kr")
        self.assertIn(evt,txv.transaction_events)
        #Transfers
        self.assertEqual(len(txv.transfers), 2)
        trsf = DTransactionTransfer()
        trsf.action = "transfer"
        trsf.name = "Tada"
        trsf.sender = Address.from_bech32("erd1qqqqqqqqqqqqqpgq60exvzsrz2qcdclvjzefthw84e05r52wd29q39yfjc")
        trsf.receiver = Address.from_bech32("erd1eckst7vrp9y82hxscjvpzcgpt9fyqvrggk7ky9xppfcqre3qz5vsjqk5kr")
        trsf.value = "753466216438356200"
        trsf.decimals = 18
        self.assertIn(trsf,txv.transfers)
        #Addresses
        self.assertEqual(len(txv.addresses), 2)
        self.assertIn(DAddress(scr.sender), txv.addresses)
        self.assertIn(DAddress(scr.receiver), txv.addresses)

    def test_update_tx(self):
        #txv = TransactionVisualization.from_tx_hash_proxy(self.update_tx_hash, self.proxi)
        txv = TransactionVisualization.from_tx_hash_proxy(self.update_tx_hash, self.mockproxi)
        # Original transaction details
        self.assertEqual(txv.original_transaction.hash, self.update_tx_hash)
        self.assertEqual(txv.original_transaction.function, 'update')
        self.assertEqual(txv.original_transaction.receiver.to_bech32(), 'erd1qqqqqqqqqqqqqpgq9j5chyk8zmjgj4ez4x92x5jq2s8h56yren6sj8zhsj')
        self.assertEqual(txv.original_transaction.sender.to_bech32(), 'erd1gpr403up2gs8any75pkjjf9t3p0hv6ry2hz4nmu8e35je4exq4gsar35pw')
        # Smart contract results
        self.assertEqual(len(txv.smart_contract_results),1)
        scr = DContractResultItem()
        scr.hash = "e5e1605974b7b5e2609a486841c152ce9c8fe425ea97102579e07f457b6b016b"
        scr.sender = Address.from_bech32("erd1qqqqqqqqqqqqqpgq9j5chyk8zmjgj4ez4x92x5jq2s8h56yren6sj8zhsj")
        scr.receiver = Address.from_bech32("erd1gpr403up2gs8any75pkjjf9t3p0hv6ry2hz4nmu8e35je4exq4gsar35pw")
        scr.previous_hash ="6f572f8e770c5d74b24323f6d0df624e9bd8d23ed3ec5088f814ea6b6381e551"
        scr.original_hash = "6f572f8e770c5d74b24323f6d0df624e9bd8d23ed3ec5088f814ea6b6381e551"
        self.assertIn(scr, txv.smart_contract_results)
        # Events
        self.assertEqual(len(txv.transaction_events),2)
        evt = DTransactionEvent()
        evt.identifier = "transferValueOnly"
        evt.address=Address.from_bech32("erd1qqqqqqqqqqqqqpgq9j5chyk8zmjgj4ez4x92x5jq2s8h56yren6sj8zhsj")
        self.assertIn(evt,txv.transaction_events)
        evt.identifier = "completedTxEvent"
        evt.address = Address.from_bech32("erd1qqqqqqqqqqqqqpgq9j5chyk8zmjgj4ez4x92x5jq2s8h56yren6sj8zhsj")
        self.assertIn(evt,txv.transaction_events)
        #Transfers
        self.assertEqual(len(txv.transfers), 1)
        trsf = DTransactionTransfer()
        trsf.action = "transfer"
        trsf.sender = Address.from_bech32("erd1qqqqqqqqqqqqqpgq9j5chyk8zmjgj4ez4x92x5jq2s8h56yren6sj8zhsj")
        trsf.receiver = Address.from_bech32("erd1qqqqqqqqqqqqqpgquyj0msy6dlsezqjp2ea0tljuvgwpc3gcen6s8aqwdn")
        trsf.value = "0"
        self.assertIn(trsf,txv.transfers)
        #Addresses
        self.assertEqual(len(txv.addresses), 3)
        self.assertIn(DAddress(scr.sender), txv.addresses)
        self.assertIn(DAddress(scr.receiver), txv.addresses)

    def test_batch_tx(self):
        #txv = TransactionVisualization.from_tx_hash_proxy(self.submit_batch_tx_hash, self.proxi)
        txv = TransactionVisualization.from_tx_hash_proxy(self.submit_batch_tx_hash, self.mockproxi)
        # Original transaction details
        self.assertEqual(txv.original_transaction.hash, self.submit_batch_tx_hash)
        self.assertEqual(txv.original_transaction.function, 'submitBatch')
        self.assertEqual(txv.original_transaction.receiver.to_bech32(), 'erd1qqqqqqqqqqqqqpgqgkr4sfm4dcmux9evu4xzxpujgzlavurmv5ysv7nflv')
        self.assertEqual(txv.original_transaction.sender.to_bech32(), 'erd13s63yrey07njylxug42tw0uwxgac8snejaj9vxtue2knjhs84xzslmzcds')
        # Smart contract results
        self.assertEqual(len(txv.smart_contract_results),1)
        scr = DContractResultItem()
        scr.hash = "db06225bec5c288f751a68c37eb15bcb51ca76fe56881a4031235880e3f6bda2"
        scr.sender = Address.from_bech32("erd1qqqqqqqqqqqqqpgqgkr4sfm4dcmux9evu4xzxpujgzlavurmv5ysv7nflv")
        scr.receiver = Address.from_bech32("erd13s63yrey07njylxug42tw0uwxgac8snejaj9vxtue2knjhs84xzslmzcds")
        scr.previous_hash ="0419c52371b6ea5e6c4985be96da87dca29896a1b2c4856c18ddd36767deb18f"
        scr.original_hash = "0419c52371b6ea5e6c4985be96da87dca29896a1b2c4856c18ddd36767deb18f"
        self.assertIn(scr, txv.smart_contract_results)
        # Events
        self.assertEqual(len(txv.transaction_events),3)
        evt = DTransactionEvent()
        evt.identifier = "submitBatch"
        evt.address=Address.from_bech32("erd1qqqqqqqqqqqqqpgqgkr4sfm4dcmux9evu4xzxpujgzlavurmv5ysv7nflv")
        self.assertIn(evt,txv.transaction_events)
        evt.identifier = "completedTxEvent"
        evt.address = Address.from_bech32("erd1qqqqqqqqqqqqqpgqgkr4sfm4dcmux9evu4xzxpujgzlavurmv5ysv7nflv")
        self.assertIn(evt,txv.transaction_events)
        #Transfers
        self.assertEqual(len(txv.transfers), 0)
        #Addresses
        self.assertEqual(len(txv.addresses), 2)
        self.assertIn(DAddress(scr.sender), txv.addresses)
        self.assertIn(DAddress(scr.receiver), txv.addresses)

    def test_swap_tx(self):
        txv = TransactionVisualization.from_tx_hash_proxy(self.swap_tx_hash, self.mockproxi)
        # Original transaction details
        self.assertEqual(txv.original_transaction.hash, self.swap_tx_hash)
        self.assertEqual(txv.original_transaction.function, 'swapTokensFixedOutput')
        self.assertEqual(txv.original_transaction.receiver.to_bech32(), 'erd1qqqqqqqqqqqqqpgqx6eg4kfqyw7ayktynn9wzhd6grv7p8542jpsj6y036')
        self.assertEqual(txv.original_transaction.sender.to_bech32(), 'erd1wyv2d22yrt6l44kymjggcess72wgs5s2u54fsc0kqj02u2zl340s83mljv')
        # Smart contract results
        self.assertEqual(len(txv.smart_contract_results),4)
        scr = DContractResultItem()
        scr.hash = "8c86eaeffcc66aa72d0fe883f9ac47a2d2e2be3c7b1b6fbdcc3966e27d7184fe"
        scr.sender = Address.from_bech32("erd1qqqqqqqqqqqqqpgqx6eg4kfqyw7ayktynn9wzhd6grv7p8542jpsj6y036")
        scr.receiver = Address.from_bech32("erd1wyv2d22yrt6l44kymjggcess72wgs5s2u54fsc0kqj02u2zl340s83mljv")
        scr.previous_hash ="c6faf67c6655cae8114e4b86e4d8499108eed26bb868a1c0da6219aab2317381"
        scr.original_hash = "c6faf67c6655cae8114e4b86e4d8499108eed26bb868a1c0da6219aab2317381"
        self.assertIn(scr, txv.smart_contract_results)
        # Events
        self.assertEqual(len(txv.transaction_events),8)
        evt = DTransactionEvent()
        evt.identifier = "ESDTLocalBurn"
        evt.address=Address.from_bech32("erd1qqqqqqqqqqqqqpgqa0fsfshnff4n76jhcye6k7uvd7qacsq42jpsp6shh2")
        self.assertIn(evt,txv.transaction_events)
        evt.identifier = "swapTokensFixedOutput"
        evt.address = Address.from_bech32("erd1qqqqqqqqqqqqqpgqx6eg4kfqyw7ayktynn9wzhd6grv7p8542jpsj6y036")
        self.assertIn(evt,txv.transaction_events)
        #Transfers
        self.assertEqual(len(txv.transfers), 5)
        trsf = DTransactionTransfer()
        trsf.action = "transfer"
        trsf.name = "WrappedEGLD"
        trsf.sender = Address.from_bech32("erd1qqqqqqqqqqqqqpgqx6eg4kfqyw7ayktynn9wzhd6grv7p8542jpsj6y036")
        trsf.receiver = Address.from_bech32("erd1wyv2d22yrt6l44kymjggcess72wgs5s2u54fsc0kqj02u2zl340s83mljv")
        trsf.value = "243841846311774"
        trsf.decimals = 18
        self.assertIn(trsf,txv.transfers)
        #Addresses
        self.assertEqual(len(txv.addresses), 3)
        self.assertIn(DAddress(scr.sender), txv.addresses)
        self.assertIn(DAddress(scr.receiver), txv.addresses)
        self.assertIn(DAddress(Address.from_bech32("erd1qqqqqqqqqqqqqpgqa0fsfshnff4n76jhcye6k7uvd7qacsq42jpsp6shh2")), txv.addresses)

    def test_aggregate_tx(self):
        txv = TransactionVisualization.from_tx_hash_proxy(self.aggregate_tx_hash, self.mockproxi)
        # Original transaction details
        self.assertEqual(txv.original_transaction.hash, self.aggregate_tx_hash)
        self.assertEqual(txv.original_transaction.function, 'aggregateEsdt')
        self.assertEqual(txv.original_transaction.receiver.to_bech32(), 'erd1qqqqqqqqqqqqqpgqcc69ts8409p3h77q5chsaqz57y6hugvc4fvs64k74v')
        self.assertEqual(txv.original_transaction.sender.to_bech32(), 'erd19dw6qeqyvn5ft7rqfzcds587j6u26n88kwkp0n0unnz7h2h6ds8qfpjmch')
        # Smart contract results
        self.assertEqual(len(txv.smart_contract_results),11)
        scr = DContractResultItem()
        scr.hash = "250efb9f7e766fa1f0d929859e0edd9258e208be1cee294212a263e316e259e7"
        scr.sender = Address.from_bech32("erd1qqqqqqqqqqqqqpgqt0uek344kaerr4gf9g2r8l0f4l8ygyha2jps82u9r6")
        scr.receiver = Address.from_bech32("erd1qqqqqqqqqqqqqpgqcc69ts8409p3h77q5chsaqz57y6hugvc4fvs64k74v")
        scr.previous_hash ="2864dedd4b536d70280d055f6a7b19b3e78360d476ba1beed977c322a2022d5c"
        scr.original_hash = "2864dedd4b536d70280d055f6a7b19b3e78360d476ba1beed977c322a2022d5c"
        self.assertIn(scr, txv.smart_contract_results)
        # Events
        self.assertEqual(len(txv.transaction_events),19)
        evt = DTransactionEvent()
        evt.identifier = "depositSwapFees"
        evt.address=Address.from_bech32("erd1qqqqqqqqqqqqqpgqjsnxqprks7qxfwkcg2m2v9hxkrchgm9akp2segrswt")
        self.assertIn(evt,txv.transaction_events)
        evt.identifier = "swapTokensFixedInput"
        evt.address = Address.from_bech32("erd1qqqqqqqqqqqqqpgqtjhhs49h0q2ncld64l3thtk7s7yuw47v2jps8emt0v")
        self.assertIn(evt,txv.transaction_events)
        #Transfers
        self.assertEqual(len(txv.transfers), 12)
        trsf = DTransactionTransfer()
        trsf.action = "transfer"
        trsf.name = "WrappedETH"
        trsf.sender = Address.from_bech32("erd1qqqqqqqqqqqqqpgqcc69ts8409p3h77q5chsaqz57y6hugvc4fvs64k74v")
        trsf.receiver = Address.from_bech32("erd19dw6qeqyvn5ft7rqfzcds587j6u26n88kwkp0n0unnz7h2h6ds8qfpjmch")
        trsf.value = "56132736706819"
        trsf.decimals = 18
        self.assertIn(trsf,txv.transfers)
        #Addresses
        self.assertEqual(len(txv.addresses), 6)
        self.assertIn(DAddress(scr.sender), txv.addresses)
        self.assertIn(DAddress(scr.receiver), txv.addresses)
        self.assertIn(DAddress(Address.from_bech32("erd1qqqqqqqqqqqqqpgqtjhhs49h0q2ncld64l3thtk7s7yuw47v2jps8emt0v")), txv.addresses)
        self.assertIn(DAddress(Address.from_bech32("erd1qqqqqqqqqqqqqpgqt0uek344kaerr4gf9g2r8l0f4l8ygyha2jps82u9r6")), txv.addresses)
        self.assertIn(DAddress(Address.from_bech32("erd1qqqqqqqqqqqqqpgqjsnxqprks7qxfwkcg2m2v9hxkrchgm9akp2segrswt")), txv.addresses)
        self.assertIn(DAddress(Address.from_bech32("erd1qqqqqqqqqqqqqpgqa0fsfshnff4n76jhcye6k7uvd7qacsq42jpsp6shh2")), txv.addresses)

if __name__ == '__main__':
    unittest.main()
