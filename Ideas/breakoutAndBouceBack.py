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
    # checkStock["48weeksHigh"] = checkStock.High.rolling(window=232, min_periods=1, center=False).max()
    checkStock["averageVol"] = checkStock.Volume.rolling(window=10, min_periods=1, center=False).mean()
    checkStock['3wksLow'] = checkStock.High.rolling(window=5,min_periods=1,center=False).max()
    if len(checkStock>252):
        lastHigh = 0
        buyPrice = 0
        sellPrice = 0
        buyDate = datetime(2000,1,1)
        sellDate = datetime(2000,1,1)
        newOrder = pd.DataFrame(columns=['stock', 'buyDate', 'buyPrice', 'sellDate', 'sellPrice', 'status','percent'])
        i = 252
        while i < len(checkStock)-25:
            if openingOrder==0:
                if  (checkStock.ix[i]['High'] > checkStock.ix[i-1]['52weeksHigh']) and checkStock.ix[i]['High']> checkStock.ix[i-1]['High'] *1.02 and checkStock.ix[i-1]['averageVol']>50000:
                    bbPrice = checkStock.ix[i-1]['52weeksHigh']
                    lastHigh = checkStock.ix[i - 1]['52weeksHigh']
                    for j in range(1,20):
                        if checkStock.ix[i+j]['Low']<=bbPrice and checkStock.ix[i+j]['Close']>bbPrice:
                            buyPrice = checkStock.ix[i+j+1]['Open']
                            buyDate = checkStock.index[i+j+1]
                            total_orders += 1
                            openingOrder = 1
                            i = i+j+2
                            break
                    #buyPrice = checkStock.ix[i]['Close']
                    i=i+1
                else:
                    i = i+1
            elif openingOrder==1:
                if checkStock.ix[i]['High'] > buyPrice*1.154:
                    sellPrice = buyPrice*1.15
                    sellDate = checkStock.index[i]
                    win_orders += 1
                    openingOrder = 0
                    percent = sellPrice/buyPrice - 1
                    newOrder = pd.DataFrame([[fileName,buyDate,buyPrice,sellDate,sellPrice,'won',percent]],columns=['stock', 'buyDate', 'buyPrice', 'sellDate', 'sellPrice', 'status','percent'])
                    orders = pd.concat([orders,newOrder])
                    lastHigh = 0
                    buyPrice = 0
                    sellPrice = 0
                    buyDate = datetime(2000,1,1)
                    sellDate = datetime(2000,1,1)
                    timesWon += 1
                    if i < len(checkStock) - 25:
                        i = i+10
                        continue
                    else:
                        break
                elif checkStock.ix[i]['Close']<=buyPrice*0.95:
                    sellPrice = checkStock.ix[i]['Close']
                    sellDate = checkStock.index[i]
                    loss_orders+=1
                    openingOrder = 0
                    percent = sellPrice/buyPrice - 1
                    newOrder = pd.DataFrame([[fileName, buyDate, buyPrice, sellDate, sellPrice, 'loss',percent]],
                                            columns=['stock', 'buyDate', 'buyPrice', 'sellDate', 'sellPrice', 'status','percent'])
                    orders = pd.concat([orders, newOrder])
                    lastHigh = 0
                    buyPrice = 0
                    sellPrice = 0
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

orders.to_csv('testresults/1year-breakout-bouceback.csv',index=False)
#statistics.to_csv('testresults/52wksbreakout-buySellClose-15percent-openHigherThanLastHigh-stats.csv',index=False)




