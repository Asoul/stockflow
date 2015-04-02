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
        self.finance_stock = 0
        self.bearish_debt = 0
        self.bearish_stock = 0

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

    def updateAndreturn(self, action, price, volume, when):
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

    def isErrorOrder(self, when, order):
        '''檢查是不是會有錯誤的單'''
        # 錯誤的 order
        for key in ["Price", "Type", "Volume"]:
            if key not in order:
                return True
        # 錯誤的價、量、時間
        if order["Price"] < 0 or order["Volume"] < 0:
            return True
        elif when not in ["start", "mid", "end"]:
            return True
        # 錯誤的類別
        elif order["Type"] not in ["Buy", "Sell", "Finance Buy", "Finance Sell",\
                                   "Bearish Buy", "Bearish Sell", "Nothing"]:
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
        return self.autoCorrectPrice(price)

    def buy(self, when, order):
        # Check Price
        price = self.getTradePrice(when, "B", order["Price"])
        if price == None:
            return self.updateAndreturnInfo('Nothing', 0, 0, when)

        # Check Volume
        if order["Volume"] == 0: # 全買
            # 至少要多少張才會超過最低手續費
            min_unit = int(STOCK_MIN_FEE/(price * 1000 * STOCK_FEE)) 

            # 錢不夠買最低手續費所需張數
            if min_unit * price * 1000 * (1 + STOCK_FEE) > self.money:
                volume = int((self.money - STOCK_MIN_FEE)/(price * 1000))
            else:
                volume = int(self.money/(price * 1000 * (1 + STOCK_FEE)))
        else:
            volume = int(order["Volume"])
            
        cost = volume * price * 1000
        total_cost = cost + max(STOCK_MIN_FEE, cost * STOCK_FEE)
        if total_cost > self.money:
            return self.updateAndreturnInfo('Nothing', 0, 0, when)
        # Update
        self.money -= total_cost # 扣除股票費和手續費
        self.stock += volume # 持有股票數

        return self.updateAndreturnInfo('Buy', price, volume, when)
        
    def sell(self, when, order):
        # Check Price
        price = self.getTradePrice(when, "S", order["Price"])
        if price == None:
            return self.updateAndreturnInfo('Nothing', 0, 0, when)

        if order["Volume"] == 0 or order["Volume"] >= self.stock:
            volume = self.stock
        else:
            volume = int(order["Volume"])# 避免傳成 float
        
        cost = int(price * volume * 1000)
        fee = int(min(STOCK_MIN_FEE, cost * STOCK_FEE))
        tax = int(cost * STOCK_TAX)

        self.money += cost - fee - tax
        self.stock -= volume

        return self.updateAndreturnInfo('Sell', price, volume, when)

    def financeBuy(self, when, order):
        # Check Price
        price = self.getTradePrice(when, "B", order["Price"])
        if price == None:
            return self.updateAndreturnInfo('Nothing', 0, 0, when)

        # Check Volume
        if order["Volume"] == 0:
            min_unit = int(STOCK_MIN_FEE/(price * 1000 * STOCK_FEE)) # 至少要多少張才會超過最低手續費

            # 錢不夠買最低手續費所需張數
            if math.ceil(min_unit * price * (1 - FINANCE_RATE)) * 1000 + STOCK_MIN_FEE > self.money:
                max_finance = int((self.money - STOCK_MIN_FEE)*FINANCE_RATE/(1 - FINANCE_RATE)/1000) * 1000
                can_use = self.money - STOCK_MIN_FEE
            else:
                max_finance = int(self.money * (FINANCE_RATE)/(1 - FINANCE_RATE +STOCK_FEE)/1000) * 1000
                can_use = self.money * (1 - FINANCE_RATE)/(1 - FINANCE_RATE + STOCK_FEE)

            volume = int((max_finance + can_use)/(price * 1000))
        else:
            volume = int(order["Volume"])

        total_finance = int(price * volume * FINANCE_RATE) * 1000
        cost = price * volume * 1000
        total_cost = cost + max(STOCK_MIN_FEE, cost * STOCK_FEE) - total_finance

        # Update
        self.money -= total_cost # 扣除股票費和手續費
        self.finance_debt += total_finance
        self.finance_stock += volume # 持有股票數

        return self.updateAndreturnInfo('Finance Buy', price, volume, when)

    def financeSell(self, when, order):
        # Check Price
        price = self.getTradePrice(when, "S", order["Price"])
        if price == None:
            return self.updateAndreturnInfo('Nothing', 0, 0, when)

        if order["Volume"] == 0 or order["Volume"] >= self.finance_stock:
            volume = self.finance_stock
            repay_finance = self.finance_debt
        else:
            volume = int(order["Volume"])# 避免傳成 float
            # 只償還一部分的話，要剩下的還可以融多少
            can_finance = int((self.finance_stock - volume) * price * FINANCE_RATE) * 1000
            repay_finance = self.finance_debt - can_finance

        cost = int(price * volume * 1000)
        interest = repay_finance * FINANCE_INTEREST# TODO: 算出差幾天
        fee = int(max(STOCK_MIN_FEE, cost * STOCK_FEE))
        tax = int(cost * STOCK_TAX)

        # Update
        self.money += cost - repay_finance - interest - fee - tax
        self.finance_debt -= repay_finance
        self.finance_stock -= volume # 持有股票數

        return self.updateAndreturnInfo('Finance Sell', price, volume, when)

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
    
    def getResult(self):
        '''回傳交易資訊'''

        return {
            # 基本資料
            "Model Description": self.model_infos["Model Description"],
            "Update Time": self.model_infos["Update Time"],
            "Model Version": self.model_infos["Model Version"],
            "Stock Number": self.stock_number,

            # 時間序列
            "Date Series": self.date_series,
            "Quant Series": self.quant_series,
            "Open Series": self.open_series,
            "High Series": self.high_series,
            "Low Series": self.low_series,
            "Close Series": self.close_series,
            
            "Trade Series": self.trade_series,
            "Stock Series": self.stock_series,
            "Buyed Stock Series": self.buyed_stock_series,
            
            "Asset Series": self.asset_series,
            "Stock Ratio Series": self.stock_ratio_series
        }