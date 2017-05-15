# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 22:51:46 2017

@author: ckchiruka
"""
import pandas as pd
import sys


def parseValues(snapshot):
    lines=snapshot.replace(']', '').replace('[', '').strip('\n').split(',')
    return lines
    

def main(filename = sys.argv[1]):
    values = open(filename).readlines()
    values = [parseValues(v) for v in values]
    values = pd.DataFrame(values).drop_duplicates()
    filename = filename.replace('.txt', '') + '.csv'
    values.to_csv(filename)

    
if __name__ == "__main__" : main()