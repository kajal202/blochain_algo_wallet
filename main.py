from algosdk.v2client import algod
import json
import os
import hashlib
from algosdk import mnemonic
from algosdk import transaction
from algosdk import account, encoding, future

# py -m venv venv
# .\venv\Scripts\activate
#  py -m pip freeze > requirements.txt
# .\requirements.txt
# py -m pip install py-algorand-sdk<2.0

# find from purestake account
algod_token = ""
algod_address = ""
purestake_token = {"X-Api-key": algod_token}
algod_client = algod.AlgodClient(algod_token, algod_address, headers=purestake_token)


class FungToken:
    def __init__(self):
        params = algod_client.suggested_params()
        self.gh = params.gh
        self.params = (params,)
        self.first_valid_round = params.first
        self.last_valid_round = params.last
        self.fee = params.min_fee
        self.send_amount = 10
        self.note = "Hello World".encode()
        self.send_to_address = (
            "ICO3XHZSIZTQ5N32VHZ6ORF3QG7QFJNHTHNECCYB4KNUKT725GP5NLQGUU"
        )

    def CreateAccount(self):
        self.private_key, self.address = account.generate_account()
        self.account_public_key = mnemonic.from_private_key(self.private_key)
        self.existing_account = self.account_public_key

        print("Private key:", self.private_key)
        print("Address:", self.address)
        print("Public Key", self.account_public_key)

        # check if the address is valid
        if encoding.is_valid_address(self.address):
            print("The address is valid!")
        else:
            print("The address is invalid.")
        self.Balance(self.address)

    def Balance(self, address):
        account_info = algod_client.account_info(address)
        print("Account balance: {} microAlgos".format(account_info.get("amount")))

    def Recover(self, mnemonic_phrase):
        account_private_key = mnemonic.to_private_key(mnemonic_phrase)
        return (account_private_key,)  # account_public_key

    def SendTransaction(self, addr, private_key):
        tx = transaction.PaymentTxn(
            addr,
            self.fee,
            self.first_valid_round,
            self.last_valid_round,
            self.gh,
            self.send_to_address,
            self.send_amount,
        )
        signed_tx = tx.sign(private_key)

        try:
            tx_confirm = algod_client.send_transaction(signed_tx)
            print(tx_confirm)
            # print('Transaction sent with ID', signed_tx.transaction.get_txid())
            self.wait_for_confirmation(
                algod_client, txid=signed_tx.transaction.get_txid()
            )
        except Exception as e:
            print(e)

    # Function from Algorand Inc. - utility for waiting on a transaction confirmation
    def wait_for_confirmation(algod_client, txid):
        last_round = algod_client.status().get("last-round")
        txinfo = algod_client.pending_transaction_info(txid)
        while not (txinfo.get("confirmed-round") and txinfo.get("confirmed-round") > 0):
            print("Waiting for confirmation")
            last_round += 1
            algod_client.status_after_block(last_round)
            txinfo = algod_client.pending_transaction_info(txid)
        print("Transaction confirmed in round", txinfo.get("confirmed-round"))
        return txinfo

    def CreateAsset(self, address, qnt, dcml, private_key):
        txn = transaction.AssetConfigTxn(
            sender=address,
            fee=self.fee,
            first=self.first_valid_round,
            last=self.last_valid_round,
            gh=self.gh,
            default_frozen=False,
            unit_name="rug",
            asset_name="Really Useful Gift",
            manager=address,
            reserve=address,
            freeze=address,
            clawback=address,
            # url="https://path/to/my/asset/details",
            total=qnt,
            decimals=dcml,
        )
        # Sign with secret key of creator
        stxn = txn.sign(private_key)
        # Send the transaction to the network and retrieve the txid.
        txid = algod_client.send_transaction(stxn)
        print(f"Sent asset create transaction with txid: {txid}")
        # results = transaction.wait_for_confirmation(algod_client, txid, 4)
        # results =self.wait_for_confirmation(algod_client, txid=txid)
        # print(f"Result confirmed in round: {results['confirmed-round']}")
        # # grab the asset id for the asset we just created
        # created_asset = results["asset-index"]
        # print(f"Asset ID created: {created_asset}")

    def ModifyAsset(self, address, private_key):
        txn = transaction.AssetConfigTxn(
            index=257498180,
            sender=address,
            fee=self.fee,
            first=self.first_valid_round,
            last=self.last_valid_round,
            gh=self.gh,
            manager=address,
            reserve=None,
            freeze=address,
            clawback=address,
            strict_empty_address_check=False,
        )
        # Sign with secret key of manager
        stxn = txn.sign(private_key)
        # Send the transaction to the network and retrieve the txid.
        txid = algod_client.send_transaction(stxn)
        print(f"Sent asset config transaction with txid: {txid}")
        # Wait for the transaction to be confirmed
        # results = transaction.wait_for_confirmation(algod_client, txid, 4)
        # print(f"Result confirmed in round: {results['confirmed-round']}")

    def OptInAsset(self, address, private_key):  # sending asset
        self.sp = algod_client.suggested_params()
        optin_txn = future.transaction.AssetOptInTxn(
            sender=address,
            sp=self.sp,
            index=258248297,
        )
        signed_optin_txn = optin_txn.sign(private_key)
        txid = algod_client.send_transaction(signed_optin_txn)
        print(f"Sent opt in transaction with txid: {txid}")
        # Wait for the transaction to be confirmed
        # results = transaction.wait_for_confirmation(algod_client, txid, 4)
        # print(f"Result confirmed in round: {results['confirmed-round']}")

    def SendAsset(self, address, private_key):  # sending asset, sender address
        raddress = "LSXJ4AICLZTLRXBS3QKORNWWWF6AAQL6E7VRS56T3ZAJOWX4SRW6K5VXWA"
        rprivate_key = "YWsPO+pyYJW9YwSSiuPJwWt/el9DmgjYpPUrr25cIndcrp4BAl5muNwy3BTottaxfABBfifrGXfT3kCXWvyUbQ=="
        self.OptInAsset(raddress, rprivate_key)
        optin_txn = transaction.AssetTransferTxn(
            receiver=raddress,
            fee=self.fee,
            first=self.first_valid_round,
            last=self.last_valid_round,
            gh=self.gh,
            index=258248297,
            amt=10000,
            sender=address,
        )
        signed_optin_txn = optin_txn.sign(private_key)
        txid = algod_client.send_transaction(signed_optin_txn)
        print(f"Send transaction with txid: {txid}")

    def FreezeAsset(self, address, private_key):
        self.sp = algod_client.suggested_params()
        freeze_txn = future.transaction.AssetFreezeTxn(
            sender=address,
            sp=self.sp,
            index=258248297,
            target=address,
            new_freeze_state=True,
        )
        signed_freeze_txn = freeze_txn.sign(private_key)
        txid = algod_client.send_transaction(signed_freeze_txn)
        print(f"Sent freeze transaction with txid: {txid}")

        results = future.transaction.wait_for_confirmation(algod_client, txid, 4)
        print(f"Result confirmed in round: {results['confirmed-round']}")

    def UnFreezeAsset(self, address, private_key):
        self.sp = algod_client.suggested_params()
        freeze_txn = future.transaction.AssetFreezeTxn(
            sender=address,
            sp=self.sp,
            index=258248297,
            target=address,
            new_freeze_state=False,
        )
        signed_freeze_txn = freeze_txn.sign(private_key)
        txid = algod_client.send_transaction(signed_freeze_txn)
        print(f"Sent freeze transaction with txid: {txid}")

        results = future.transaction.wait_for_confirmation(algod_client, txid, 4)
        print(f"Result confirmed in round: {results['confirmed-round']}")

    def RevokeAsset(self, address, private_key, amt):
        raddress = "LSXJ4AICLZTLRXBS3QKORNWWWF6AAQL6E7VRS56T3ZAJOWX4SRW6K5VXWA"
        optin_txn = transaction.AssetTransferTxn(
            receiver=address,
            fee=self.fee,
            first=self.first_valid_round,
            last=self.last_valid_round,
            gh=self.gh,
            index=258248297,
            amt=amt,
            sender=address,
            revocation_target=raddress,
        )
        signed_optin_txn = optin_txn.sign(private_key)
        txid = algod_client.send_transaction(signed_optin_txn)
        print(f"Send transaction with txid: {txid}")

    def OptOutAsset(self, address):  # sending asset
        raddress = "LSXJ4AICLZTLRXBS3QKORNWWWF6AAQL6E7VRS56T3ZAJOWX4SRW6K5VXWA"
        rprivate_key = "YWsPO+pyYJW9YwSSiuPJwWt/el9DmgjYpPUrr25cIndcrp4BAl5muNwy3BTottaxfABBfifrGXfT3kCXWvyUbQ=="
        optout_txn = transaction.AssetTransferTxn(
            sender=raddress,
            fee=self.fee,
            first=self.first_valid_round,
            last=self.last_valid_round,
            gh=self.gh,
            index=258248297,
            receiver=address,
            close_assets_to=address,
            amt=0,
        )
        signed_optout_txn = optout_txn.sign(rprivate_key)
        txid = algod_client.send_transaction(signed_optout_txn)
        print(f"Sent opt in transaction with txid: {txid}")

    def DeleteAsset(self, address, private_key):
        sp = algod_client.suggested_params()
        destroy_txn = future.transaction.AssetDestroyTxn(
            sender=address,
            sp=sp,
            index=258248297,
        )
        signed_destroy_txn = destroy_txn.sign(private_key)
        txid = algod_client.send_transaction(signed_destroy_txn)
        print(f"Sent destroy transaction with txid: {txid}")

        results = future.transaction.wait_for_confirmation(algod_client, txid, 4)
        print(f"Result confirmed in round: {results['confirmed-round']}")

        try:
            info = algod_client.asset_info(258248297)
            print(info)
        except Exception as e:
            print("Expected Error:", e)


"""
class NonFungToken():
    def __init__(self):
        params = algod_client.suggested_params()  
        self.gh = params.gh 
        self.params= params,
        self.first_valid_round = params.first  
        self.last_valid_round = params.last  
        self.fee = params.min_fee  
        self.send_amount = 10
        self.note = "Hello World".encode()   
        self.send_to_address = (
            "ICO3XHZSIZTQ5N32VHZ6ORF3QG7QFJNHTHNECCYB4KNUKT725GP5NLQGUU"
        ) 

    def ReadJSON(self):
        #JSON FILE    
        dir_path = os.path.dirname(os.path.realpath(__file__))    
        f = open (dir_path + '/nft.json', "r")    
            
        #Reading from File    
        metadataJSON = json.loads(f.read())    
        metadataStr = json.dumps(metadataJSON)    
            
        hash = hashlib.new("sha512_256")    
        hash.update(b"arc0003/amj")    
        hash.update(metadataStr.encode("utf-8"))    
        json_metadata_hash = hash.digest()
        return json_metadata_hash

    def MintNFT(self, address, private_key):
        params = algod_client.suggested_params()
        txn = future.transaction.AssetConfigTxn(
            sender=address,
            sp=params,
            total=1,
            default_frozen=False,
            unit_name="TESTNFT",
            asset_name="Algorand Test NFT",
            manager=address,
            reserve=None,
            freeze=None,
            clawback=None,
            strict_empty_address_check=False,
            url="https://path/to/my/asset/details",
            metadata_hash=self.ReadJSON(),
            decimals=0,
        )
         # Sign with secret key of creator
        try:
            stxn = txn.sign(private_key)

            # Send the transaction to the network and retrieve the txid.
            txid = algod_client.send_transaction(stxn)
            print("Asset Creation Transaction ID: {}".format(txid))

            # Wait for the transaction to be confirmed
            confirmed_txn = future.transaction.wait_for_confirmation(algod_client, txid, 4)
            print("TXID: ", txid)
            print("Result confirmed in round: {}".format(confirmed_txn["confirmed-round"]))
        except Exception as e:
            print(e)

        try:
            ptx = algod_client.pending_transaction_info(txid)
            NFTId = ptx["asset-index"]
            self.print_created_asset(addr, NFTId)
            self.print_asset_holding(addr, NFTId)
        except Exception as e:
            print(e)

    def print_created_asset(self, account, assetid):
        account_info = algod_client.account_info(account)
        idx = 0
        for my_account_info in account_info["created-assets"]:
            scrutinized_asset = account_info["created-assets"][idx]
            idx = idx + 1
            if scrutinized_asset["index"] == assetid:
                print("Asset ID: {}".format(scrutinized_asset["index"]))
                print(json.dumps(my_account_info["params"], indent=4))
            break
    
    def print_asset_holding(self, account, assetid):
        account_info = algod_client.account_info(account)
        idx = 0
        for account_info in account_info["assets"]:
            scrutinized_asset = account_info["assets"][idx]
            idx = idx + 1
            if scrutinized_asset["asset-id"] == assetid:
                print("Asset ID: {}".format(scrutinized_asset["asset-id"]))
                print(json.dumps(scrutinized_asset, indent=4))
                break
"""

if __name__ == "__main__":
    fungToken = FungToken()
    # fungToken.CreateAccount()
    public_key = "fox canal gift curious trust actor jelly ozone south super spider return lamp render elevator burst quarter almost nasty initial couch warrior smoke abstract pluck"
    addr = "R4EPC3ZF64ZAG6WZAEMLPGDDDEKU3FPJT5KAVLJMAPFOQC5VECKOJXLFBI"
    private_key = "4kKIw17T9Ar4jp6Bbnajg2s+2P7IHnu1QSY/dxjdm/mPCPFvJfcyA3rZARi3mGMZFU2V6Z9UCq0sA8roC7UglA=="
    if addr != "":
        fungToken.Balance(addr)  # 2nd
        fungToken.SendTransaction(addr, private_key)
    #        fungToken.SendTransaction(addr, private_key) #3rd
    #        fungToken.CreateAsset(addr, 10000000, 6, private_key)
    #        fungToken.ModifyAsset(addr, private_key)
    #        fungToken.SendAsset(addr, private_key)
    #        fungToken.FreezeAsset(addr, private_key)
    #        fungToken.UnFreezeAsset(addr, private_key)
    #        fungToken.RevokeAsset(addr, private_key, 1)
    #        fungToken.OptOutAsset(addr)
    #        fungToken.DeleteAsset(addr, private_key)
    else:
        fungToken.CreateAccount()  # 1st
    # print(fungToken.Recover('accuse simple piece salute north scheme spy price daughter quality reduce fiber danger large bacon path thumb kite eyebrow turtle below lounge nerve above buzz'))

    # nonFungToken = NonFungToken()
    # nonFungToken.MintNFT(addr, private_key)
