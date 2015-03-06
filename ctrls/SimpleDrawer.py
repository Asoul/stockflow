#!/bin/python
# -*- coding: utf-8 -*-

from os import listdir
from os.path import isfile, join
import csv
import matplotlib.pyplot as plt
import sys
sys.path.append('..')

index_list = []

for line in open('../stocknumber.csv','rb'):
    index_list.append(line.strip()+'.csv')

for f in index_list:
    print f
    csvfile = open(join(mypath,f), 'rb')
    csvreader = csv.reader(csvfile, delimiter=',')
    series = []
    for row in csvreader:
        if row[6] != '--' and float(row[6]) != 0:
            series.append(float(row[6]))
    x_axis = range(0, len(series))
    plt.plot(x_axis, series, 'b--', ls='-')
    plt.title('ID = %s, Update Date = %s' % (f[:-4], row[0]))

    # set figure arguments
    fig = plt.gcf()
    fig.set_size_inches(FIGURE_WIDTH, FIGURE_HEIGHT)

    # output figure
    fig.savefig(join('../figures',f[:-4]+'.png'), dpi=FIGURE_DPI)
    plt.clf()
    plt.close('all')