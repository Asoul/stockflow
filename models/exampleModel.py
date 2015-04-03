#!/bin/python
# -*- coding: utf-8 -*-

import numpy as np

class exampleModel():
    
    def __init__(self):
        # 紀錄序列
        self.price_series = []

        # 紀錄狀態
        self.haveStock = 0.0
        self.buyPrice = 0.0

        # Simple Moving Average
        self.price_ma = [0.0 for x in xrange(121)]  # the price ma(x) series

        # 參數們
        self.infos = {
            "Model Description": "exampleModel",
            "Update Time": '2015/03/26',
            "Model Version": "2.0.0"
        }

    def updateTrade(self, trade):
        if trade and trade["Volume"] != 0:# 有交易
            if trade["Type"][-3:] == 'Buy':
                self.haveStock += trade["Volume"]
                self.buyPrice = float(trade["Price"])
            elif trade["Type"][-4:] == "Sell":
                self.haveStock -= trade["Volume"]


    def updateData(self, row):
        self.price_series.append(float(row[6]))
        # Simple Moving Average
        for i in [20, 60]:
            self.price_ma[i] = np.mean(self.price_series[-min(i, len(self.price_series)):])

    def predict(self, when, price):
        '''
        讓 model 預測下一步應該要怎麼做，模擬下單的過程，會要回傳一個 dictionary，包含：
            Type: Buy, Sell or Nothing
            Price: 要下單的價格，0 代表用開盤價買
            Volume: 要下單的量，0 代表能買多少盡量買
        '''
        if when == 'start':
            '''
            when = start 是開盤時，可以決定要不要下單，可以用當下的開盤價買賣，
            或下單在整天中如果有價格符合下單的條件，就會交易
            '''
            if len(self.price_series) == 0:
                return {"Type": "Nothing", "Price": 0, "Volume": 0}
            elif self.haveStock == 0 and(# 沒有持有的情況

                # 高於月線 ma20
                self.price_series[-1] > self.price_ma[20]
                # 低於季線 ma60
                and self.price_series[-1] < self.price_ma[60]

            ):
                return {"Type": "Finance Buy", "Price": 0, "Volume": 0}

            elif self.haveStock > 0 and (# 有持有的情框

                # 低於月線 ma20
                self.price_series[-1] < self.price_ma[20]
                # 停損
                or self.price_series[-1] < self.buyPrice * 0.9

            ):
                return {"Type": "Finance Sell", "Price": 0, "Volume": 0}
            else:
                return {"Type": "Nothing", "Price": 0, "Volume": 0}
        elif when == 'end':
            '''
            when = end 是收盤時，可以決定要不要下單，只能用當下的開盤價買賣
            '''
            return {"Type": "Nothing", "Price": 0, "Volume": 0}
        else:
            return {"Type": "Nothing", "Price": 0, "Volume": 0}