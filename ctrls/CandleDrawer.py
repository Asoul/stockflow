#!/bin/python
# -*- coding: utf-8 -*-

import os
import csv
import numpy as np
from config import *
from datetime import datetime
import matplotlib.pyplot as plt
from os.path import join, isdir
from matplotlib.finance import candlestick_ohlc

class CandleDrawer():

    def getBooleanBand(self, series):
        bool_next = []# 近 n 天和 Moving Average 的分佈

        bool_up_series = []# boolean band 上界
        ma_series = []# boolean band 中間
        bool_down_series = []# boolean band 上界

        for i in xrange(len(series)):
            ma_series.append(np.mean(series[-min(CANDLE_BOOL_NUM, len(series)):]))

            # Boolean Band

            # 近 n 天和 Moving Average 的分佈
            bool_next.append(series[i] - ma_series[-1])
            if len(bool_next) > CANDLE_BOOL_NUM: bool_next.pop(0)

            # 通道大小
            bool_width = 2 * np.std(bool_next)
            bool_up_series.append(ma_series[-1] + bool_width)
            bool_down_series.append(ma_series[-1] - bool_width)

        return bool_up_series, ma_series, bool_down_series

    def getFigTitle(self, stock_number):
        t = datetime.now()
        return ('%s, Update: %s/%s/%s %s:%s:%s' % (stock_number,
            str(t.year), str(t.month),str(t.day),
            str(t.hour), str(t.minute), str(t.second))
        )


    def draw(self, result):

        # Candle Stick
        candle_sticks = []
        
        # Append Candle Stick and Calculate Boolean Band
        for i in xrange(len(result["Close Series"])):
            # matplotlib 的 candlestick_ohlc 依序放入 [編號, 收盤, 最高, 最低, 開盤] 會畫出 K 線圖
            candle_sticks.append((
                i,
                result["Close Series"],
                result["High Series"],
                result["Low Series"],
                result["Open Series"]
            ))
            
        bool_up_series, ma_series, bool_down_series = self.getBooleanBand(result["Close Series"])
        
        # Draw Figure
        default_line_width = CANDLE_FIG_LINE_WIDTH
        
        fig, axarr = plt.subplots(2, sharex=True)

        candlestick_ohlc(axarr[0], quotes[-CANDLE_FIG_LENGTH:], width=CANDLE_STICK_WIDTH)
        
        x_axis = range(len(quotes))
        # set zorder 讓 candlestick 可以在上面
        axarr[0].plot(x_axis[-CANDLE_FIG_LENGTH:], ma_series[-CANDLE_FIG_LENGTH:], c='#00ff00', ls='-', lw=default_line_width, zorder=-5)
        axarr[0].plot(x_axis[-CANDLE_FIG_LENGTH:], bool_up_series[-CANDLE_FIG_LENGTH:], c='#ff0000', ls='-', lw=default_line_width, zorder=-4)
        axarr[0].plot(x_axis[-CANDLE_FIG_LENGTH:], bool_down_series[-CANDLE_FIG_LENGTH:], c='#0000ff', ls='-', lw=default_line_width, zorder=-3)
        axarr[0].plot(x_axis[-CANDLE_FIG_LENGTH:], result["High Series"][-CANDLE_FIG_LENGTH:], c='#ff3399', ls='-', lw=default_line_width, zorder=-2)
        axarr[0].plot(x_axis[-CANDLE_FIG_LENGTH:], result["Low Series"][-CANDLE_FIG_LENGTH:], c='#0099ff', ls='-', lw=default_line_width, zorder=-1)
        
        axarr[0].set_title(self.getFigTitle(result["Stock Number"]))
        
        axarr[1].plot(x_axis[-CANDLE_FIG_LENGTH:], result["Quant Series"][-CANDLE_FIG_LENGTH:], c='#000000', ls='-', lw=default_line_width)
        
        # set figure arguments
        fig.set_size_inches(FIGURE_WIDTH, FIGURE_HEIGHT)

        # output figure
        
        fig.savefig(CANDLE_FIG_PATH+'/'+result["Stock Number"]+'.png', dpi=FIGURE_DPI)

        plt.clf()
        plt.close('all')
    