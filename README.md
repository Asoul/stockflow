# 股票分析程式 stockflow

這是一個拿來跑各式各樣測試的股市模型控制流程，可以簡單的增加自己想要的模型並測試結果。接上我的另一個專案 [台灣上市上櫃股票爬蟲，含歷史資料](https://github.com/Asoul/tsec)，就可以簡單做到歷史資料模擬、隔日評估、即時預測等功能。

## 起始設定

下載完本專案後，可以把之前的 [tsec](https://github.com/Asoul/tsec) 專案用 `ln -s` 放到 `stockflow` 下，或者是更改 `ctrls/settings.py` 裡面的 `TSEC_DATA_PATH` 至原本有下載過的 tsec 目錄。

## 主要流程邏輯

```python
while True:
    row = reader.getInput() # Reader 讀新的資料
    if row == None: break # 讀不到就 Stop    

    prediction = model.predict('start', float(row[3]))#決定開盤要不要買賣
    trade = trader.do(row, prediction, 'start')
    
    # 盤中 update
    model.update(row, trade)

    # 快收盤的買賣
    prediction = model.predict('end', float(row[6]))
    trade = trader.do(row, prediction, 'end')

traderRecorder.record(trader.analysis())# TraderRecorder 紀錄買賣資料
```

## 基本控制元件

### Model

#### [Spec]

一個可以預測的模型，有放上 `exampleModel` 當成範例。

#### [Methods]

`update(row, trade = None)`：根據新的資料，和新的交易結果來做更新

`predict(when, value)`：讓 model 預測下一步應該要怎麼做，模擬一個下單的過程。when 是 'start' 或 'end'，value 是開盤價或收盤價。需要回傳一個 dictionary，包含：
            
- `Act`: `Buy`, `Sell` or `Nothing`
- `Value`: 要下單的價格，0 代表用開盤價買
- `Volume`: 要下單的量，0 代表能買多少盡量買

========

### Reader

#### [Spec]

可以讀取 tsec 單隻股票的歷史資料

#### [Initialize]

`Reader(number)`：`number` 是股票編號

#### [Methods]

`getInput()`：會回傳下一天的資料，自動把沒有交易的資料過濾掉，若沒有資料了則回傳 None

========

### Trader

#### [Spec]

可以模擬交易，並輸出交易資訊分析

#### [Initialize]

`Trader(model_infos, stock_number)`：`model_infos` 是 Model 內建描述,`stock_number` 是股票編號

#### [Methods]

`do(row, prediction, when)`：把 Reader 新讀的一行 row 和 Model 輸出的 prediction 來去做買賣，when 是 'start' 或 'end'

`analysis()`：輸出交易資訊結果分析，包含很多東西不多加描述，可以直接 run 一次看看 result 裡多出什麼就知道了。

========

### TraderRecorder

#### [Spec]

可以紀錄買賣的結果成 csv 檔、和把交易序列輸出成圖檔

#### [Methods]

`record(result)`：把 Trader.analysis() 的結果輸出成檔案，可以看到圖片中紅點是 Model 買入點，藍點是賣出點，視覺化後一目了然，此外 `result` 中也有很多資料可以看。

![](https://raw.githubusercontent.com/asoul/stockflow/master/demo/trade-fig.png)

![](https://raw.githubusercontent.com/asoul/stockflow/master/demo/trade-fig2.png)

========

### Tester

#### [Spec]

可以測試 Model、預測明日趨勢、預測即時趨勢

#### [Methods]

`run(mode = 'train', noLog = False, noRecord = False, dateFrom = None, dateTo = None, roiThr = -100, drawCandle = True)`：跑測試


- mode：有 `train`, `tmrGood`, `tmrHold`, `tmpGood`, `tmrGood` 五種
- 所有 mode 都可以設定 `dateFrom` 和 `dateTo` 設定指定區間
- `train` 會跑測試資料，可以選擇 `noLog = True` 和 `noRecord = True` 兩個參數
- `tmrGood` 和 `tmpGood` 可以預測 Model 要買的清單，可以設定 `roiThr` 為輸出的最低累計 ROI 門檻。如果不輸出圖片可以設定 `drawCandle = False`
- `tmrHold` 和 `tmpHold` 可以根據現有持有的股票，用 Model 預測下一步動作。如果不輸出圖片可以設定 `drawCandle = False`

========

### BenchMark

#### [Spec]

可以測試指定股票清單和指定年份，做多年單隻股票的績效分析和同年不同模型的平均績效統計。

#### [Initialize]

`BenchMark(numbers, Model)`：`numbers` 是要測試的股票清單，`Model` 是一個可以用來輸出的 Model

#### [Methods]

`run(noLog = False)`：開始測試，`noLog = True` 可以把螢幕輸出關掉

========

### BenchYearRecorder

#### [Spec]

可以輸出 BenchMark 測試不同年份的結果，相同年份存在同一個檔案中。

#### [Initialize]

`BenchYearRecorder(model_infos, year)`：`model_infos` 是模型敘述，`year` 是年份

#### [Methods]

`update(result)`：把每隻股票指定年份的結果更新

`record()`：輸出成 csv 檔

========

### BenchModelRecorder

#### [Spec]

可以輸出 BenchMark 測試不同年份的結果，相同 Model 存在同一個檔案中。

#### [Initialize]

`BenchModelRecorder(model_infos, number)`：`number` 是股票編號，`model_infos` 是模型敘述

#### [Methods]
    
`update(result)`：把每隻股票指定年份的結果更新

`record()`：輸出成 csv 檔

========

### SimpleDrawer

#### [Spec]

可以輸出日收盤價的圖

#### [Methods]

`draw(number, length = SIMPLE_FIG_LENGTH)`：`number` 是股票編號，`length` 是想要輸出的序列長度

![](https://raw.githubusercontent.com/asoul/stockflow/master/demo/simple.png)

========

### CandleDrawer

#### [Spec]

可以輸出 K 線圖 + 布林通道 + 每日最高最低區間 + 量的圖

#### [Methods]

`draw(number, length = SIMPLE_FIG_LENGTH)`：`number` 是股票編號，`length` 是想要輸出的序列長度

![](https://raw.githubusercontent.com/asoul/stockflow/master/demo/candle.png)

========

### 參數設定

參數設定都在 `ctrls/settings.py` 中，可以設定輸出檔案位置、交易稅、起始金額等資料。

## 常用功能

有寫幾個常用功能的範例於檔案中，可以參考使用，都短短的兩三行就可以做到以下功能。

### 預測明日趨勢用

- `findTmrGood`：可以根據自己設定的 Model 和指定時間至今的績效，找出明天要買的清單，
- `getTmrHold`：可以根據自己設定的 Model，找出現有清單中，明天該做的動作。

### 預測當下趨勢用（把今日累計資料當成是最新一天的資料）

- `findTmpGood`：可以根據自己設定的 Model 和指定時間至今的績效，找出當下要買的清單，
- `findTmpHold`：可以根據自己設定的 Model，找出現有清單中，當下該做的動作。

### 測試資料

- `main`：基本的範例格式
- `testThisYearTilNow`：測試今年至今的績效
- `runBenchMark`：測試特定資料群組在特定年份中歷年的績效，和比較歷年績效。

### 畫圖用

- `drawSimple`：一般收盤圖
- `drawCandle`：蠟燭圖

## LOG

1. printTrade 改成 trader 輸出

## TODO:

1. doc 獨立開來成gh-page，要改明白一點
2. 增加融資finance、融券bearish
3. 東西命名改成 Python 一點

## 附上免責聲明

本人旨在為廣大投資人提供正確可靠之資訊及最好之服務，作為投資研究的參考依據，若因任何資料之不正確或疏漏所衍生之損害或損失，本人將不負法律責任。是否經由本網站使用下載或取得任何資料，應由您自行考量且自負風險，因任何資料之下載而導致您電腦系統之任何損壞或資料流失，您應負完全責任。

## 聯絡我

有 Bug 麻煩跟我說：`azx754@gmail.com`

最後更新時間：`2015/03/26`

## LICENSE

In short, stockflow is available under the MIT license. See the LICENSE file for more info.

## 我的其他專案

[台灣上市上櫃股票爬蟲，含歷史資料](https://github.com/Asoul/tsec)

[股票即時資料爬蟲](https://github.com/Asoul/tsrtc)
