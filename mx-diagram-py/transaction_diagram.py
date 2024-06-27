from typing import Any, Dict
from graphviz import Digraph
from multiversx_sdk import ApiNetworkProvider
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork
from multiversx_sdk.network_providers.contract_results import ContractResultItem
from multiversx_sdk.network_providers.transaction_events import TransactionEvent
from multiversx_sdk.core.address import Address
from multiversx_sdk.network_providers.resources import EmptyAddress
#from pprint import pprint

###################################################################################################
#                                                                                                 #
#   Use:                                                                                          #
#   TransactionVisualization.from_tx_hash_proxy(hash,proxi).draw_diagram()                        #
#                           or                                                                    #
#   TransactionVisualization.from_hash(hash).draw_diagram()                                       #
#                                                                                                 #
###################################################################################################

# class containing fields in ContractResultItem that are used in the visual representation of the transaction
def to_prefix_sufix_form(aString: str):
    return f"{aString[:8]}...{aString[-8:]}"

class DContractResultItem:
    def __init__(self) -> None:
        self.hash = ''
        self.previous_hash = ''
        self.original_hash = ''
        self.sender = EmptyAddress()
        self.receiver = EmptyAddress()
    #Diagram label for smart contract result:
    def __str__(self) -> str:
        return to_prefix_sufix_form(self.hash)
    #Object equality for testing purposes:
    def __eq__(self, value: object) -> bool:
        if isinstance(value, DContractResultItem):
            return (value.hash == self.hash and value.previous_hash == self.previous_hash and value.original_hash == self.original_hash
                    and value.receiver.to_bech32()==self.receiver.to_bech32() and value.sender.to_bech32()==self.sender.to_bech32())
        return False
    #Object renderer from ContractResultItem in TransactionOnNetwork object's ContractResults:
    @staticmethod
    def from_contract_result_item(cntr: ContractResultItem) -> 'DContractResultItem':
        result=DContractResultItem()
        result.hash = cntr.hash
        result.previous_hash = cntr.previous_hash
        result.original_hash = cntr.original_hash
        result.sender = cntr.sender
        result.receiver = cntr.receiver
        return result

class DTransactionEvent:
    def __init__(self) -> None:
        self.identifier = ''
        self.address = EmptyAddress()
    #Diagram label for event:
    def __str__(self) -> str:
        return self.identifier
    def __eq__(self, value: object) -> bool:
        if isinstance(value, DTransactionEvent):
            return value.identifier == self.identifier and value.address.to_bech32()==self.address.to_bech32()
        return False
    #Object renderer from TransactionEvent item in TransactionOnNetwork object:
    @staticmethod
    def from_transaction_event(event: TransactionEvent) -> 'DTransactionEvent':
        result = DTransactionEvent()
        result.identifier = event.identifier
        result.address = event.address
        return result

class DTransactionTransfer:
    def __init__(self) -> None:
        self.receiver = EmptyAddress()
        self.sender = EmptyAddress()
        self.name = ''
        self.value = ''
        self.decimals = ''
        self.action = ''
    #Diagram label for transfer:
    def __str__(self) -> str:
        return self.action + " :\n " + self.value + " " + self.name
    def __eq__(self, value: object) -> bool:
        if isinstance(value, DTransactionTransfer):
            return (value.action == self.action and value.name == self.name and value.value == self.value and value.decimals == self.decimals
                    and value.receiver.to_bech32() == self.receiver.to_bech32() and value.sender.to_bech32() == self.sender.to_bech32())
        return False
    #Object renderer from http_response in TransactionOnNetwork object:
    @staticmethod
    def from_http_response(response:Dict[str, Any]) -> 'DTransactionTransfer':
        result = DTransactionTransfer()
        receiver = response.get('receiver', '')
        result.receiver = Address.new_from_bech32(receiver) if receiver else EmptyAddress()
        sender = response.get('sender', '')
        result.sender = Address.new_from_bech32(sender) if sender else EmptyAddress()

        result.name = response.get('name', '')
        result.value = response.get('value', '')
        result.decimals = response.get('decimals', '')
        result.action = response.get('action', '')
        return result

class DAddress:
    def __init__(self, address: Address) -> None:
        self.address = address
    #Object equality for uniquelly adding addresses as well as testing:
    def __eq__(self, value: object) -> bool:
        if isinstance(value, DAddress):
            return value.address.to_bech32() == self.address.to_bech32()
        return False
    #Diagram label for addresses:
    def __str__(self) -> str:
        return to_prefix_sufix_form(self.address.to_bech32())

class DOriginalTransaction:
    def __init__(self) -> None:
        self.hash = ''
        self.sender = EmptyAddress()
        self.receiver = EmptyAddress()
        self.function = ''
    #Diagram label for original transaction:
    def __str__(self) -> str:
        return to_prefix_sufix_form(self.hash) + " ( " + self.function + " ) "
    #Object renderer from details in TransactionOnNetwork object:
    @staticmethod
    def from_transaction_on_network(tx: TransactionOnNetwork) -> 'DOriginalTransaction':
        result = DOriginalTransaction()
        result.hash = tx.hash
        result.sender = tx.sender
        result.receiver = tx.receiver
        result.function = tx.function
        return result

class TransactionVisualization:
    def __init__(self):
        self.original_transaction = DOriginalTransaction()
        self.smart_contract_results: list[DContractResultItem] = []
        self.transaction_events: list[DTransactionEvent] = []
        self.transfers: list[DTransactionTransfer]= []
        self.addresses: list[DAddress] = []

    def to_formated_address(self, address: Address):
        return to_prefix_sufix_form(address.to_bech32())

    def draw_diagram(self):
        # Create a new graph
        dot = Digraph(comment='Transaction Visualization')
        dot.attr(rankdir='TB')

        dot.node(name=self.original_transaction.hash, shape='rectangle', style= 'filled', color='lightgrey', label=str(self.original_transaction))
        # Add cluster for SCRs
        with dot.subgraph(name='cluster_results') as c:
            c.attr(color='red')
            c.attr(rankdir='TB')
            c.node_attr.update(style='filled', color='darksalmon')
            c.attr(label='Smart Contract Results')
            c.attr(rank='same')
            #c.attr(cluster=True)
            for ctr in self.smart_contract_results:
                c.node(name = ctr.hash, shape='rectangle', label=str(ctr))
                #for the SCRs to lay vertically in the diagram, draw invisible edges between them:
                idx=self.smart_contract_results.index(ctr)
                if idx>0:
                    c.edge(self.smart_contract_results[idx-1].hash, ctr.hash, style='invis')

        # Add cluster for addresses
        with dot.subgraph(name='cluster_addresses') as c:
            c.attr(color='blue')
            c.node_attr.update(style='filled', color='darkslategray1')
            c.attr(label='Addresses')
            c.attr(rank='same')
            c.attr(rankdir='TB')
            for addr in self.addresses:
                c.node(name = addr.address.to_bech32(), shape='rectangle', label=str(addr))

        # Add cluster for events
        with dot.subgraph(name='cluster_events') as c:
            c.attr(color='blue')
            c.node_attr.update(style='filled', color='darkslategray1')
            c.attr(label='Events')
            c.attr(rank='same')
            for evt in self.transaction_events:
                evt_idx=self.transaction_events.index(evt)
                evt_name="E"+str(evt_idx)
                c.node(name = evt_name, shape='rectangle', label=str(evt))

        # Draw edges for transfers
        for trsf in self.transfers:
            dot.edge(trsf.sender.to_bech32(), trsf.receiver.to_bech32(), label=str(trsf))
        #Draw other edges
        for ctr in self.smart_contract_results:
            dot.edge(ctr.hash, ctr.previous_hash)
            dot.edge(ctr.sender.to_bech32(), ctr.hash)
            dot.edge(ctr.hash, ctr.receiver.to_bech32())
        for evt in self.transaction_events:
            evt_idx=self.transaction_events.index(evt)
            evt_name="E"+str(evt_idx)
            dot.edge(evt.address.to_bech32(), evt_name)

        # Render the graph
        file_name= 'transaction-visualization'+to_prefix_sufix_form(self.original_transaction.hash)
        dot.render(file_name, format='png', view=False)


    @staticmethod
    def from_tx_hash_proxy(txHash:str, proxy:ApiNetworkProvider) -> 'TransactionVisualization':
        result = TransactionVisualization()
        tx : TransactionOnNetwork = proxy.get_transaction(txHash)              #the original form of the transaction
        # retain necessary fields related to the original transaction:
        result.original_transaction = DOriginalTransaction.from_transaction_on_network(tx)
        # retain from ContractResults in original transaction necessary fields for each item:
        result.smart_contract_results = [DContractResultItem.from_contract_result_item(item) for item in tx.contract_results.items]
        # retain from list of events in original transaction logs necessary fields for each event:
        result.transaction_events = [DTransactionEvent.from_transaction_event(item) for item in tx.logs.events]
        # retain from operations in original http_response, necessary fields for each relevant item (ignoring logging operations):
        operations = tx.raw_response.get('operations', [])
        result.transfers = [DTransactionTransfer.from_http_response(item) for item in filter(lambda x: x.get('action','')!='writeLog' ,operations)]
        # add addresses involved in transaction:
        addrs = []
        addrs.append(DAddress(result.original_transaction.sender))
        #addresses associated with smart contract results:
        for res in result.smart_contract_results:
            if DAddress(res.sender) not in addrs:
                addrs.append(DAddress(res.sender))
            if DAddress(res.receiver) not in addrs:
                addrs.append(DAddress(res.receiver))
        #addresses associated with transfers
        for res in result.transfers:
            if DAddress(res.sender) not in addrs:
                addrs.append(DAddress(res.sender))
            if DAddress(res.receiver) not in addrs:
                addrs.append(DAddress(res.receiver))
        #addresses associated with events:
        for res in result.transaction_events:
            if DAddress(res.address) not in addrs:
                addrs.append(DAddress(res.address))
        if DAddress(result.original_transaction.receiver) not in addrs:
            addrs.append(DAddress(result.original_transaction.receiver))
        result.addresses = addrs
        return result

    @staticmethod
    def from_tx_hash(txHash:str) -> 'TransactionVisualization':
        proxy = ApiNetworkProvider("https://api.multiversx.com")
        return TransactionVisualization.from_tx_hash_proxy(txHash, proxy)
