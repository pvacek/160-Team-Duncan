# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 09:37:59 2017

@author: Patrick Vacek
"""

#STA 160 Data Extraction Process

#We are now able to extract a single NBA game's PBP

import nba_py as nba
import pandas as pd

from nba_py import game

gid = '0041400122'

def getGame(gid):
    game_json=game.PlayByPlay(gid).json["resultSets"][0]
    headers=game_json["headers"]
    data=pd.DataFrame(game_json["rowSet"],columns=headers)
    return(data)
    
test_data=getGame(gid)
test_data.head()

#Making the scoreboards data

import os
import re
import numpy as np

os.chdir("E:/ProjectTimDuncan")

unique_dates=list(set([re.sub(".[A-z].+","",os.listdir()[i]) for i in range(635)]))
dates_list=[unique_dates[i].split(".") for i in range(len(unique_dates))]
dates=np.array(dates_list,dtype="int64").flatten().reshape(85,3)

scoreboards_list=[nba.Scoreboard(d[0],d[1],d[2]).line_score() for d in dates]
scoreboards_df=pd.concat(scoreboards_list).sort_values(by="GAME_DATE_EST").reset_index(drop=True)

#Making the pbp data

pbp_list=[getGame(g) for g in scoreboards_df.GAME_ID.unique()]
pbp_df=pd.concat(pbp_list).reset_index(drop=True)