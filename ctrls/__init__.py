__all__ = ['Trader', 'Reader', 'TraderRecorder', 'CandleDrawer', 'BenchMarkRecorder', 'Tester']

from config import *
from Reader import Reader
from Trader import Trader
from Tester import Tester
from TraderRecorder import TraderRecorder
from CandleDrawer import CandleDrawer
from BenchMarkRecorder import BenchMarkRecorder

import os
from os.path import isdir
# create default folders
if not isdir(RESULT_PATH): os.mkdir(RESULT_PATH)
if not isdir(STOCK_FIGURE_PATH): os.mkdir(STOCK_FIGURE_PATH)
if not isdir(MODEL_FIGURE_PATH): os.mkdir(MODEL_FIGURE_PATH)
if not isdir(MODEL_RESULT_PATH): os.mkdir(MODEL_RESULT_PATH)
if not isdir(STOCK_RESULT_PATH): os.mkdir(STOCK_RESULT_PATH)