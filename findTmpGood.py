#!/bin/python
# -*- coding: utf-8 -*-

import sys
import json
import requests
from ctrls import *
from datetime import date
from models.exampleModel import exampleModel

def main():

    file_list = [ (line.strip()+'.csv') for line in open('stocknumber.csv', 'rb') ]

    drawer = CandleDrawer()

    for filename in file_list:

        model = exampleModel()
        reader = Reader(filename)

        trader = Trader(model.infos, filename)#參數是Model Description 和 filename
        endFlag = False

        while True:
            
            if endFlag:
                break
            row = reader.getInput()

            if row == None: # 歷史資料爬完了，用現在即時的資料
                page = requests.get('http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_'+filename[:-4]+'.tw&json=1&delay=0')
                content = json.loads(page.content)
                vals = content['msgArray'][0]
                t = date.today()
                row = [str(t.year-1911)+'/'+str(t.month).zfill(2)+'/'+str(t.day).zfill(2), 0, 0, vals['o'], vals['h'], vals['l'], vals['z'], 0, 0]
                endFlag = True

            model.update(row)
            prediction = model.predict()
            
            data_year = row[0].split('/')[0]
            if data_year == '104':
                trade = trader.do(float(row[6]), prediction)

        result = trader.analysis()

        if float(row[6]) < 25.0:
            if prediction == 1:
                print row[0], filename, ' @ ', float(row[6]), '該買囉, 今年累計：', result["ROI"], '%'
                # drawer.draw(filename)

if __name__ == '__main__':
    sys.exit(main())