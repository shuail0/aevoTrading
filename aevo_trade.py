import asyncio
import json

from loguru import logger

from aevo import AevoClient


async def main():
    # The following values which are used for authentication on private endpoints, can be retrieved from the Aevo UI
    aevo = AevoClient(
        signing_key="",
        wallet_address="",
        api_key="",
        api_secret="",
        env="mainnet",
    )
    aevo_2 = AevoClient(
    signing_key="",
    wallet_address="",
    api_key="",
    api_secret="",
    env="mainnet",
    )


    tradeAsset = 'ETH'
    max_trade_number = 10
    

    if not aevo.signing_key:
        raise Exception(
            "Signing key is not set. Please set the signing key in the AevoClient constructor."
        )
    
    markets = aevo.get_markets(tradeAsset)
    await aevo.open_connection()
    await aevo.subscribe_ticker(f"ticker:{tradeAsset}:PERPETUAL")
    open_position = True
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
            amount_step = float(markets[0]['amount_step'])
            amount_decimals = len(str(amount_step).split('.')[1])
            # quantity = round( 300 / limit_price, amount_decimals )
            quantity = 0.2

            if open_position:
                print('开始开仓')
                response = aevo.rest_create_order(instrument_id=instrument_id, is_buy=True, limit_price=limit_price, quantity=quantity, post_only=False)
                print(response)
                response = aevo_2.rest_create_order(instrument_id=instrument_id, is_buy=False, limit_price=limit_price, quantity=quantity, post_only=False)
                print(response)
                open_position = False
                # 暂停2秒
                await asyncio.sleep(5)
            else:
                print('开始平仓')
                response = aevo_2.rest_create_order(instrument_id=instrument_id, is_buy=True, limit_price=limit_price, quantity=quantity, post_only=False)
                print(response)
                response = aevo.rest_create_order(instrument_id=instrument_id, is_buy=False, limit_price=limit_price, quantity=quantity, post_only=False)
                print(response)
                open_position = True
                number += 1
            # 暂停2秒
            await asyncio.sleep(30)
                
            
            if number >= max_trade_number:
                print('交易次数已达到上限，程序退出')
                exit()

if __name__ == "__main__":
    asyncio.run(main())
