# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 22:25:08 2017

@author: Patrick Vacek
"""

#Determining the location of shots, starting with a single easy game.

import os
import numpy as np
import pandas as pd

os.chdir('E:/ProjectTimDuncan')
playershot=pd.read_csv('playershotsdf.csv')

os.chdir('E:/output')
thegame=pd.read_csv('01.01.2016.CHA.at.TOR_0021500492.csv')

#Subset the shot data by game

gameshot=playershot.loc[playershot['GAME_ID']==21500492]

#Plot the XY data

import matplotlib.pyplot as plt

gameshot.plot(x="LOC_X",y="LOC_Y",kind="scatter",alpha=.1)

#Look at a single shot

shot1=thegame[(thegame["qtr"]==2)&(thegame["time"]>=426)&(thegame["time"]<=428)]

shot1sort=shot1.sort_values(by="time",ascending=False)

#This function is unfinished.

def findReleasePoint(qtr,time):
    shot=thegame[(thegame["qtr"]==2)&(thegame["time"]>=time+3)&(thegame["time"]<=time)]
    shot_sort=shot.sort_values(by="time",ascending=False)

    