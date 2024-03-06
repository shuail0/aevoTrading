# 期权交易策略 ：
#     - 查看买一卖一价差有多大，如果小于0.1%， 直接下市价单。
#     - 下单后，查询是否有未平仓位，如果有，市价平仓。
#     - 交易次数达到上限后，程序退出。

import asyncio
import json
from aevo import AevoClient
from dotenv import load_dotenv
import os




async def main():
    # 加载.env文件
    load_dotenv()

    # ==================== 交易配置 ====================
    quantity = 1  # 设置每次交易数量(单位：币)
    max_trade_number = 1000  # 设置刷交易的次数，开平仓为一次
    limit_price=0.3  # 订单价格,期权固定价格
    option_symbol = 'ETH-08MAR24-2650-P' # 期权合约名称
    # ===============================================
    
    
    aevo = AevoClient(
    signing_key=os.getenv("SIGNING"), # 钱包私钥
    wallet_address=os.getenv("WALLETADDRESS"), # 钱包地址
    api_key=os.getenv("APIKEY"), # API key
    api_secret=os.getenv("APISECRET"), # API secret
    env="mainnet",
    )



    if not aevo.signing_key:
        raise Exception(
            "Signing key is not set. Please set the signing key in the AevoClient constructor."
        )
    
    markets = aevo.get_markets(option_symbol)

    await aevo.open_connection()
    await aevo.subscribe_ticker(f"ticker:{option_symbol}")
    number = 0
    async for msg in aevo.read_messages():
        data = json.loads(msg)["data"]
    #     # 如果数据里包含ticker，就执行交易
        if "tickers" in data:
            print('开始执行第{}次交易'.format(number + 1))
            instrument_id = data["tickers"][0]['instrument_id']

            # 下卖单
            response = aevo.rest_create_order(instrument_id=instrument_id, is_buy=False, limit_price=limit_price, quantity=quantity, post_only=False)
            print(response)
            # 下买单
            response = aevo.rest_create_order(instrument_id=instrument_id, is_buy=True, limit_price=limit_price, quantity=quantity, post_only=False)
            print(response)
            
            # 暂停5秒
            number += 1
            # await asyncio.sleep(5)
            # aevo.rest_cancel_all_orders()
        
        if number >= max_trade_number:
            print('交易次数已达到上限，程序退出')
            exit()

if __name__ == "__main__":
    asyncio.run(main())
