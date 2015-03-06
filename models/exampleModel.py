#!/bin/python
# -*- coding: utf-8 -*-

import numpy as np

class exampleModel():
    
    def __init__(self, argv = []):
        # 紀錄序列
        self.value_series = []

        # 紀錄狀態
        self.haveStock = 0.0
        self.buyValue = 0.0
        self.buyDay = 0

        # Simple Moving Average
        self.value_ma = [0.0 for x in xrange(121)]  # the value ma(x) series

        # 參數們
        variables = [[]]
        self.infos = {
            "Model Description": "exampleModel",
            "Update Time": '2015/03/05',
            "Model Version": "1.0.0",
            "Recommend Variables": variables
        }

    def update(self, row, trade):
        self.value_series.append(float(row[6]))

        # Simple Moving Average
        for i in [20, 60]:
            self.value_ma[i] = np.mean(self.value_series[-min(i, len(self.value_series)):])

        # 交易資訊
        if trade["Volume"] != 0:# 有交易
            if trade["Act"] == 'Buy':
                self.haveStock += trade["Volume"]
            else:
                self.haveStock -= trade["Volume"]

            if self.haveStock < 0:
                raise Exception("haveStock cannot be negative")

        # 股市持有資訊
        if self.haveStock > 0: self.buyDay += 1
        else: self.buyDay = 0

    def predict(self):
        if len(self.value_series) == 0: return [0, 0]
        elif self.haveStock == 0 and(# 沒有持有的情況

            # 高於月線 ma20
            self.value_series[-1] > self.value_ma[20]
            # 低於季線 ma60
            and self.value_series[-1] < self.value_ma[60]

        ):
            return [1, 0]

        elif self.haveStock > 0 and (# 有持有的情框

            # 低於月線 ma20
            self.value_series[-1] < self.value_ma[20]
            # 停損
            or self.value_series[-1] < self.buyValue * 0.9

        ):
            return [-1, 0]
        else:
            return [0, 0]
        