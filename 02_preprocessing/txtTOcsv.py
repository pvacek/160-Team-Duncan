# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 22:51:46 2017

@author: ckchiruka
"""
import pandas as pd
import sys


def parseValues(snapshot):
    lines = snapshot.replace(']', '').replace('[', '').strip('\n').split(',')
    return lines
    

def main(filename = sys.argv[1]):
    values = open(filename).readlines()
    values = [parseValues(v) for v in values]
    values = pd.DataFrame(values).drop_duplicates()
    values = values.drop([4,5,6,10,14,15,19,20,24,25,29,30,34,35,39,40,44,45,49,50,54,55,59], axis = 1)
    
    colNames = ['quarter', 'unique_id', 'sec_in_quarter', 'shot_clock', 'ball_x', 'ball_y', 'ball_z']
    for i in range(1,11):
        colNames.append('player'+str(i)+'_id')
        colNames.append('player'+str(i)+'_x')
        colNames.append('player'+str(i)+'_y')
    
    filename = filename.replace('.txt', '.csv')
    values.to_csv(filename, index = False, header = colNames)

    
if __name__ == "__main__" : main()