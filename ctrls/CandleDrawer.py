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

    def draw(self, stock_number, today_tmp_data=[]):
        csvfile = open(TSEC_DATA_PATH+stock_number+'.csv', 'rb')
        csvreader = csv.reader(csvfile, delimiter=',')

        # Series
        value_series = []
        quant_series = []
        high_series = []
        low_series = []
        quotes = []

        # Simple Moving Average
        value_ma = [[] for x in xrange(121)]  # the value ma(x) series
        quant_ma = [[] for x in xrange(121)]  # the quant ma(x) series
        
        # Boolean Band, using ma20
        bool_next = []
        bool_up_series = []
        bool_down_series = []

        # concat tmp row
        rows = []
        for row in csvreader:
            rows.append(row)
        if len(today_tmp_data) == 9:
            rows.append(today_tmp_data)

        count = 0
        for row in rows:
            if row[6] != '--' and float(row[6]) != 0.0:
                count += 1
                value_series.append(float(row[6]))
                quant_series.append(float(row[2]))
                high_series.append(float(row[4]))
                low_series.append(float(row[5]))
                quotes.append((count, float(row[6]), float(row[4]), float(row[5]), float(row[3])))

                # Simple Moving Average, ma20 for boolean band
                value_ma[20].append(np.mean(value_series[-min(20, len(value_series)):]))

                # Boolean Band

                bool_next.append(value_series[-1] - value_ma[CANDLE_BOOL_NUM][-1])
                if len(bool_next) > CANDLE_BOOL_NUM:
                    bool_next.pop(0)
                bool_width = 2*np.std(bool_next)
                if bool_width != 0.0:
                    bool_b = (value_series[-1] - value_ma[CANDLE_BOOL_NUM][-1])/bool_width * 100
                else:
                    bool_b = 0.0
                bool_up_series.append(value_ma[CANDLE_BOOL_NUM][-1] + bool_width)
                bool_down_series.append(value_ma[CANDLE_BOOL_NUM][-1] - bool_width)
                    
        default_line_width = 1
        
        fig, axarr = plt.subplots(2, sharex=True)
        
        candlestick_ohlc(axarr[0], quotes[-CANDLE_FIG_LENGTH:], width=0.6)

        x_axis = range(len(quotes))
        axarr[0].plot(x_axis[-CANDLE_FIG_LENGTH:], bool_up_series[-CANDLE_FIG_LENGTH:], c='#ff0000', ls='-', lw=default_line_width)
        axarr[0].plot(x_axis[-CANDLE_FIG_LENGTH:], value_ma[20][-CANDLE_FIG_LENGTH:], c='#00ff00', ls='-', lw=default_line_width)
        axarr[0].plot(x_axis[-CANDLE_FIG_LENGTH:], bool_down_series[-CANDLE_FIG_LENGTH:], c='#0000ff', ls='-', lw=default_line_width)
        axarr[0].plot(x_axis[-CANDLE_FIG_LENGTH:], high_series[-CANDLE_FIG_LENGTH:], c='#ffff55', ls='-', lw=default_line_width)
        axarr[0].plot(x_axis[-CANDLE_FIG_LENGTH:], low_series[-CANDLE_FIG_LENGTH:], c='#55ff55', ls='-', lw=default_line_width)
        t = datetime.now()
        axarr[0].set_title(stock_number+' Update: '+str(t.year)+'/'+str(t.month)+'/'+str(t.day)+' '+str(t.hour)+':'+str(t.minute)+':'+str(t.second))
        
        axarr[1].plot(x_axis[-CANDLE_FIG_LENGTH:], quant_series[-CANDLE_FIG_LENGTH:], c='#000000', ls='-', lw=default_line_width)
        
        # set figure arguments
        fig.set_size_inches(FIGURE_WIDTH, FIGURE_HEIGHT)

        # output figure
        if not isdir(CANDLE_FIG_PATH):
            os.mkdir(CANDLE_FIG_PATH)
        fig.savefig(CANDLE_FIG_PATH+'/'+stock_number+'.csv'[:-4]+'.png', dpi=FIGURE_DPI)
        plt.clf()
        plt.close('all')
    