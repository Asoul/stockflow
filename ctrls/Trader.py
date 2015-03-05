#!/bin/python
# -*- coding: utf-8 -*-

import csv
import numpy as np
from config import *

class Trader():
    '''模擬交易情形的過程，買賣最小單位為張'''
    def __init__(self, model_infos, stock_number):

        # Model 的資料
        self.model_description = model_infos["Model Description"]
        self.model_upate_time = model_infos["Update Time"]
        self.model_version = model_infos["Model Version"]

        # 錢和股票
        self.stock_number = stock_number
        self.initial_money = TRADER_INIT_MONEY
        self.money = self.initial_money
        self.stock = 0

        # 買賣次數資訊
        self.buy_count = 0
        self.sell_count = 0
        self.buy_series = []
        self.sell_series = []

        # 天數資訊
        self.days = 0

        # 風險值
        self.day_risks = []
        self.week_risks = []
        self.month_risks = []
        self.year_risks = []

        # 計算股票平均持有天數
        self.hold_stock = 0 #股票持有天數 x 股數
        self.buyed_stock = 0#曾持有的股票數

        # 股票佔資產比率
        self.stockRate_series = []

        # 累計資訊
        self.series = []
        self.asset_series = [TRADER_INIT_MONEY]# 資產序列, 先加入一個起始資產
        self.ratio_series = []# 獲利率序列

    def returnInfo(self, action, number):
        self.hold_stock += self.stock
        stockValue = self.stock * self.series[-1]
        self.stockRate_series.append(float(stockValue)/(stockValue+self.money))
        if action == 'Buy' and number != 0:
            self.buy_series.append(self.series[-1])
            self.sell_series.append(None)
        elif action == 'Sell' and number != 0:
            self.buy_series.append(None)
            self.sell_series.append(self.series[-1])
        else:
            self.buy_series.append(None)
            self.sell_series.append(None)
        
        return ['Day', self.days,
                'Act', action,
                'Volume', number,
                'Current', self.series[-1],
                'Current Money', self.money,
                'Current Stock', self.stock,
                'Current Asset', int(stockValue + self.money)]

    def do(self, newdata, prediction):
        self.series.append(newdata)

        # 更新資產、獲利率、風險值：日風險、週風險、月風險、年風險
        asset = self.series[-1] * self.stock + self.money
        ratio = asset / self.asset_series[-1]

        # 風險是要把獲利 ln(ratio(n)/ratio(n-1)) 算標準差
        if self.days >= 1:
            self.day_risks.append(np.log(ratio/self.ratio_series[-1]))
        if self.days >= 5 and self.days % 5 == 0:
            self.week_risks.append(np.log(ratio/self.ratio_series[-5]))
        if self.days >= 20 and self.days % 20 == 0:
            self.month_risks.append(np.log(ratio/self.ratio_series[-20]))
        if self.days >= 240 and self.days % 240 == 0:
            self.year_risks.append(np.log(ratio/self.ratio_series[-240]))
        
        # 更新 Trader 的基本資料：天數、最新股價、資產序列
        self.days += 1
        self.asset_series.append(asset)
        self.ratio_series.append(ratio)
        

        # 做交易
        # prediction >0 是買，<0 是賣，=0是不動作
        # 1 是有多少錢買多少，-1 是有多少股票賣多少，0.5 是有多少錢買一半... 依此類推

        if prediction > 1 or prediction < -1:
            # 傳入參數錯誤
            return self.returnInfo('Error', 0)
        elif prediction > 0:# 買
            value = self.series[-1] * 1000 # 一張的價錢
            fee = self.series[-1] * 1000 * STOCK_FEE # 一張的手續費
            
            number = int(self.money * prediction / (value + fee))# 願意買的張數

            if fee * number < 20:
                total_fee = 20
            else:
                total_fee = fee * number

            # 考慮如果手續費比一張多，這裡就會變成負的
            if self.money < number * self.series[-1] + total_fee:
                while number > 0:
                    if self.money < number * self.series[-1] + max(20, self.series[-1] * number * STOCK_FEE):
                        break
                    number -= 1

            self.money -= (number * (value + fee)) # 扣除股票費和手續費
            self.money = int(self.money) # 無條件捨去小數點
            self.stock += (number * 1000) # 增加張數 * 1000 股
            self.buyed_stock += (number * 1000) # 買過的股票數
            self.buy_count += 1
            return self.returnInfo('Buy', number*1000)
                
        elif prediction < 0:# 賣
            number = int(self.stock / 1000 * -prediction)# 想要賣的張數
            self.money += (number * 1000 * self.series[-1] * (1 - STOCK_FEE - STOCK_TAX))
            self.money = int(self.money) # 無條件捨去小數點
            self.stock -= (number * 1000)
            self.sell_count += 1
            return self.returnInfo('Sell', number*1000)
        else:
            return self.returnInfo('Nothing', 0)
    
    def analysis(self):
        # 回傳總交易資訊分析
        final_money = self.money + self.stock * self.series[-1] if len(self.series) > 0 else self.money
        ROI = float(final_money) / self.initial_money
        weekly_roi = (ROI**(float(5)/self.days) - 1)*100 if self.days != 0 else 0.0
        years = self.days/240 if self.days > 0 else 0
        infos = {
                # 基本資料
                "Model Description": self.model_description,
                "Update Time": self.model_upate_time,
                "Model Version": self.model_version,
                "Stock Number": self.stock_number,
                "Series": self.series,
                "days": self.days,
                
                # 錢和股票
                "Initial Money": self.initial_money,
                "Initial Money": self.initial_money,
                "Final Money": self.money,
                "Final Stock": self.stock,
                "Stock / Asset Rate": np.mean(self.stockRate_series) if len(self.stockRate_series) > 0 else 0.0,
                "Stock / Asset Change Std": np.std(self.stockRate_series) if len(self.stockRate_series) > 0 else 0.0,
                "Stock-Hold Day": float(self.hold_stock)/self.buyed_stock if self.buyed_stock != 0 else 0,

                # 交易資訊
                "Buy Count": self.buy_count,
                "Sell Count": self.sell_count,
                "Buy Series": self.buy_series,
                "Sell Series": self.sell_series,
                "Trade Count": self.buy_count + self.sell_count,
                
                # 報酬
                "Weekly ROI": weekly_roi,
                "ROI Per Trade": (ROI**(2.0/(self.buy_count+self.sell_count))-1)*100 if (self.buy_count+self.sell_count) != 0 else 0.0,
                "ROI": (ROI-1)*100,
                "Year Interest": ROI/years if years > 0 else 0,
                
                # 風險
                "Daily Risk": np.std(self.day_risks) if len(self.day_risks) > 0 else 0.0,
                "Weekly Risk": np.std(self.week_risks) if len(self.week_risks) > 0 else 0.0,
                "Monthly Risk": np.std(self.month_risks) if len(self.month_risks) > 0 else 0.0,
                "Yearly Risk": np.std(self.year_risks) if len(self.year_risks) > 0 else 0.0
                
                }

        return infos