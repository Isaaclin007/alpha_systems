# Entry rules:
#
# 	* (t-1 -> t-6)Breakout 52 weeks and high > 3% of last high
# 	* Buy at close
#
# Exit rules:
#
# 	* Profit 15%
# 	* Loss is break 5%
#   * Sell @ close price


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import datetime
from datetime import datetime, date


fileList = glob.glob('data/*.csv')
orders = pd.DataFrame(columns=['stock','buyDate','buyPrice','sellDate','sellPrice','status','percent'])
statistics = pd.DataFrame(columns=['stock','won','loss','wonRate'])
total_orders = 0
win_orders = 0
loss_orders = 0


for fileName in fileList:
    print(fileName)
    checkStock = pd.read_csv(fileName, index_col=0, parse_dates=['Date'])
    openingOrder = 0
    lastHigh = 0
    timesWon = 0
    timesLoss = 0
    #find entry pattern:
    #checkStock["52weeksHigh"] = pd.rolling_max(checkStock.High, window=252, min_periods=1)
    checkStock["52weeksHigh"] = checkStock.High.rolling(window=252,min_periods=1,center=False).max()
    checkStock["1monthLow"] = checkStock.Low.rolling(window=44,min_periods=1,center=False).min()
    # checkStock['value'] = checkStock.Volume * checkStock.Close
    # checkStock["48weeksHigh"] = checkStock.High.rolling(window=232, min_periods=1, center=False).max()
    checkStock["averageVol"] = checkStock.Volume.rolling(window=20, min_periods=1, center=False).mean()
    checkStock['rolling_std'] = checkStock['Close'].rolling(5).std() * 10
    checkStock['change'] = checkStock.rolling_std / checkStock.Close
    checkStock = checkStock.reset_index()
    checkStock['aveStd'] = checkStock['change'].rolling(window=5,min_periods=1).mean()

    if len(checkStock>252) and not 'ABT' in fileName:
        lastHigh = 0
        buyPrice = 0
        sellPrice = 0
        buyDate = datetime(2000,1,1)
        sellDate = datetime(2000,1,1)
        change1 = 0
        change2 = 0
        # aveSTD = 0
        newOrder = pd.DataFrame(columns=['stock', 'buyDate', 'buyPrice', 'sellDate', 'sellPrice', 'status','percent','change1','change2'])
        i = 200
        while i < len(checkStock)-10:
            if openingOrder==0:
                if (checkStock.ix[i]['High'] > checkStock.ix[i-1]['52weeksHigh']) and checkStock.ix[i-1]['52weeksHigh'] == checkStock.ix[i-23]['52weeksHigh'] and checkStock.ix[i]['High']> checkStock.ix[i-1]['High'] * 1.03  and  checkStock.ix[i-1]['averageVol']>100000:
                    lastHigh = checkStock.ix[i-1]['52weeksHigh']
                    if checkStock.ix[i - 1]['change'] > 0 and checkStock.ix[i]['change']>0:
                        change1 = checkStock.ix[i-1]['aveStd']
                        change2 = checkStock.ix[i]['change']
                    buyPrice = checkStock.ix[i]['Close']
                    buyDate = checkStock.index[i]
                    total_orders += 1
                    openingOrder = 1
                    i=i+4
                    continue
                else:
                    i = i+1
            elif openingOrder==1:
                if checkStock.ix[i]['High'] > buyPrice*1.154:
                    sellPrice = buyPrice*1.15
                    sellDate = checkStock.index[i]
                    win_orders += 1
                    openingOrder = 0
                    percent = sellPrice/buyPrice - 1
                    newOrder = pd.DataFrame([[fileName,buyDate,buyPrice,sellDate,sellPrice,'won',percent,change1,change2]],columns=['stock', 'buyDate', 'buyPrice', 'sellDate', 'sellPrice', 'status','percent','change1','change2'])
                    orders = pd.concat([orders,newOrder])
                    lastHigh = 0
                    buyPrice = 0
                    sellPrice = 0
                    buyDate = datetime(2000,1,1)
                    sellDate = datetime(2000,1,1)
                    change1=0
                    change2=0
                    timesWon += 1
                    if i < len(checkStock) - 25:
                        i = i+10
                        continue
                    else:
                        break
                elif checkStock.ix[i]['Close']<=buyPrice*0.925:
                    sellPrice = checkStock.ix[i]['Close']
                    sellDate = checkStock.index[i]
                    loss_orders+=1
                    openingOrder = 0
                    percent = sellPrice/buyPrice - 1
                    newOrder = pd.DataFrame([[fileName, buyDate, buyPrice, sellDate, sellPrice, 'loss',percent,change1,change2]],
                                            columns=['stock', 'buyDate', 'buyPrice', 'sellDate', 'sellPrice', 'status','percent','change1','change2'])
                    orders = pd.concat([orders, newOrder])
                    lastHigh = 0
                    buyPrice = 0
                    sellPrice = 0
                    change1=0
                    change2=0
                    buyDate = datetime(2000,1,1)
                    sellDate = datetime(2000,1,1)
                    timesLoss+=1
                    if i < len(checkStock) - 25:
                        i = i+10
                        continue
                    else:
                        break
                else:
                    i += 1
        if timesLoss > 0 or timesWon > 0:
            tempStats = pd.DataFrame([[fileName,timesWon,timesLoss,timesWon/(timesWon+timesLoss)*100]],columns=['stock','won','loss','wonRate'])
            statistics = pd.concat([statistics,tempStats])

orders.to_csv('testresults/52wksbreakout-buyatClose-last1month.csv',index=False)
statistics.to_csv('testresults/52wksbreakout-buyatClose-last1month-stats.csv',index=False)




