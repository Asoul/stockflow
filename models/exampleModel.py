#!/bin/python
# -*- coding: utf-8 -*-

import numpy as np

class exampleModel():
    
    def __init__(self):
        # 紀錄序列
        self.value_series = []

        # 紀錄狀態
        self.haveStock = 0.0
        self.buyValue = 0.0

        # Simple Moving Average
        self.value_ma = [0.0 for x in xrange(121)]  # the value ma(x) series

        # 參數們
        self.infos = {
            "Model Description": "exampleModel",
            "Update Time": '2015/03/07',
            "Model Version": "1.0.0"
        }

    def update(self, row, trade = None):
        self.value_series.append(float(row[6]))

        # Simple Moving Average
        for i in [20, 60]:
            self.value_ma[i] = np.mean(self.value_series[-min(i, len(self.value_series)):])

        # 交易資訊
        if trade and trade["Volume"] != 0:# 有交易
            if trade["Act"] == 'Buy':
                self.haveStock += trade["Volume"]
            else:
                self.haveStock -= trade["Volume"]

            if self.haveStock < 0:
                raise Exception("haveStock cannot be negative")

    def predict(self):
        '''
        讓 model 預測下一步應該要怎麼做，模擬下單的過程，會要回傳一個 dictionary，包含：
            Act: Buy, Sell or Nothing
            Value: 要下單的價格，0 代表用開盤價買
            Volume: 要下單的量，0 代表能買多少盡量買
        '''
        if len(self.value_series) == 0:
            return {"Act": "Nothing", "Value": 0, "Volume": 0}
        elif self.haveStock == 0 and(# 沒有持有的情況

            # 高於月線 ma20
            self.value_series[-1] > self.value_ma[20]
            # 低於季線 ma60
            and self.value_series[-1] < self.value_ma[60]

        ):
            return {"Act": "Buy", "Value": 0, "Volume": 0}

        elif self.haveStock > 0 and (# 有持有的情框

            # 低於月線 ma20
            self.value_series[-1] < self.value_ma[20]
            # 停損
            or self.value_series[-1] < self.buyValue * 0.9

        ):
            return {"Act": "Sell", "Value": 0, "Volume": 0}
        else:
            return {"Act": "Nothing", "Value": 0, "Volume": 0}
        