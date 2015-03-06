#!/bin/python
# -*- coding: utf-8 -*-

import csv
import numpy as np
from config import TRADER_INIT_MONEY, STOCK_FEE, STOCK_TAX

class Trader():
    '''模擬交易情形的過程，買賣最小單位為張'''
    def __init__(self, model_infos, stock_number):

        # 基本資料
        self.model_infos = model_infos
        self.stock_number = stock_number

        # 錢和股票
        self.money = TRADER_INIT_MONEY
        self.stock = 0

        # 時間序列
        self.value_series = [] # 價格序列
        self.trade_series = [] # 交易種類序列, 1 買 -1 賣 0 沒動作
        

        # 風險值
        self.ratio_series = []# 獲利率序列
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
        
        self.asset_series = [TRADER_INIT_MONEY]# 資產序列, 先加入一個起始資產
        

    def updateAndreturnInfo(self, action, volume):
        # 更新資產、獲利率、風險值：日風險、週風險、月風險、年風險
        asset = self.value_series[-1] * self.stock + self.money
        ratio = asset / self.asset_series[-1]

        # 風險是要把獲利 ln(ratio(n)/ratio(n-1)) 算標準差
        days = len(self.ratio_series)
        if days >= 1:
            self.day_risks.append(np.log(ratio/self.ratio_series[-1]))
        if days >= 5 and days % 5 == 0:
            self.week_risks.append(np.log(ratio/self.ratio_series[-5]))
        if days >= 20 and days % 20 == 0:
            self.month_risks.append(np.log(ratio/self.ratio_series[-20]))
        if days >= 240 and days % 240 == 0:
            self.year_risks.append(np.log(ratio/self.ratio_series[-240]))
        
        # 更新 Trader 的基本資料：天數、最新股價、資產序列
        self.asset_series.append(asset)
        self.ratio_series.append(ratio)

        self.hold_stock += self.stock
        stockValue = self.stock * self.value_series[-1]
        
        self.stockRate_series.append(float(stockValue)/(stockValue+self.money))
        
        if action == 'Buy' and volume != 0:
            self.trade_series.append(1)
        elif action == 'Sel' and volume != 0:
            self.trade_series.append(-1)
        else:
            self.trade_series.append(0)
        
        return {
            'Day': days,
            'Act': action,
            'Volume': volume,
            'Value': self.value_series[-1],
            'Money': self.money,
            'Stock': self.stock,
            'Asset': int(stockValue + self.money),
            'ROI': float(stockValue + self.money)/TRADER_INIT_MONEY
        }

    def do(self, row, pred):
        self.value_series.append(float(row[6]))
        high_value = float(row[4])
        low_value = float(row[5])
        
        # 做交易
        # pred[0] >0 是買，<0 是賣，=0是不動作
        # 1 是有多少錢買多少，-1 是有多少股票賣多少，0.5 是有多少錢買一半... 依此類推
        # pred[1] 是要買或賣的價格，今天要有在這個價格內才會交易成功

        if pred[0] == 0: return self.updateAndreturnInfo('Non', 0)
        elif pred[0] > 1 or pred[0] < -1:# 傳入參數錯誤
            return self.updateAndreturnInfo('Err', 0)
        elif pred[1] == 0 or (pred[1] >= low_value and pred[1] <= high_value):
            if pred[0] > 0:
                if pred[1] == 0:
                    value = self.value_series[-1] * 1000 # 一張的價錢
                else:
                    value = pred[1]

                fee = self.value_series[-1] * 1000 * STOCK_FEE # 一張的手續費
                
                volume = int(self.money * pred[0] / (value + fee))# 願意買的張數

                if fee * volume < 20:
                    total_fee = 20
                else:
                    total_fee = fee * volume

                # 考慮如果手續費比一張多，這裡就會變成負的
                if self.money < volume * self.value_series[-1] + total_fee:
                    while volume > 0:
                        if self.money < volume * self.value_series[-1] + max(20, self.value_series[-1] * volume * STOCK_FEE):
                            break
                        volume -= 1

                self.money -= (volume * (value + fee)) # 扣除股票費和手續費
                self.money = int(self.money) # 無條件捨去小數點
                self.stock += (volume * 1000) # 增加張數 * 1000 股
                self.buyed_stock += (volume * 1000) # 買過的股票數
                return self.updateAndreturnInfo('Buy', volume*1000)
            else:
                volume = int(self.stock / 1000 * -pred[0])# 想要賣的張數
                if pred[1] == 0:
                    value = self.value_series[-1] # 一張的價錢
                else:
                    value = pred[1]
                self.money += (volume * 1000 * value * (1 - STOCK_FEE - STOCK_TAX))
                self.money = int(self.money) # 無條件捨去小數點
                self.stock -= (volume * 1000)
                return self.updateAndreturnInfo('Sel', volume*1000)
        else:
            return self.updateAndreturnInfo('Out', 0)
    
    def analysis(self):

        # 回傳總交易資訊分析

        final_money = self.money + self.stock * self.value_series[-1] if len(self.value_series) > 0 else self.money
        ROI = float(final_money) / TRADER_INIT_MONEY
        days = len(self.value_series)
        weekly_roi = (ROI**(float(5)/days) - 1)*100 if days != 0 else 0.0
        years = days/240 if days > 0 else 0

        trade_count = len(self.trade_series) - self.trade_series.count(0)

        return {

            # 基本資料
            "Model Description": self.model_infos["Model Description"],
            "Update Time": self.model_infos["Update Time"],
            "Model Version": self.model_infos["Model Version"],
            "Stock Number": self.stock_number,

            # 時間序列
            "Value Series": self.value_series,
            "Trade Series": self.trade_series,
            
            # 錢和股票
            "Initial Money": TRADER_INIT_MONEY,
            "Final Money": self.money,
            "Final Stock": self.stock,
            "Stock / Asset Rate": np.mean(self.stockRate_series) if len(self.stockRate_series) > 0 else 0.0,
            "Stock / Asset Change Std": np.std(self.stockRate_series) if len(self.stockRate_series) > 0 else 0.0,
            "Stock-Hold Day": float(self.hold_stock)/self.buyed_stock if self.buyed_stock != 0 else 0,

            # 交易次數資訊
            "Buy Count": self.trade_series.count(1),
            "Sell Count": self.trade_series.count(-1),
            "Trade Count": len(self.trade_series) - self.trade_series.count(0),
            
            # 報酬
            "Weekly ROI": weekly_roi,
            "ROI Per Trade": (ROI**(2.0/(len(self.trade_series) - self.trade_series.count(0)))-1)*100 if len(self.trade_series) != self.trade_series.count(0) else 0.0,
            "ROI": (ROI-1)*100,
            "Year Interest": ROI/years if years > 0 else 0,
            
            # 風險
            "Daily Risk": np.std(self.day_risks) if len(self.day_risks) > 0 else 0.0,
            "Weekly Risk": np.std(self.week_risks) if len(self.week_risks) > 0 else 0.0,
            "Monthly Risk": np.std(self.month_risks) if len(self.month_risks) > 0 else 0.0,
            "Yearly Risk": np.std(self.year_risks) if len(self.year_risks) > 0 else 0.0
                
        }