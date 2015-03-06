#!/bin/python
# -*- coding: utf-8 -*-

from os import listdir
from os.path import isfile, join
import csv
import matplotlib.pyplot as plt
import numpy as np

mypath = '../tsec/data'
file_list = [ f for f in listdir(mypath) if f[-4:] == '.csv' ]

for f in file_list:
    print f
    csvfile = open(join(mypath,f), 'rb')
    csvreader = csv.reader(csvfile, delimiter=',')
    series = []
    for row in csvreader:
        try:
            if float(row[6]) != 0.0:
                series.append(float(row[6]))
        except:
            continue

    mas = [[] for x in xrange(500)]  # the ma(x) series
    for i in xrange(len(series)):
        for j in [2, 3, 5, 10, 20, 30, 60, 90, 120, 180, 240]:
            if i >= j - 1:
                mas[j].append(np.mean(series[i-j+1:i+1]))
            else:
                mas[j].append(0)
    x_axis = range(0, len(series))
    default_line_width = 0.2
    plt.plot(x_axis, series, c='#000000', ls='-', lw=default_line_width)
    plt.plot(x_axis, mas[2], c='#ff0000', ls='-', lw=default_line_width)
    plt.plot(x_axis, mas[3], c='#00ff00', ls='-', lw=default_line_width)
    plt.plot(x_axis, mas[5], c='#0000ff', ls='-', lw=default_line_width)
    plt.plot(x_axis, mas[10], c='#555555', ls='-', lw=default_line_width)
    plt.plot(x_axis, mas[20], c='#ff5555', ls='-', lw=default_line_width)
    plt.plot(x_axis, mas[30], c='#55ff55', ls='-', lw=default_line_width)
    plt.plot(x_axis, mas[60], c='#5555ff', ls='-', lw=default_line_width)
    plt.plot(x_axis, mas[90], c='#999999', ls='-', lw=default_line_width)
    plt.plot(x_axis, mas[120], c='#ff9999', ls='-', lw=default_line_width)
    plt.plot(x_axis, mas[180], c='#99ff99', ls='-', lw=default_line_width)
    plt.plot(x_axis, mas[240], c='#9999ff', ls='-', lw=default_line_width)

    # set figure arguments
    fig = plt.gcf()
    fig.set_size_inches(FIGURE_WIDTH, FIGURE_HEIGHT)

    # output figure
    fig.savefig('mas/'+f[:-4]+'.png', dpi=FIDURE_DPI)
    # fig.savefig('mas-hd/'+f[:-4]+'.png', dpi=1200)
    plt.clf()
    plt.close('all')