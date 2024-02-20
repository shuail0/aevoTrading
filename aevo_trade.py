import asyncio
import json
from aevo import AevoClient
from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv()



async def main():
    # ==================== 配置 ====================
    # 设置账户
    aevo = AevoClient(
        signing_key=os.getenv("SIGNING"), # 钱包私钥
        wallet_address=os.getenv("WALLETADDRESS"), # 钱包地址
        api_key=os.getenv("APIKEY"), # API key
        api_secret=os.getenv("APISECRET"), # API secret
        env="mainnet",
    )

    tradeAsset = 'ETH' # 设置交易币种
    quantity = 0.01  # 设置每次交易数量(单位：币)
    max_trade_number = 20  # 设置刷交易的次数，开平仓为一次
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
            
            print('第{}次交易结束'.format(number),'开始查询是否有未平仓位。')
            account_info = aevo.rest_get_account()
            positions = account_info['positions']
            if len(positions) > 0:
                # 找出instrument_name等于交易资产的position
                for position in positions:
                    if position['instrument_name'] == f'{tradeAsset}-PERP':
                        # 市价平仓
                        instrument_id, quantity, side = position['instrument_id'], float(position['amount']), position['side']
                        is_buy = True if side == 'sell' else False
                        limit_price = 2**200 - 1 if is_buy else 0
                        print(f'存在未平仓位，开始平仓,并取消所有挂单。instrument_id: {instrument_id}, quantity: {quantity}, is_buy: {is_buy}, limit_price: {limit_price}')
                        response = aevo.rest_create_order(instrument_id=instrument_id, is_buy=False, limit_price=limit_price, quantity=quantity, post_only=False)
                        aevo.rest_cancel_all_orders()
            # 暂停5秒
            await asyncio.sleep(5)
            
            if number >= max_trade_number:
                print('交易次数已达到上限，程序退出')
                exit()

if __name__ == "__main__":
    asyncio.run(main())
