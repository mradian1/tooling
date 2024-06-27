from pathlib import Path
from multiversx_sdk import AccountNonceHolder, Address, AddressComputer, ApiNetworkProvider, TransactionComputer, TransactionsConverter, TransactionsFactoryConfig, UserSigner, UserWallet
from multiversx_sdk import SmartContractTransactionsFactory
from multiversx_sdk.abi import U32Value, Abi

transaction_converter = TransactionsConverter()
transaction_computer=TransactionComputer()
bytecode = Path("contract/adder/output/adder.wasm").read_bytes()                                        #built contract
abi = Abi.load(Path("contract/adder/output/adder.abi.json"))                                            #abi json for contract
secret_key = UserWallet.load_secret_key(Path("./wallet/test_wallet.json"), "misu", address_index=0)
deployer_address = secret_key.generate_public_key().to_address("erd")                                   #address from wallet

config_data = TransactionsFactoryConfig(chain_id="D")
factory = SmartContractTransactionsFactory(config_data, abi)                                            #transaction factory

args=[42]

#####  DEPLOY CONTRACT TRANSACTION
deploy_transaction = factory.create_transaction_for_deploy(
    sender=deployer_address,
    bytecode=bytecode,
    arguments=args,
    gas_limit=10000000,
    is_upgradeable=True,
    is_readable=True,
    is_payable=True,
    is_payable_by_sc=True,
)

api=ApiNetworkProvider('https://devnet-api.multiversx.com')
signer=UserSigner.from_wallet(Path("./wallet/test_wallet.json"), "misu")
#Sign & broadcast contract
deploy_transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(deploy_transaction))
print("Contract signature:", deploy_transaction.signature.hex())
tx_hash = api.send_transaction(deploy_transaction)
print("Transaction hash:", tx_hash)

address_computer = AddressComputer()
contract_address = address_computer.compute_contract_address(
    deployer=Address.new_from_bech32(deploy_transaction.sender),
    deployment_nonce=deploy_transaction.nonce
)
print("Contract address:", contract_address.to_bech32())


