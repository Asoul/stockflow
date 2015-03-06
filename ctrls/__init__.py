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
result_folders = [
    STOCK_FIGURE_PATH,
    MODEL_FIGURE_PATH,
    MODEL_RESULT_PATH,
    STOCK_RESULT_PATH
]

for folder in result_folders:
    if not isdir(folder):
        os.mkdir(folder)

