#!/bin/python
# -*- coding: utf-8 -*-

import numpy as np

class variableModel():
    
    def __init__(self, argv = []):
        # 紀錄序列
        self.value_series = []

        # 紀錄狀態
        self.haveStockState = False
        self.changeStateFlag = False

        # 紀錄股市資訊
        self.buyValue = 0.0
        self.buyDay = 0

        # Simple Moving Average
        self.value_ma = [0.0 for x in xrange(121)]  # the value ma(x) series

        # 參數們
        variables = [[5, 10],
                     [10, 20],
                     [20, 60]]

        self.infos = {
                        "Model Description": "variableModel"+str(argv[0])+"_"+str(argv[1]),
                        "Update Time": '2015/03/05',
                        "Model Version": "1.0.0",
                        "Recommend Variables": variables
                     }

    def update(self, row):
        self.value_series.append(float(row[6]))

        # Simple Moving Average
        for i in [20, 60]:
            self.value_ma[i] = np.mean(self.value_series[-min(i, len(self.value_series)):])

        # 看是不是要買賣
        if self.changeStateFlag:
            self.haveStockState = not self.haveStockState
            self.changeStateFlag = False

        if self.haveStockState:
            self.buyDay += 1
        else:
            self.buyDay = 0

    def predict(self):        
        if  (
                (
                    (
                    # 高於月線 ma20
                    self.value_series[-1] > self.value_ma[20]
                    # 低於季線 ma60
                    and self.value_series[-1] < self.value_ma[60]
                    )
                )
            and not self.haveStockState):
                self.changeStateFlag = True
                self.buyValue = self.value_series[-1]
                return 1
        elif (

                (
                    # 低於月線 ma20
                    self.value_series[-1] < self.value_ma[20]
                    # 停損
                    or self.value_series[-1] < self.buyValue * 0.9
                )
            and self.haveStockState):
            self.changeStateFlag = True
            return -1
        else:
            return 0
        