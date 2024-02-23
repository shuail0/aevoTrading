# AEVO 刷交易量程序

# 更新记录

## 2024/2/22

增加使用市价单成交的策略，用市价成交比原来的策略成本要低（在ETH刷10万U交易成本20U以内）并且能减少挂单无法成交导致长时间持仓产生亏损，代码在`aevo_market_price_trade.py`：

 - 检查盘口买卖价差是否低于0.05%，如果低于开始交易。
 - 以市价卖出，并以卖一价格*1.02买入平仓。
 - 检查账户有没有持仓，如果有持仓以市价平仓。

## 2024/2/20
增加订单检测，每次交易完成检查是否空仓，如果不是空仓市价平仓并取消所有挂单。

# 项目介绍

AEVO是一个去中心化衍生品交易平台，主要交易品种是永续合约和期权。项目前身是Ribbon Finance，项目获得了Paradigm、Dragonfly和Coinbase等资本方的投资，项目最近上合约的速度非常快，很多项目在。

项目原先发过一个RBN的代币，并且21年发过一次空投，平均一个地址空投了50万RMB。未来老币RBN将置换成AEVO，根据文档中的描述，项目代币中16%的代币用于激励（包括空投），AEVO代币总量10亿枚，按照目前RBN的币价，这部分价值8000万U左右。

项目最近上了一个按交易量空投的活动。空投根据用户的空投交易量发放，空投交易量=交易量*boost因子，boost因子根据最近的7天交易量计算，交易越多提升越高。

具体的规则可以在这里查看：https://aevo.mirror.xyz/pVCrIjnPwDkC7h16vr_Ca__AdsXL31ZL2VylkICX0Ss 




# AEVO账户准备

项目链接：

 - 官方链接：https://app.aevo.xyz/perpetual/ilv
 - 我的邀请链接：https://app.aevo.xyz/r/Roan-Elastic-Nakamoto

连接钱包后存入USDC，OP或者Arbitrum网络的都可以，费用都很低。

![image-20240219175549654](https://s2.loli.net/2024/02/19/nEeOGIydctkHRj9.png)

![image-20240219173411045](https://s2.loli.net/2024/02/19/DRpF82oZ3VP4NJy.png)



# 创建API

API可以直接在网站上创建或通过代码创建, 钱包数量少可以直接在网页创建，钱包多的可以用我的代码批量创建。

## 在网页中创建

访问：https://app.aevo.xyz/settings/api-keys

点击 Creaate API创建API，创建完成后可以点击API Key和APISecret复制。第一次复制Secret的时候需要在小狐狸签名确认。

![image-20240219174644354](https://s2.loli.net/2024/02/19/4JVzcHrZMx9pE7X.png)

![image-20240219174946898](https://s2.loli.net/2024/02/19/Q4dzXfoL3S1e7B9.png)



# 使用代码创建

用create_apiKey.py代码可以批量创建API，按照data/input目录下的aevoAccount.csv编辑自己的钱包文件，然后将路径填写到代码中，然后运行create_apiKey.py即可。

![image-20240219180019364](https://s2.loli.net/2024/02/19/EIPhs8g4fT6coWS.png)

# 刷交易代码

## 刷交易策略

交易策略是根据设置的品种和交易币数同时挂买卖单，挂单价格是买一和卖一的中间价，交易达到指定次数后程序停止运行。

## 程序执行

首先在代码目录下创建一个`.env`文件，然后按照下面的格式填入账户信息

``` bash
SIGNING=钱包私钥
WALLETADDRESS=钱包地址
APIKEY=API_Key
APISECRET=API_Seret
```

![image-20240220191231393](https://s2.loli.net/2024/02/20/VlC2LGamAzyvHht.png)



刷交易的程序是`aevo_trade.py`(同时挂买卖单)和`aevo_market_price_trade.py`(同时挂市价卖买单)，流动性比较好的交易对推荐用挂市价单的方式刷，下图的配置部分根据实际情况进行配置，修改完毕后运行程序。


![image-20240220191348102](https://s2.loli.net/2024/02/20/P2Dr1LE5fuJRxhI.png)

## 程序代码

代码链接：https://github.com/shuail0/aevoTrading

作者推特：https://twitter.com/crypto0xLeo