import secrets
from typing import TypedDict
import requests
from eth_account import Account
from eth_hash.auto import keccak as keccak_256
from eip712_structs import Address, EIP712Struct, Uint, make_domain
import pandas as pd


class Register(EIP712Struct):
    key = Address()
    expiry = Uint(256)


class SignKey(EIP712Struct):
    account = Address()


class AevoRegister(TypedDict):
    account: str
    signing_key: str
    expiry: str
    account_signature: str
    signing_key_signature: str


CONFIG = {
    "testnet": {
        "rest_url": "https://api-testnet.aevo.xyz",
        "ws_url": "wss://ws-testnet.aevo.xyz",
        "signing_domain": {
            "name": "Aevo Testnet",
            "version": "1",
            "chainId": "11155111",
        },
    },
    "mainnet": {
        "rest_url": "https://api.aevo.xyz",
        "ws_url": "wss://ws.aevo.xyz",
        "signing_domain": {
            "name": "Aevo Mainnet",
            "version": "1",
            "chainId": "1",
        },
    },
}

def generate_api_info(account_key, environment):
    domain = make_domain(**CONFIG[environment]["signing_domain"])

    account = Account.from_key(account_key)
    signing_key = secrets.token_hex(32)
    signing_key_account = Account.from_key(signing_key)

    expiry = 2**256 - 1

    sign_key = SignKey(account=account.address)
    register = Register(key=signing_key_account.address, expiry=expiry)

    sign_key_hash = keccak_256(sign_key.signable_bytes(domain=domain))
    signing_key_signature = Account._sign_hash(sign_key_hash, signing_key).signature.hex()

    register_hash = keccak_256(register.signable_bytes(domain=domain))
    account_signature = Account._sign_hash(register_hash, account_key).signature.hex()

    aevo_register: AevoRegister = {
        "account": account.address,
        "signing_key": signing_key_account.address,
        "expiry": str(expiry),
        "account_signature": account_signature,
        "signing_key_signature": signing_key_signature,
    }

    r = requests.post(f"{CONFIG[environment]['rest_url']}/register", json=aevo_register)
    j = r.json()

    api_info = {
        'signing_key': account_key,
        'wallet_address': account.address,
        'api_key': j['api_key'],
        'api_secret': j['api_secret'],
        'env': environment
    }
    return api_info

if __name__ == "__main__":
    input_path = '/Users/wr/Desktop/BOT/aevoTrading/data/input/aevoAccount.csv'  # 输入钱包私钥的路径
    output_path = '/Users/wr/Desktop/BOT/aevoTrading/data/output/api_keys.csv'  # 保存api_key的路径
    df = pd.read_csv(input_path)
    environment = "mainnet"
    apis = []
    # 遍历每一行
    for index, row in df.iterrows():
        account_key = row['PrivateKey']
        api_info = generate_api_info(account_key, environment)
        apis.append(api_info)
    df = pd.DataFrame(apis)
    df.to_csv(output_path, index=False)