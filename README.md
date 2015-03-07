# 股票分析程式 stockflow

這是一個可以拿來跑各式各樣測試的股市模型控制流程，可以簡單的增加自己想要的模型並測試結果。接上我的另一個專案 [台灣上市上櫃股票爬蟲，含歷史資料](https://github.com/Asoul/tsec)，就可以簡單做到歷史資料模擬、隔日評估、即時預測等功能。

## 主要流程邏輯

```python
while True:
    row = reader.getInput() # Reader 讀新的資料
    if row == None: break # 讀不到就 Stop    
    prediction = model.predict() # Model 做下單預測
    trade = trader.do(row, prediction) # Trader 做買賣
    model.update(row) # 更新 model
traderRecorder.record(trader.analysis())# TraderRecorder 紀錄買賣資料
```

===================================

## 常用功能

有寫幾個常用功能的範例於檔案中，可以參考使用。

- 預測明日趨勢用

    - findTmrGood：可以根據自己設定的 Model 和指定時間至今的績效，找出明天要買的清單，
    - getTmrHold：可以根據自己設定的 Model，找出現有清單中，明天該做的動作。

- 預測當下趨勢用（把今日累計資料當成是最新一天的資料來給 Model 預測）

    - findTmpGood：可以根據自己設定的 Model 和指定時間至今的績效，找出當下要買的清單，
    - findTmpHold：可以根據自己設定的 Model，找出現有清單中，當下該做的動作。

- 測試資料

    - main：基本的範例格式
    - runBenchMark：測試特定資料群組在特定年份中歷年的績效，和比較歷年績效。

- 畫圖用

    - drawSimple：一般收盤圖
    - drawCandle：蠟燭圖

===================================

## 基本控制元件

### Reader

- Spec：可以讀取 tsec 單隻股票的歷史資料
- Initialize
    - `Reader(number)`：`number` 是股票編號
- Methods
    - `getInput()`：會回傳下一天的資料，自動把沒有交易的資料過濾掉，若沒有資料了則回傳 None

### Trader

- Spec：可以模擬交易，並輸出交易資訊分析
- Initialize
    - `Trader(model_infos, stock_number)`：`model_infos` 是 Model 內建描述,`stock_number` 是股票編號
- Methods
    - `do(row, prediction)`：把 Reader 新讀的一行 row 和 Model 輸出的 prediction 來去做買賣
    - `analysis()`：輸出交易資訊結果分析

### TraderRecorder

- Spec：可以紀錄買賣的結果成 csv 檔、和把交易序列輸出成圖檔
- Methods
    - `record(result)`：把 Trader.analysis() 的結果輸出成檔案

### Tester

- Spec：可以測試 Model、預測明日趨勢、預測即時趨勢
- Methods：
    - `run(mode = 'train', noLog = False, noRecord = False, dateFrom = None, dateTo = None, roiThr = -100, drawCandle = True)`：
        - mode：有 `train`, `tmrGood`, `tmrHold`, `tmpGood`, `tmrGood` 五種
            - 所有 mode 都可以設定 `dateFrom` 和 `dateTo` 設定指定區間
            - `train` 會跑測試資料，可以選擇 `noLog = True` 和 `noRecord = True` 兩個參數
            - `tmrGood` 和 `tmpGood` 可以預測 Model 要買的清單，可以設定 `roiThr` 為輸出的最低累計 ROI 門檻。如果不輸出圖片可以設定 `drawCandle = False`
            - `tmrHold` 和 `tmpHold` 可以根據現有持有的股票，用 Model 預測下一步動作。如果不輸出圖片可以設定 `drawCandle = False`

### BenchMark

- Spec：可以測試指定股票清單和指定年份，做多年單隻股票的績效分析和同年不同模型的平均績效統計。
- Initialize
    - `BenchMark(numbers, Model)`：`numbers` 是要測試的股票清單，`Model` 是一個可以用來輸出的 Model
- Methods
    - `run(noLog = False)`：開始測試，`noLog = True` 可以把螢幕輸出關掉

### BenchYearRecorder

- Spec：可以輸出 BenchMark 測試不同年份的結果，相同年份存在同一個檔案中。
- Initialize
    - `BenchYearRecorder(model_infos, year)`：`model_infos` 是模型敘述，`year` 是年份
- Methods
    - `update(result)`：把每隻股票指定年份的結果更新
    - `record()`：輸出成 csv 檔

### BenchModelRecorder

- Spec：可以輸出 BenchMark 測試不同年份的結果，相同 Model 存在同一個檔案中。
- Initialize
    - `BenchModelRecorder(model_infos, number)`：`number` 是股票編號，`model_infos` 是模型敘述
- Methods
    - `update(result)`：把每隻股票指定年份的結果更新
    - `record()`：輸出成 csv 檔

### SimpleDrawer

- Spec：可以輸出日收盤價的圖
- Methods
    - `draw(number, length = SIMPLE_FIG_LENGTH)`：`number` 是股票編號，`length` 是想要輸出的序列長度

[](https://raw.githubusercontent.com/asoul/stockflow/master/demo/simple.png)

### CandleDrawer

- Spec：可以輸出日收盤價的圖
- Methods
    - `draw(number, length = SIMPLE_FIG_LENGTH)`：`number` 是股票編號，`length` 是想要輸出的序列長度

[](https://raw.githubusercontent.com/asoul/stockflow/master/demo/candle.png)

### 參數設定

參數設定都在 `ctrls/config.py` 中，可以設定輸出檔案位置、交易稅、起始金額等資料。

## 簡單使用測試元件

```python
numbers = ['0050']# 股票編號
tester = Tester(numbers, exampleModel)# 使用測試元件
tester.run()# 模擬
```


===================================


## TODOs
1. 把不必要的 import 拿掉

