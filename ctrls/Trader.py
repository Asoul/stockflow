#!/bin/python
# -*- coding: utf-8 -*-

import csv
import numpy as np
from config import *

class Trader():
    '''模擬交易情形的過程，買賣最小單位為張'''
    def __init__(self, model_infos, stock_number, noQuantLimit = True):

        # 基本資料
        self.model_infos = model_infos
        self.stock_number = stock_number
        self.date_from = None
        self.date_to = None

        # 錢和股票
        self.money = TRADER_INIT_MONEY
        self.stock = 0

        # 時間序列
        # 交易日期、成交股數、成交金額、開盤價、最高價、最低價、收盤價、漲跌價差、成交筆數
        self.date_series  = [] # 0. 日期序列
        self.quant_series = [] # 1. 量序列
        self.open_series  = [] # 3. 開盤價序列
        self.high_series  = [] # 4. 最高價序列
        self.low_series   = [] # 5. 最低價序列
        self.close_series = [] # 6. 收盤價序列
        
        self.trade_series = [] # 交易種類序列, 1 買 -1 賣 0 沒動作
        self.asset_series = [TRADER_INIT_MONEY]# 資產序列, 先加入一個起始資產
        self.stockRate_series = []# 股票佔資產比率

        # 計算股票平均持有天數
        self.hold_stock = 0 #股票持有天數 x 股票數
        self.buyed_stock = 0 #曾持有的股票數

        # TODO: 實作 quant Limit
        self.noQuantLimit = noQuantLimit

    def _getBuyAndSellSeries(self):
        '''為了做成買賣趨勢圖，把交易序列和價格序列，各轉換為一個序列，有買賣就放值，沒買賣就放 None'''
        buy_series = []
        sell_series = []

        for i in range(len(self.close_series)):
        
            if self.trade_series[i] == 1:
                buy_series.append(self.close_series[i])
            else:
                buy_series.append(None)

            if self.trade_series[i] == -1:
                sell_series.append(self.close_series[i])
            else:
                sell_series.append(None)

        return buy_series, sell_series

    def _getRisks(self):
        risks = [0.0, 0.0, 0.0, 0.0]# 分別為日、週、月、年的風險值
        risk_days = [1, 5, 20, 240]

        for risk_idx in xrange(4):
            # 如果累計天數超過要算風險值所需的天數，才要算
            if len(self.asset_series) > risk_days[risk_idx] + 1:

                # 風險是要把獲利取自然對數再算標準差：std(ln(estate(n)/estate(n-1)))
                tmp_risks = []
                for i in range(risk_days[risk_idx]+1, len(self.asset_series)):
                    tmp_risks.append(np.log(float(self.asset_series[i])/self.asset_series[i - risk_days[risk_idx]]))
                risks[risk_idx] = np.std(tmp_risks)

        return risks

    def _updateAndreturnInfo(self, action, volume):
        # 更新資產：最後才更新因為買賣會扣手續費
        asset = int(self.close_series[-1] * self.stock * 1000+ self.money)
        self.asset_series.append(asset)

        # 更新持有的股票數 x 一天
        self.hold_stock += self.stock
        # 更新股票占資產的比率序列
        self.stockRate_series.append(float(self.close_series[-1] * self.stock * 1000)/asset)
        
        # 更新買賣序列
        if action == 'Buy': self.trade_series.append(1)
        elif action == 'Sel': self.trade_series.append(-1)
        else: self.trade_series.append(0)
        
        return {
            'Day': len(self.close_series),
            'Act': action,
            'Volume': volume,
            'Value': self.close_series[-1],
            'Money': self.money,
            'Stock': self.stock,
            'Asset': asset,
            'Rate': (float(asset)/TRADER_INIT_MONEY)*100
        }

    def do(self, row, pred):
        '''更新資訊並做交易，row 是新的一份資料，pred 是 model 傳來想要買或賣的資料'''

        # 更新資料
        self.date_series.append(row[0])
        self.quant_series.append(float(row[1]))
        self.open_series.append(float(row[3]))
        self.high_series.append(float(row[4]))
        self.low_series.append(float(row[5]))
        self.close_series.append(float(row[6]))

        # todayQuant = float(row[1]) # TODO: 實作量的限制

        # 沒有操作、先擋掉 Volume 小於 0 的錯誤
        if (pred["Act"] != "Buy" and pred["Act"] != "Sell") or pred["Volume"] < 0:
            return self._updateAndreturnInfo('Nothing', 0)

        # 操作價位
        if pred["Value"] == 0:# 使用開盤價買賣
            value = self.open_series[-1] * 1000 # 一張的價錢
        elif pred["Value"] <= self.high_series[-1] and pred["Value"] >= self.low_series[-1]:# 用自訂的金額買賣
            value = pred["Value"] * 1000 # 一張的價錢
        else:
            return self._updateAndreturnInfo('Nothing', 0)

        # 操作動作
        if pred["Act"] == "Buy":
            # 操作數量
            if pred["Volume"] == 0:# 全買
                
                min_unit = int(STOCK_MIN_FEE / (value * STOCK_FEE)) # 至少要多少張才會超過最低手續費
                volume = int(self.money/(value * (1 + STOCK_FEE)))

                # 如果剛好卡在最低手續費而算起來會超過金額
                if volume < min_unit and volume * value * (1 + STOCK_FEE) < self.money:
                    volume = int((self.money - STOCK_MIN_FEE)/value)
                    total_cost = int(volume * value + STOCK_MIN_FEE)
                else:
                    total_cost = int(volume * value * (1 + STOCK_FEE))

            else:# Volume > 0, 買 n 張

                total_cost = volume * value + max(STOCK_MIN_FEE, volume * value * STOCK_FEE)

                if total_cost > self.money:
                    return self._updateAndreturnInfo('Nothing', 0)

            self.money -= total_cost # 扣除股票費和手續費
            self.stock += volume # 持有股票數
            self.buyed_stock += volume # 買過的股票數

            return self._updateAndreturnInfo('Buy', volume)
            
        elif pred["Act"] == "Sell":

            # pred["Volume"] > self.stock 的話是 model 有 bug，就當做全賣
            if pred["Volume"] == 0 or pred["Volume"] > self.stock:
                volume = self.stock
            else:
                volume = int(pred["Volume"])# 避免傳成 float
            
            self.money += int(value * volume * (1 - STOCK_FEE - STOCK_TAX))
            self.stock -= volume

            return self._updateAndreturnInfo('Sel', volume)
    
    def analysis(self):
        '''回傳總交易資訊分析'''

        ROI = float(self.asset_series[-1]) / TRADER_INIT_MONEY
        days = len(self.close_series)

        trade_count = len(self.trade_series) - self.trade_series.count(0)

        buy_series, sell_series = self._getBuyAndSellSeries()

        day_risks, week_risks, month_risks, year_risks = self._getRisks()

        return {

            # 基本資料
            "Model Description": self.model_infos["Model Description"],
            "Update Time": self.model_infos["Update Time"],
            "Model Version": self.model_infos["Model Version"],
            "Stock Number": self.stock_number,
            "Date From": self.date_series[0] if len(self.date_series) > 0 else 'No Period',
            "Date To": self.date_series[-1] if len(self.date_series) > 0 else 'No Period',

            # 時間序列
            "Date Series": self.date_series,
            "Quant Series": self.quant_series,
            "Open Series": self.open_series,
            "High Series": self.high_series,
            "Close Series": self.close_series,
            "Low Series": self.low_series,
            "Trade Series": self.trade_series,
            "Buy Series": buy_series,
            "Sell Series": sell_series,
            
            # 錢和股票
            "Initial Money": TRADER_INIT_MONEY,
            "Stock / Asset Rate": np.mean(self.stockRate_series) if len(self.stockRate_series) > 0 else 0.0,
            "Stock / Asset Change Std": np.std(self.stockRate_series) if len(self.stockRate_series) > 0 else 0.0,
            "Stock-Hold Day": float(self.hold_stock)/self.buyed_stock if self.buyed_stock != 0 else 0,

            # 交易次數資訊
            "Buy Count": self.trade_series.count(1),
            "Sell Count": self.trade_series.count(-1),
            "Trade Count": trade_count,
            
            # 報酬
            "ROI": (ROI-1)*100,
            "Weekly ROI": (ROI**(float(5)/days) - 1)*100 if days != 0 else 0.0,
            "ROI Per Trade": (ROI**(2.0/(trade_count))-1)*100 if trade_count else 0.0,
            
            # 風險
            "Daily Risk": day_risks,
            "Weekly Risk": week_risks,
            "Monthly Risk": month_risks,
            "Yearly Risk": year_risks
                
        }