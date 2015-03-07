#!/bin/python
# -*- coding: utf-8 -*-

import csv
from config import *
from os.path import join

class Reader():
    '''To Read file'''
    def __init__(self, number):
        self.path = join(TSEC_DATA_PATH, number + '.csv')
        try:
            csvfile = open(self.path, 'rb')
            self.csvreader = csv.reader(csvfile, delimiter=',')
        except IOError:
            return None
        
    def getInput(self):
        try:
            while True:
                row = self.csvreader.next()
                if len(row) != 9:
                    raise Exception("Data Error")
                elif row[3] == '--' or row[4] == '--' or row[5] == '--' or row[6] == '--':
                    continue
                elif float(row[6]) == 0:
                    continue
                elif float(row[1]) == 0:
                    continue
                else:
                    return row
        except StopIteration:
            return None
        except Exception as e:
            print e
            return None