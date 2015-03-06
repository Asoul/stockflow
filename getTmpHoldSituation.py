#!/bin/python
# -*- coding: utf-8 -*-

import sys
import json
import requests
from ctrls import *
from datetime import date
from models.exampleModel import exampleModel

def main():

    number_list = ["2206", "2324"]# 設定你現在持有的清單

    drawer = CandleDrawer()
    this_year = str(date.today().year-1911)

    for number in number_list:

        model = exampleModel()
        reader = Reader(number)

        trader = Trader(model.infos, number)#參數是Model Description 和 number
        endFlag = False

        while True:
            
            if endFlag:
                break
            row = reader.getInput()

            if row == None: # 歷史資料爬完了，用現在即時的資料
                page = requests.get('http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_'+number+'.tw&json=1&delay=0')
                content = json.loads(page.content)
                vals = content['msgArray'][0]
                t = date.today()
                row = [str(t.year-1911)+'/'+str(t.month).zfill(2)+'/'+str(t.day).zfill(2), 0, 0, vals['o'], vals['h'], vals['l'], vals['z'], 0, 0]
                endFlag = True

            model.update(row)
            prediction = model.predict()
            
            data_year = row[0].split('/')[0]
            if data_year == this_year:
                trade = trader.do(float(row[6]), prediction)

        result = trader.analysis()

        drawer.draw(number, row)

        if prediction == 1:
            print row[0], number, ' @ ', float(row[6]), '該買囉, 今年累計：', result["ROI"], '%'
        elif prediction == -1:
            print row[0], number, ' @ ', float(row[6]), '該賣囉, 今年累計：', result["ROI"], '%'
        elif prediction == 0:
            print row[0], number, ' @ ', float(row[6]), '不要動, 今年累計：', result["ROI"], '%'

if __name__ == '__main__':
    sys.exit(main())