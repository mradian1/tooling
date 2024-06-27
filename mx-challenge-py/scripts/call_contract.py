from pathlib import Path
from multiversx_sdk import AccountNonceHolder, Address, ApiNetworkProvider, SmartContractTransactionsFactory, TransactionComputer, TransactionsFactoryConfig, UserSigner, UserWallet
from multiversx_sdk.abi import U32Value, Abi

#####  CALL ADDER CONTRACT
transaction_computer=TransactionComputer()

abi = Abi.load(Path("contract/adder/output/adder.abi.json"))                                            #abi json for contract
secret_key = UserWallet.load_secret_key(Path("./wallet/test_wallet.json"), "misu", address_index=0)
deployer_address = secret_key.generate_public_key().to_address("erd")                                   #address from wallet
# ('erd13ea605vwj79w3kwnukregqanj4ptasdjtytfxnt3az77fvjv0x3syhvdrl')
api=ApiNetworkProvider('https://devnet-api.multiversx.com')
signer=UserSigner.from_wallet(Path("./wallet/test_wallet.json"), "misu")
args=[42]
config_data = TransactionsFactoryConfig(chain_id="D")
factory = SmartContractTransactionsFactory(config_data, abi)
contract_address = Address.new_from_bech32('erd1qqqqqqqqqqqqqpgqulj8aetxs9kmnhhynpfyyvd2a88hkugp0x3sdezkjf')

#Call contract transaction 1
execute_transaction1 = factory.create_transaction_for_execute(
    sender=deployer_address,
    contract=contract_address,
    function="add",
    gas_limit=10000000,
    arguments=args,
)
#Call contract transaction 2
execute_transaction2 = factory.create_transaction_for_execute(
    sender=deployer_address,
    contract=contract_address,
    function="add",
    gas_limit=10000000,
    arguments=args,
)

#Set nonce
deployer_address_on_network = api.get_account(deployer_address)
nonce_holder = AccountNonceHolder(deployer_address_on_network.nonce)
execute_transaction1.nonce= nonce_holder.get_nonce_then_increment()
execute_transaction2.nonce= nonce_holder.get_nonce_then_increment()

#Sign & send call transactions
execute_transaction1.signature = signer.sign(transaction_computer.compute_bytes_for_signing(execute_transaction1))
print("Execute Tx1 signature:", execute_transaction1.signature.hex())
execute_transaction2.signature = signer.sign(transaction_computer.compute_bytes_for_signing(execute_transaction2))
print("Execaute Tx2 signature:", execute_transaction2.signature.hex())

tx_hash = api.send_transaction(execute_transaction1)
print("Execute transaction1 hash:", tx_hash)
tx_hash = api.send_transaction(execute_transaction2)
print("Execute transaction2 hash:", tx_hash)