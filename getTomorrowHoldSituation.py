#!/bin/python
# -*- coding: utf-8 -*-

import sys
from ctrls import *
from datetime import date
from models.exampleModel import exampleModel

def main():

    number_list = ["9907"]

    drawer = CandleDrawer()

    for filename in number_list:

        model = exampleModel()
        reader = Reader(filename)

        trader = Trader(model.infos, filename)#參數是Model Description 和 filename
        last_row = None
        this_year = str(date.today().year-1911)


        while True:
            
            row = reader.getInput()
            if row == None: # today, use crawled data
                break

            last_row = row

            model.update(row)
            prediction = model.predict()
            
            data_year = row[0].split('/')[0]
            if data_year == this_year:
                trader.do(float(row[6]), prediction)

        result = trader.analysis()

        drawer.draw(filename, last_row)

        if prediction == 1:
            print last_row[0], filename, ' @ ', float(last_row[6]), '該買囉, 今年累計：', result["ROI"], '%'
        elif prediction == -1:
            print last_row[0], filename, ' @ ', float(last_row[6]), '該賣囉, 今年累計：', result["ROI"], '%'
        elif prediction == 0:
            print last_row[0], filename, ' @ ', float(last_row[6]), '不要動, 今年累計：', result["ROI"], '%'

if __name__ == '__main__':
    sys.exit(main())