#!/bin/python
# -*- coding: utf-8 -*-

# 資料來源
TSEC_DATA_PATH = 'tsec/data/'

# 交易費率
STOCK_FEE = 0.001425
STOCK_TAX = 0.003
STOCK_MIN_FEE = 20
TRADER_INIT_MONEY = 100000000

# 繪圖設定
FIGURE_WIDTH = 16
FIGURE_HEIGHT = 9
FIGURE_DPI = 300

# 輸出位置
RESULT_PATH = 'results'

# 測試結果 csv 輸出位置
STOCK_RESULT_PATH = 'results/stock'
MODEL_RESULT_PATH = 'results/model'

# 測試結果交易圖片輸出位置
STOCK_FIGURE_PATH = 'results/tradefig-stock'
MODEL_FIGURE_PATH = 'results/tradefig-model'

# Benchmark 從民國 100 年開始測 
BENCHMARK_YEAR_START = 100
BENCHMARK_YEAR_END = 105

# Benchmark 測試結果輸出位置
BENCHMARK_YEAR_PATH = 'results/benchmark-year'
BENCHMARK_MODEL_PATH = 'results/benchmark-model'

# Testalldata 從 100 年開始測
TESTALLDATA_YEAR_START = 100

# Candle Drawer (K 線圖)
# 放置蠟燭圖的地方
CANDLE_FIG_PATH = 'results/candle'
# 蠟燭圖時間軸長度
CANDLE_FIG_LENGTH = 120
# 蠟燭圖布林通道天數
CANDLE_BOOL_NUM = 20
# 蠟燭圖布林線寬
CANDLE_FIG_LINE_WIDTH = 1
# 蠟燭寬
CANDLE_STICK_WIDTH = 0.6