__all__ = ['Trader', 'Reader', 'TraderRecorder', 'CandleDrawer', 'BenchYearRecorder', 'BenchModelRecorder']

from config import *
from Reader import Reader
from Trader import Trader
from CandleDrawer import CandleDrawer
from TraderRecorder import TraderRecorder
from BenchYearRecorder import BenchYearRecorder
from BenchModelRecorder import BenchModelRecorder

import os
from os.path import isdir
# create default folders
if not isdir(RESULT_PATH): os.mkdir(RESULT_PATH)
if not isdir(STOCK_FIGURE_PATH): os.mkdir(STOCK_FIGURE_PATH)
if not isdir(MODEL_FIGURE_PATH): os.mkdir(MODEL_FIGURE_PATH)
if not isdir(MODEL_RESULT_PATH): os.mkdir(MODEL_RESULT_PATH)
if not isdir(STOCK_RESULT_PATH): os.mkdir(STOCK_RESULT_PATH)
if not isdir(SIMPLE_FIG_PATH): os.mkdir(SIMPLE_FIG_PATH)
if not isdir(CANDLE_FIG_PATH): os.mkdir(CANDLE_FIG_PATH)
if not isdir(BENCHMARK_YEAR_PATH): os.mkdir(BENCHMARK_YEAR_PATH)
if not isdir(BENCHMARK_MODEL_PATH): os.mkdir(BENCHMARK_MODEL_PATH)