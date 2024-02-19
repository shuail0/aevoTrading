import asyncio
import json
from aevo import AevoClient


async def main():
    # ==================== 配置 ====================
    # 设置账户
    aevo = AevoClient(
        signing_key="", # 钱包私钥
        wallet_address="", # 钱包地址
        api_key="", # API key
        api_secret="", # API secret
        env="mainnet",
    )

    tradeAsset = 'ETH' # 设置交易币种
    quantity = 0.2  # 设置每次交易数量(单位：币)
    max_trade_number = 50  # 设置刷交易的次数，开平仓为一次
    # ===============================================
    

    if not aevo.signing_key:
        raise Exception(
            "Signing key is not set. Please set the signing key in the AevoClient constructor."
        )
    
    markets = aevo.get_markets(tradeAsset)
    await aevo.open_connection()
    await aevo.subscribe_ticker(f"ticker:{tradeAsset}:PERPETUAL")
    number = 0
    async for msg in aevo.read_messages():
        data = json.loads(msg)["data"]
        # 如果数据里包含ticker，就执行交易
        if "tickers" in data:
            print('开始执行第{}次交易'.format(number + 1))
            bid_price = float(data["tickers"][0]['bid']['price'])
            ask_price = float(data["tickers"][0]['ask']['price'])
            price_step = float(markets[0]['price_step'])
            price_decimals = len(str(price_step).split('.')[1])
            limit_price = round((bid_price + ask_price) / 2, price_decimals)
            instrument_id = markets[0]['instrument_id']
            response = aevo.rest_create_order(instrument_id=instrument_id, is_buy=True, limit_price=limit_price, quantity=quantity, post_only=False)
            print(response)
            response = aevo.rest_create_order(instrument_id=instrument_id, is_buy=False, limit_price=limit_price, quantity=quantity, post_only=False)
            print(response)
            number += 1
            # 暂停5秒
            await asyncio.sleep(5)
            
            if number >= max_trade_number:
                print('交易次数已达到上限，程序退出')
                exit()

if __name__ == "__main__":
    asyncio.run(main())
