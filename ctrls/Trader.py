#!/bin/python
# -*- coding: utf-8 -*-

import csv
import numpy as np
from settings import *
import math
from datetime import datetime, date, timedelta

class Trader():
    '''模擬交易情形的過程，買賣最小單位為張(1000 股)'''
    def __init__(self, model_infos, stock_number, noLog):

        # 基本資料
        self.model_infos = model_infos # Model 資訊
        self.stock_number = stock_number # 股票代號

        # 狀態設置
        self.noLog = noLog

        # 錢、股票、未還融資券金額
        self.money = TRADER_INIT_MONEY # 帳戶餘額
        self.stock = 0 # 現股
        self.finance_debt = 0 # 未還融資金
        self.finance_stock = 0 # 未還融資股票
        self.finance_interest = 0 # 融資利息
        self.bearish_promise = 0 # 未還融券保證金
        self.bearish_debt = 0 # 未還融券擔保品
        self.bearish_stock = 0 # 未還融券股票
        self.bearish_interest = 0 # 融券利息

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
        self.stock_ratio_series = []# 股票佔資產比率

        # 計算股票平均持有天數
        self.stock_series = [] #股票持有的股票數序列
        self.buyed_stock_series = [] #曾購賣的股票數序列

    def printLog(self, trade, when):

        stocks = self.stock + self.finance_stock - self.bearish_stock
        debts = self.finance_debt - self.bearish_debt
        asset = self.getAsset(trade["Price"])

        print ('%s %s %s %d at %.2f, Money: %d, Stock: %d, Debt: %d, Asset: %d, Rate: %.3f%%' % 
            (self.date_series[-1], when[:3], ABBR[trade["Type"]], trade['Volume'], trade['Price'], 
            self.money, stocks, debts, asset, float(asset)/TRADER_INIT_MONEY*100)
        )

    def autoCorrectPrice(self, price):
        '''依照證券交易所的級距更改成實際價格'''
        if price >= 1000: return math.floor(price / 5) * 5
        elif price >= 500: return math.floor(price)
        elif price >= 100: return math.floor(price * 2)/2
        elif price >= 50: return math.floor(price * 10)/10
        elif price >= 10: return math.floor(price * 20)/20
        else: return math.floor(price * 100)/100

    def getAsset(self, price):
        cost = int(price * self.stock * 1000)
        fee = int(max(STOCK_MIN_FEE, cost * STOCK_FEE))
        tax = int(cost * STOCK_TAX)
        total_stock = cost - fee - tax

        finance = self.finance_stock * price * 1000
        finance_fee = int(max(STOCK_MIN_FEE, finance * STOCK_FEE))
        finance_tax = int(finance * STOCK_TAX)
        finance_interest = 0
        total_finance = finance - finance_fee - finance_tax - finance_interest - self.finance_debt

        bearish = self.bearish_stock * price * 1000
        bearish_fee = int(max(STOCK_MIN_FEE, bearish * STOCK_FEE))
        total_bearish = self.bearish_debt + self.bearish_promise - bearish - bearish_fee + self.bearish_interest

        return self.money + total_stock + total_finance + total_bearish

    def updateAndReturn(self, action, price, volume, when):

        if action in ['Buy', "Finance Buy", "Bearish Buy"]:
            self.buyed_stock_series[-1] += volume
            self.stock_series[-1] += volume
        elif action in ["Sell", "Finance Sell", "Bearish Sell"]:
            self.stock_series[-1] -= volume

        if when == 'end':# 一天結束了
            asset = self.getAsset(self.close_series[-1])
            self.asset_series.append(asset)

            self.finance_interest += int(self.finance_debt * FINANCE_INTEREST / 365)
            self.bearish_interest += int((self.bearish_promise + self.bearish_debt) * BEARISH_INTEREST / 365)
            
            # 更新買賣序列
            if self.stock_series[-1] > 0:
                self.trade_series.append(1)
            elif self.stock_series[-1] < 0:
                self.trade_series.append(-1)
            else:
                self.trade_series.append(0)

            # 更新股票占資產的比率序列
            if len(self.stock_series) > 1:
                self.stock_series[-1] = self.stock_series[-1] + self.stock_series[-2]
            self.stock_ratio_series.append(1 - float(self.money)/asset)            

        trade =  {
            'Type': action,
            'Volume': volume,
            'Price': price
        }

        if not self.noLog and trade["Type"] != "Nothing":
            self.printLog(trade, when)

        return trade

    def updateData(self, row):
        self.date_series.append(row[0])
        self.quant_series.append(float(row[1]))
        self.open_series.append(float(row[3]))
        self.high_series.append(float(row[4]))
        self.low_series.append(float(row[5]))
        self.close_series.append(float(row[6]))
        self.buyed_stock_series.append(0)
        self.stock_series.append(0)

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
        # 沒有量要賣
        elif order["Type"] == "Sell" and self.stock <= 0:
            return True
        elif order["Type"] == "Finance Sell" and self.finance_stock <= 0:
            return True
        elif order["Type"] == "Bearish Sell" and self.bearish_stock <= 0:
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
            return self.updateAndReturn('Nothing', 0, 0, when)

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
            
        if volume <= 0:
            return self.updateAndReturn('Nothing', 0, 0, when)
        cost = volume * price * 1000
        total_cost = cost + max(STOCK_MIN_FEE, cost * STOCK_FEE)
        if total_cost > self.money:
            return self.updateAndReturn('Nothing', 0, 0, when)
        # Update
        self.money -= total_cost # 扣除股票費和手續費
        self.stock += volume # 持有股票數

        return self.updateAndReturn('Buy', price, volume, when)
        
    def sell(self, when, order):
        # Check Price
        price = self.getTradePrice(when, "S", order["Price"])
        if price == None:
            return self.updateAndReturn('Nothing', 0, 0, when)

        if order["Volume"] == 0 or order["Volume"] >= self.stock:
            volume = self.stock
        else:
            volume = int(order["Volume"])# 避免傳成 float
        
        cost = int(price * volume * 1000)
        fee = int(min(STOCK_MIN_FEE, cost * STOCK_FEE))
        tax = int(cost * STOCK_TAX)

        self.money += cost - fee - tax
        self.stock -= volume

        return self.updateAndReturn('Sell', price, volume, when)

    def financeBuy(self, when, order):
        # Check Price
        price = self.getTradePrice(when, "B", order["Price"])
        if price == None:
            return self.updateAndReturn('Nothing', 0, 0, when)

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

        if volume <= 0:
            return self.updateAndReturn('Nothing', 0, 0, when)
        total_finance = int(price * volume * FINANCE_RATE) * 1000
        cost = price * volume * 1000
        total_cost = cost + max(STOCK_MIN_FEE, cost * STOCK_FEE) - total_finance

        # Update
        self.money -= total_cost # 扣除股票費和手續費
        self.finance_debt += total_finance
        self.finance_stock += volume # 持有股票數

        return self.updateAndReturn('Finance Buy', price, volume, when)

    def financeSell(self, when, order):
        # Check Price
        price = self.getTradePrice(when, "S", order["Price"])
        if price == None:
            return self.updateAndReturn('Nothing', 0, 0, when)

        if order["Volume"] == 0 or order["Volume"] >= self.finance_stock:
            volume = self.finance_stock
            repay_finance = self.finance_debt
        else:
            volume = int(order["Volume"])# 避免傳成 float
            # 只償還一部分的話，要剩下的還可以融多少
            can_finance = int((self.finance_stock - volume) * price * FINANCE_RATE) * 1000
            repay_finance = self.finance_debt - can_finance

        cost = int(price * volume * 1000)
        interest = int(repay_finance / self.finance_debt * self.finance_interest)
        fee = int(max(STOCK_MIN_FEE, cost * STOCK_FEE))
        tax = int(cost * STOCK_TAX)

        # Update
        self.money += cost - repay_finance - interest - fee - tax
        self.finance_debt -= repay_finance
        self.finance_interest -= interest
        self.finance_stock -= volume # 持有股票數

        return self.updateAndReturn('Finance Sell', price, volume, when)

    def bearishBuy(self, when, order):
        # Check Price
        price = self.getTradePrice(when, "S", order["Price"])
        if price == None:
            return self.updateAndReturn('Nothing', 0, 0, when)

        # Check Volume
        if order["Volume"] == 0:
            volume = int(int(self.money / 100) / (BEARISH_RATE * price * 10))
        else:
            volume = int(order["Volume"])

        if volume <= 0:
            return self.updateAndReturn('Nothing', 0, 0, when)

        cost = price * volume * 1000
        promise = int(math.ceil(cost*BEARISH_RATE/100)*100)
        bearish_fee = int(cost * BEARISH_FEE)
        fee = int(max(STOCK_MIN_FEE, cost * STOCK_FEE))
        tax = int(cost * STOCK_TAX)

        # Update
        self.money -= promise # 扣除股票費和手續費
        self.bearish_debt += cost - fee - tax - bearish_fee
        self.bearish_promise += promise
        self.bearish_stock += volume # 持有股票數

        return self.updateAndReturn('Bearish Buy', price, volume, when)

    def bearishSell(self, when, order):
        # Check Price
        price = self.getTradePrice(when, "B", order["Price"])
        if price == None:
            return self.updateAndReturn('Nothing', 0, 0, when)

        if order["Volume"] == 0 or order["Volume"] >= self.bearish_stock:
            volume = self.bearish_stock
            remain_debt = 0
            remain_promise = 0
            interest = self.bearish_interest
        else:
            volume = int(order["Volume"])
            # 只償還一部分的話，要剩下的還可以融多少
            remain_cost = int((self.bearish_stock - volume) * price)
            remain_fee = int(max(STOCK_MIN_FEE, remain_cost * STOCK_FEE))
            remain_tax = int(remain_cost * STOCK_TAX)
            remain_bfee = int(remain_cost * BEARISH_FEE)
            remain_debt = int(remain_cost - remain_fee - remain_tax - remain_bfee)
            remain_promise = int(math.ceil(remain_cost * BEARISH_RATE / 100) * 100)
            interest = int(self.bearish_interest * (float(volume)/self.bearish_stock))

        cost = int(price * volume * 1000)
        fee = int(max(STOCK_MIN_FEE, cost * STOCK_FEE))
        debt_delta = self.bearish_debt - remain_debt
        promise_delta = self.bearish_promise - remain_promise

        # Update
        self.money += (debt_delta + promise_delta - cost - fee + interest)
        self.bearish_stock -= volume
        self.bearish_interest -= interest
        self.bearish_promise -= promise_delta
        self.bearish_debt -= debt_delta

        return self.updateAndReturn('Bearish Sell', price, volume, when)

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