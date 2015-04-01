#!/bin/python
# -*- coding: utf-8 -*-

import csv
import numpy as np
from settings import *
import math

class Trader():
    '''模擬交易情形的過程，買賣最小單位為張(1000 股)'''
    def __init__(self, model_infos, stock_number, noLog):

        # 基本資料
        self.model_infos = model_infos
        self.stock_number = stock_number

        # 狀態設置
        self.noLog = noLog

        # 錢、股票、未還融資券金額
        self.money = TRADER_INIT_MONEY
        self.stock = 0
        self.finance_debt = 0
        self.bearish_debt = 0

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
        self.stock_series = [] #股票持有的股票數序列
        self.buyed_stock_series = [] #曾持有的股票數序列

    def printTradeLog(self, trade):
        print ('%s %s %d at %.2f, Money: %d, Stock: %d, Asset: %d, Rate: %.3f%%' % 
            (self.date_series[-1], trade['Type'][:3], trade['Volume'], round(trade['Value']/1000, 2), 
            trade['Money'], trade['Stock'], trade['Asset'], trade['Rate'])
        )

    def autoCorrectPrice(self, price):
        '''依照證券交易所的級距更改成實際價格'''
        if price >= 1000:
            price = math.floor(price / 5) * 5
        elif price >= 500:
            price = math.floor(price)
        elif price >= 100:
            price = math.floor(price * 2)/2
        elif price >= 50:
            price = math.floor(price * 10)/10
        elif price >= 10:
            price = math.floor(price * 20)/20
        else:
            price = math.floor(price * 100)/100
        return price

    def updateAndreturnInfo(self, action, price, volume, when):
        # 更新資產：最後才更新因為買賣會扣手續費
        asset = int(self.close_series[-1] * self.stock * 1000+ self.money)
        self.asset_series.append(asset)

        if when == 'start':
            self.todayVolume = 0# 每天開始前先歸零，計算當沖量
        
        if action == 'Buy':
            self.todayVolume += volume
        elif action == 'Sell':
            self.todayVolume -= volume

        if when == 'end':# 一天結束了
            
            # 更新持有的股票數
            if self.todayVolume > 0:
                self.buyed_stock_series.append(self.todayVolume) # 買過的股票數
            else:
                self.buyed_stock_series.append(0)
            self.stock_series.append(self.stock)
            
            # 更新股票占資產的比率序列
            self.stockRate_series.append(float(self.close_series[-1] * self.stock * 1000)/asset)
        
            # 更新買賣序列
            if self.todayVolume > 0: self.trade_series.append(1)
            elif self.todayVolume < 0: self.trade_series.append(-1)
            else: self.trade_series.append(0)
        
        trade =  {
            'Day': len(self.close_series),
            'Type': action,
            'Volume': volume,
            'Price': price,
            'Money': self.money,
            'Stock': self.stock,
            'Asset': asset,
            'Rate': (float(asset)/TRADER_INIT_MONEY)*100
        }

        if not noLog:
            self.printTradeLog(trade)

        return trade

    def updateData(self, row):
        self.date_series.append(row[0])
        self.quant_series.append(float(row[1]))
        self.open_series.append(float(row[3]))
        self.high_series.append(float(row[4]))
        self.low_series.append(float(row[5]))
        self.close_series.append(float(row[6]))

    def isErrorOrder(when, order):
        '''檢查是不是會有錯誤的單'''
        # 錯誤的 order
        for key in ["Price", "Type", "Volume"]:
            if key not in order:
                return True
        # 錯誤的價
        if order["Price"] < 0:
            return True
        # 錯誤的量，融資融券才會有負數的量
        elif order["Volume"] < 0 and order["Type"] in ["Buy", "Sell"]:
            return True
        elif when not in ["start", "mid", "end"]:
            return True
        # 錯誤的類別
        elif order["Type"] not in ["Buy", "Sell", "Finance", "Bearish", "Nothing"]:
            return True
        # 盤中沒有指定價位
        elif when == 'mid' and order["Price"] == 0:
            return True

        return False

    def getTradePrice(self, when, act, price):
        if when == "start":
            return self.open_series[-1]
        elif when == "end":
            return self.close_series[-1]
        elif act == "B":
            if price > self.high_series[-1]:
                return self.high_series[-1]
            elif price < self.low_series[-1]:
                return None
        elif act == "S":
            if price > self.high_series[-1]:
                return None
            elif price < self.low_series[-1]:
                return self.low_series[-1]
        return price

    def buy(self, when, order):
        # Check Price
        price = self.getTradePrice(when, "B", order["Price"])

        # Check Volume
        min_unit = int(STOCK_MIN_FEE/(price * 1000 * STOCK_FEE)) # 至少要多少張才會超過最低手續費

        # 錢不夠買最低手續費所需張數
        if min_unit * price * 1000 * (1 + STOCK_FEE) > self.money:
            volume = int((self.money - STOCK_MIN_FEE)/(price * 1000))
            total_cost = int(price * 1000 * volume) + int(STOCK_MIN_FEE)
        else:
            volume = int(self.money/(price * 1000 * (1 + STOCK_FEE)))
            total_cost = int(price * 1000 * volume) + int(price * 1000 * volume * STOCK_FEE)

        # Update
        self.money -= total_cost # 扣除股票費和手續費
        self.stock += volume # 持有股票數

        return self.updateAndreturnInfo('Buy', price, volume, when)
        
    def sell(self, when, order):
        # Check Price
        price = self.getTradePrice(when, "S", order["Price"])

        if order["Volume"] == 0 or order["Volume"] > self.stock:
            volume = self.stock
        else:
            volume = int(order["Volume"])# 避免傳成 float
        
        fee = int(min(STOCK_MIN_FEE, price * volume * 1000 * STOCK_FEE))
        tax = int(price * volume * 1000 * STOCK_TAX)
        self.money += int(price * volume * 1000) - fee - tax
        self.stock -= volume

        return self.updateAndreturnInfo('Sell', price, volume, when)

    def financeBuy(self, when, order):
        # Check Price
        if order["Volume"]
        price = self.getTradePrice(when, "B", order["Price"])

        # Check Volume
        min_unit = int(STOCK_MIN_FEE/(price * 1000 * STOCK_FEE)) # 至少要多少張才會超過最低手續費

        # 錢不夠買最低手續費所需張數
        if math.ceil(min_unit * price * (1 - FINANCE_RATE)) * 1000 + STOCK_MIN_FEE > self.money:

        else:
            max_finance = int(self.money * (FINANCE_RATE)/(1 - FINANCE_RATE +STOCK_FEE)/1000) * 1000
            can_use = self.money * (1 - FINANCE_RATE)/(1 - FINANCE_RATE + STOCK_FEE)

            volume = int((max_finance + can_use)/(price * 1000))
            total_finance = int(price * volume * FINANCE_RATE) * 1000
            total_cost = price * volume * 1000 * (1 + STOCK_FEE) - total_finance

        # Update
        self.money -= total_cost # 扣除股票費和手續費
        self.finance_debt += total_finance
        self.stock += volume # 持有股票數

        return self.updateAndreturnInfo('Finance', price, volume, when)

    def place(self, when, order):
        '''when 是時間點，order 是 model 傳來想要買或賣的資料'''

        if self.isErrorOrder(when, order):
            return self.updateAndReturn('Nothing', 0, 0, when)

        if order["Type"] == "Nothing":
            return self.updateAndReturn('Nothing', 0, 0, when)        
        elif order["Type"] == "Buy":
            return self.buy(when, order)
        elif order["Type"] == "Sell":
            return self.sell(when, order)
        elif order["Type"] == "Finance Buy":
            return self.financeBuy(when, order)
        elif order["Type"] == "Finance Sell":
            return self.financeSell(when, order)
        elif order["Type"] == "Bearish Buy":
            return self.bearishBuy(when, order)
        elif order["Type"] == "Bearish Sell":
            return self.bearishSell(when, order)
        else:
            return self.bearish(when, order)

            
            # 操作數量
            if order["Volume"] == 0:# 全買

            else:# Volume > 0, 買 n 張

                total_cost = volume * price + max(STOCK_MIN_FEE, volume * price * STOCK_FEE)

                if total_cost > self.money:
                    return self._updateAndreturnInfo('Nothing', 0, 0, when)

            self.money -= total_cost # 扣除股票費和手續費
            self.stock += volume # 持有股票數

            return self._updateAndreturnInfo('Buy', price, volume, when)
            
        elif order["Type"] == "Sell":

            # order["Volume"] > self.stock 的話是 model 有 bug，就當做全賣
            if order["Volume"] == 0 or order["Volume"] > self.stock:
                volume = self.stock
            else:
                volume = int(order["Volume"])# 避免傳成 float
            
            self.money += int(price * volume * (1 - STOCK_FEE - STOCK_TAX))
            self.stock -= volume

            return self._updateAndreturnInfo('Sell', price, volume, when)
        else:
            return self._updateAndreturnInfo('Nothing', 0, 0, when)

        if order["Volume"] < 0 or order["Type"] == "Nothing":
            return self._updateAndreturnInfo('Nothing', 0, 0, when)
        
        # 做交易
        price = self.getTradePrice(row, order, when)
        return self._transact(order, price)

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
    
    def analysis(self):
        '''回傳總交易資訊分析'''

        ROI = float(self.asset_series[-1]) / TRADER_INIT_MONEY
        days = len(self.close_series)

        trade_count = len(self.trade_series) - self.trade_series.count(0)

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
            
            # 錢和股票
            "Initial Money": TRADER_INIT_MONEY,
            "Stock / Asset Rate": np.mean(self.stockRate_series) \
                                   if len(self.stockRate_series) > 0 else 0.0,
            "Stock / Asset Change Std": np.std(self.stockRate_series) \
                                   if len(self.stockRate_series) > 0 else 0.0,
            "Stock-Hold Day": float(sum(self.stock_series))/sum(self.buyed_stock_series) \
                                if sum(self.buyed_stock_series) != 0 else 0,

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