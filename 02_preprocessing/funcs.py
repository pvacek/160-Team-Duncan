#ESSENTIAL SportVU functions

def sidingAlgorithm(game):
    #Find our candidate shot
    left_shots=np.where(game.SHOT_ZONE_AREA=="Left Side(L)")
    the_shot=game.iloc[np.min(left_shots),:]
    
    #Determine the team that took the shot
    shot_team=the_shot.TEAM_NAME
    
    #Set indicators based on shot.
    if the_shot.LOC_X>0:
        side_indicator=np.where(game.TEAM_NAME==shot_team,1,0)
    else:
        side_indicator=np.where(game.TEAM_NAME==shot_team,0,1)
        
    #Flip indicator for 2nd half.
    side_indicator[np.where(game.PERIOD>2)[0]]=1-side_indicator[np.where(game.PERIOD>2)[0]]
    left_right_map=np.vectorize(lambda x: "Left" if x == 1 else "Right")
    sides_labeled=left_right_map(side_indicator)
    
    #Set the sides dataframe to the shot dataframe
    shot_df=pd.DataFrame(sides_labeled,columns=["SIDE"])
    game_with_sides=pd.concat([game,shot_df],axis=1)
    return(game_with_sides)

def NBA_to_SportVU(game):
    Y=game.LOC_X/10+25
    Y_star=np.array(game.SIDE=="Left")*(50-Y)+np.array(game.SIDE=="Right")*Y
    X=game.LOC_Y/10+5
    X_star=np.array(game.SIDE=="Left")*X+np.array(game.SIDE=="Right")*(94-X)
    return(np.array([X_star,Y_star]).T)
	
def distMat(row):
    ball_xy=row[4:6]
    player_index=np.linspace(8,35,10,dtype="int")
    all_xy=np.vstack([ball_xy]+[row[i:(i+2)] for i in player_index]).astype(float)
    dist_mat=squareform(pdist(all_xy))
    return(dist_mat)
	
def setDistances(motion):
    distance_matrices=[distMat(row) for row in motion.values]
    ball_distances=pd.DataFrame([d[0][1:] for d in distance_matrices])
    return(distance_matrices,ball_distances)
	
def closestPlayerAlgorithm(motion,ball_dist):
    player_index=pd.Series(np.linspace(7,34,10,dtype="int"))
    player_num=ball_dist.idxmin(axis=1)
    player_col=player_num.map(player_index)
    col_names=player_col.map(pd.Series(motion.columns))
    player_ids=motion.lookup(col_names.index,col_names.values)
    closest_player=players_list.loc[player_ids]
    return(closest_player)
	
