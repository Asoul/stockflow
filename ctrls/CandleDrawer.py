#!/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from config import *
from datetime import datetime
from ctrls.Reader import Reader
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc

class CandleDrawer():
    '''畫出近 n 天 K 線圖＋Ma20布林通道+高低通道+量'''

    def _getBooleanBand(self, series):
        bool_next = []# 近 n 天和 Moving Average 的分佈

        bool_up_series = []# boolean band 上界
        ma_series = []# boolean band 中間
        bool_down_series = []# boolean band 上界

        for i in xrange(CANDLE_BOOL_NUM, len(series)):
            ma_series.append(np.mean(series[i - CANDLE_BOOL_NUM:i]))

            # Boolean Band

            # 近 n 天和 Moving Average 的分佈
            bool_next.append(series[i] - ma_series[-1])
            if len(bool_next) > CANDLE_BOOL_NUM: bool_next.pop(0)

            # 通道大小
            bool_width = 2 * np.std(bool_next)
            bool_up_series.append(ma_series[-1] + bool_width)
            bool_down_series.append(ma_series[-1] - bool_width)

        return bool_up_series, ma_series, bool_down_series

    def _getFigTitle(self, number):
        t = datetime.now()
        return ('%s, Update: %s/%s/%s %s:%s:%s' % (number,
            str(t.year), str(t.month),str(t.day),
            str(t.hour), str(t.minute), str(t.second))
        )


    def draw(self, number, length = CANDLE_FIG_LENGTH):

        reader = Reader(number)
        series = [[] for x in xrange(7)]

        # Candle Stick
        candle_sticks = []

        idx = -1
        while True:
            idx +=1 
            row = reader.getInput()
            if row == None: break
            for i in [1, 3, 4, 5, 6]:
                series[i].append(float(row[i]))
                # matplotlib 的 candlestick_ohlc 依序放入 [編號, 收盤, 最高, 最低, 開盤] 會畫出 K 線圖
            candle_sticks.append((
                idx,
                float(row[6]),
                float(row[4]),
                float(row[5]),
                float(row[3])
            ))            
            
        bool_up_series, ma_series, bool_down_series = self._getBooleanBand(series[6])
        
        # Draw Figure
        line_width = CANDLE_FIG_LINE_WIDTH
        
        fig, axarr = plt.subplots(2, sharex=True)

        candlestick_ohlc(axarr[0], candle_sticks[-length:], width=CANDLE_STICK_WIDTH)
        
        x_axis = range(len(series[6]))
        # set zorder 讓 candlestick 可以在上面
        axarr[0].plot(x_axis[-length:], ma_series[-length:], c='#00ff00', ls='-', lw=line_width, zorder=-5)
        axarr[0].plot(x_axis[-length:], bool_up_series[-length:], c='#ff0000', ls='-', lw=line_width, zorder=-4)
        axarr[0].plot(x_axis[-length:], bool_down_series[-length:], c='#0000ff', ls='-', lw=line_width, zorder=-3)
        axarr[0].plot(x_axis[-length:], series[4][-length:], c='#ff3399', ls='-', lw=line_width, zorder=-2)
        axarr[0].plot(x_axis[-length:], series[5][-length:], c='#0099ff', ls='-', lw=line_width, zorder=-1)
        
        axarr[0].set_title(self._getFigTitle(number))
        
        axarr[1].plot(x_axis[-length:], series[1][-length:], c='#000000', ls='-', lw=line_width)
        
        # set figure arguments
        fig.set_size_inches(FIGURE_WIDTH, FIGURE_HEIGHT)

        # output figure
        
        fig.savefig(CANDLE_FIG_PATH+'/'+number+'.png', dpi=FIGURE_DPI)

        plt.clf()
        plt.close('all')
        