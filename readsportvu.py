import os
import pandas as pd
import numpy as np
import re

###DATA LOADING FUNCTIONS###

def initializeShots(path="",loadGitHub=True):
    if loadGitHub==False:
        try:
            nba_shots=pd.read_csv(path+"playershotsdf.csv")
            print("Loaded from directory.")
            return(nba_shots)
        except:
            print("File not found. Using GitHub instead")
            loadGitHub=True
    if loadGitHub==True:
        nba_shots=pd.read_csv("https://raw.githubusercontent.com/pvacek/160-Team-Duncan/master/playershotsdf.csv")
        print("Loaded from GitHub.")
        return(nba_shots)

def loadGameData(file,shot_df,shot_path="",loadShots=False):
    #Set directory to where the ball motion csvs exist, load ball motion data
    motion=pd.read_csv(file)
    
    #Load in the data if asked for.
    if loadShots==True:
        nba_shots=initializeShots(directory=path,loadGitHub=True)
    else:
        nba_shots=shot_df
        
    #Find the matching data within the NBA shot data.
    game_id=int(re.sub("(^.+\_00|\.csv)","",file))
    game=nba_shots[nba_shots["GAME_ID"]==game_id]
    
    #Return the two files.
    return(motion,game)
	
###DATA PROCESSING FUNCTIONS###

def ShotLink(motion,time,qtr):
    motion_subset=motion[motion["qtr"]==qtr]
    closest_point=np.argmin((motion_subset.time-time)**2)
    return(closest_point)

def makeChunks(motion,game,time):
    num_shots=len(game)
    point_set=[ShotLink(motion,time[i],game.PERIOD.values[i]) for i in range(num_shots)]
    midpoints=np.vstack((0,np.round(pd.DataFrame(np.sort(point_set)).rolling(2).mean()[1:]),len(motion)))
    midpoint_set=np.array([midpoints[i:(i+2)] for i in range(len(game))],dtype="int64").reshape(num_shots,2)
    shot_chunks=[motion.iloc[midpoint_set[i,0]:midpoint_set[i,1],:] for i in range(num_shots)]
    return(shot_chunks)

def quickSide(chunks,game):
    #Data stuff
    half=np.where(game.PERIOD<=2,"1st","2nd+")
    first_half=game[half=="1st"]
    team_names=np.unique(game.TEAM_NAME)
    
    #Initialize an identity vector
    half_vector=np.where(half=="1st",0,1)
    team_vector=np.where(game.TEAM_NAME==team_names[0],0,1)
    id_vector=2*half_vector+team_vector
    
    #Find the average x location of shots in the first half
    x_means=np.array([np.mean(chunks[i].x) for i in range(len(first_half))])
    x_on_left=np.where(x_means<=50,"Left","Right")
    shot_table=pd.crosstab(first_half.TEAM_NAME,x_on_left)
    
    #Map the identities to sides depending on where teams shot in the first half
    if np.argmax(shot_table.iloc[:,0])==team_names[0]:
        shot_sides=pd.Series(id_vector).map({0:"Left",1:"Right",2:"Right",3:"Left"})
    else:
        shot_sides=pd.Series(id_vector).map({0:"Right",1:"Left",2:"Left",3:"Right"})
    shot_df=pd.DataFrame(shot_sides,columns=["SIDE"])
    game_with_sides=pd.concat([game,shot_df],axis=1)
    return(game_with_sides)

def NBA_to_SportVU(game):
    #Convert NBA API coordinates to SportVU coordinates
    Y=game.LOC_X/10+25
    Y_star=np.array(game.SIDE=="Left")*(50-Y)+np.array(game.SIDE=="Right")*Y
    X=game.LOC_Y/10+5
    X_star=np.array(game.SIDE=="Left")*X+np.array(game.SIDE=="Right")*(94-X)
    return(np.array([X_star,Y_star]).T)

def enhanceChunk(index,chunk,shot_val,game_side):
    chunk_XY=chunk.iloc[:,4:6].values
    chunk_id=pd.DataFrame(np.repeat([index],len(chunk)),columns=["id"])
    dshot=np.array([np.linalg.norm(chunk_XY[i]-shot_val) for i in range(len(chunk))])
    hoop_val=np.where(game_side=="Left",np.array([5,25]),np.array([89,25]))
    dhoop=np.array([np.linalg.norm(chunk_XY[i]-hoop_val) for i in range(len(chunk))])
    distance_df=pd.DataFrame(np.vstack([dshot,dhoop]).T,columns=["dshot","dhoop"])
    chunk_enhanced=pd.concat([chunk_id,chunk.reset_index(drop=True),distance_df],axis=1)
    return(chunk_enhanced)
	
def mergeSportVU(motion,game):
    game_lean=game.drop(["GRID_TYPE","SHOT_ATTEMPTED_FLAG","LOC_X","LOC_Y","MINUTES_REMAINING","SECONDS_REMAINING","EVENT_TYPE"],axis=1)
    game_indexed=game_lean.reset_index().rename(columns={'index': 'id'})
    sportVU_data=motion.merge(game_indexed,how='inner',on='id')
    return(sportVU_data)
	
def ProcessData(motion,game):
    #STEP 0: Remove any duplicated rows from the motion data
    motion_unique=motion[motion.duplicated()==False]
    
    #STEP 1: Sort the data by timestamps and event ID
    motion_sort=motion_unique.sort_values(by="stamp").reset_index(drop=True)
    game_sort=game.sort_values(by="GAME_EVENT_ID").reset_index(drop=True)
    
    #STEP 2: Combine minutes and seconds from the time variables in game.
    mins_and_secs=np.array(game_sort.MINUTES_REMAINING.values*60+game_sort.SECONDS_REMAINING.values,dtype="int64")
    
    #STEP 3: Find the sets of data where each shot could potentially exist.
    chunks_set=makeChunks(motion_sort,game_sort,mins_and_secs)
    
    #STEP 4: Use the 'siding algorithm' to determine which side each team is shooting on, redefine game data
    game_with_sides=quickSide(chunks_set,game_sort)
    
    #STEP 5: Determine where the shot locations are from the NBA API in SportVU coordinate space
    shot_XY=NBA_to_SportVU(game_with_sides)
    
    #STEP 6: Enhance the chunks by adding distance to shot location and distance to hoop
    chunks_enhanced=[enhanceChunk(i,chunks[i],shot_XY[i],game_with_sides.SIDE[i]) for i in range(len(game))]
    motion_enhanced=pd.concat(chunks_enhanced)
	
	#STEP 7: Merge our two datasets together, remove unnecessary features.
    sportVU_data=mergeSportVU(motion_enhanced,game_with_sides)
    
    return(sportVU_data)

###FINAL FUNCTION

def read_sportVU(file,shot_df,shot_path="",loadShots=False):
    print("Reading in data...")
    motion,game=loadGameData(file,shot_df,shot_path,loadShots)
    print("Processing data...")
    sportVU_data=ProcessData(motion,game)
    return(sportVU_data)
	
###EXAMPLE:
#
#Find where the files are
#os.chdir("E:/output")
#file_names=os.listdir()
#
#Initialize shot data
#nba_shots=initializeShots(path="E:/ProjectTimDuncan/",loadGitHub=False)
#
#Load the data.
#cha_tor=read_sportVU(file_names[0],nba_shots)