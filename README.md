# 股票分析程式 stock-model

這是一個可以拿來跑各式各樣測試的股市模型控制流程，可以簡單的增加自己想要的模型並測試結果。接上我的另一個專案 [台灣上市上櫃股票爬蟲，含歷史資料](https://github.com/Asoul/tsec)，就可以簡單做到歷史資料模擬、隔日評估、即時預測等功能。

## 跑過去資料模型用



### 測試特定群組資料 benchMark

一次可以測試特定的清單在一個 Model 上歷年的績效

### 測試所有資料

===================================

## 預測明日趨勢用

### findTommorrowGood

### getTomorrowHoldSituation

## 預測當下趨勢用

### findTmpGood

### findTmpHoldSituation

## 畫圖用

### 一般收盤圖

### 蠟燭圖

### MA 圖

## 模型控制流程

```python
while True:
	row = reader.getInput() # 讀新的資料
	if row == None: break # 讀不到就 Stop
	model.update(row) # 更新 model
	prediction = model.predict() # model 做決定       
	trade = trader.do(row, prediction) # 做買賣
traderRecorder.record(trader.analysis()) # 把分析記錄下來
```

## 模型元件

### Reader

- Spec: 可以讀取 tsec 單隻股票的歷史資料
- Methods: 
	- ```getInput()```: 會回傳下一天的資料

### Trader

- 可以模擬交易
- STOCK_FEE：手續費為千分之 1.425
- STOCK_TAX：證交稅為千分之三
- 交易最小單位為一張
- 一開始有 1,000,000
- Methods:
	- ```do(row, prediction)```: 把 Reader 新讀的一行 row 和 Model 輸出的 prediction 來去做買賣
	- ```analysis()```: 輸出一大堆的交易資訊結果分析
- TODO: 一次可以買很多支不同股票
- TODO: 一次最小單位為一張？

### TraderRecorder

- 可以紀錄買賣的結果成 csv 檔
- 和交易時間序列成 png 檔
- Methods:
	- ```record(result)```: 紀錄結果

## TODOs
1. 把不必要的 import 拿掉
2. update readme
3. 測試所有元件
4. 整理每份 code
5. path 改一致尾巴沒有 /
6. '104' -> this_year
7. 把每個 model 標頭的註解要改
8. drawSimple, drawMA
9. Tester 分為有 variable 和沒有 variable 的，不然會很亂
10. 把 tsrtc 接上
11. range to xrange
12. path 那邊要改成都可以改的  RESULT ..

## 控制流程局限性

1. 這個流程因為是靠當天的收盤資料來評估買賣，所以並不能反應動態的買賣結果，會有誤差。但如果只是要模擬一個較中長期的投資策略，可能就較無影響。

測試種類：
1. 知道今天價格，用收盤價買
2. 知道今天價格，明天用開盤價買
3. 知道今天價格，訂一個價格買或賣，明天價格落在這個區間中就買或賣
4. 知道今天價格，訂一個價格買或賣，明天價格落在這個區間中就買或賣，量就限最大量