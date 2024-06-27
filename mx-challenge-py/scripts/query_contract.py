from pathlib import Path
from multiversx_sdk import Address, ProxyNetworkProvider, QueryRunnerAdapter, SmartContractQueriesController
from multiversx_sdk.abi import Abi

#####  QUERY ADDER CONTRACT

abi = Abi.load(Path("contract/adder/output/adder.abi.json"))
contract_address = Address.new_from_bech32('erd1qqqqqqqqqqqqqpgqulj8aetxs9kmnhhynpfyyvd2a88hkugp0x3sdezkjf')
query_runner = QueryRunnerAdapter(ProxyNetworkProvider("https://devnet-api.multiversx.com"))

query_controller = SmartContractQueriesController(query_runner, abi)

query = query_controller.create_query(
    contract=contract_address.to_bech32(),
    function="getSum",
    arguments=[],
)

response = query_controller.run_query(query)
data_parts = query_controller.parse_query_response(response)

print("Return code:", response.return_code)
print("Return data (raw):", response.return_data_parts)
print("Return data (parsed):", data_parts)