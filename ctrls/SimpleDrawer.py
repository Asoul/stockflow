#!/bin/python
# -*- coding: utf-8 -*-

from config import *
from os.path import join
from datetime import datetime
from ctrls.Reader import Reader
import matplotlib.pyplot as plt

class SimpleDrawer():
    '''畫出近 n 天收盤價圖'''

    def _getFigTitle(self, stock_number):
        t = datetime.now()
        return ('%s, Update: %s/%s/%s %s:%s:%s' % (stock_number,
            str(t.year), str(t.month),str(t.day),
            str(t.hour), str(t.minute), str(t.second))
        )
        
    def draw(self, number, length = SIMPLE_FIG_LENGTH):
        reader = Reader(number)
        series = []

        while True:
            row = reader.getInput()
            if row == None: break
            series.append(float(row[6]))

        x_axis = range(len(series[-SIMPLE_FIG_LENGTH:]))
        plt.plot(x_axis, series[-SIMPLE_FIG_LENGTH:], 'b--', ls='-')
        plt.title(self._getFigTitle(number))

        # set figure
        fig = plt.gcf()
        fig.set_size_inches(FIGURE_WIDTH, FIGURE_HEIGHT)

        # output figure
        fig.savefig(join(SIMPLE_FIG_PATH, number+'.png'), dpi=FIGURE_DPI)
        plt.clf()
        plt.close('all')