#anim.py: animate a sequence in an NBA game
#code borrowed from: http://www.danvatterott.com/blog/2016/06/16/creating-videos-of-nba-action-with-sportsvu-data/

def draw_court(ax=None, color="gray", lw=1, zorder=0):
    
    if ax is None:
        ax = plt.gca()

    # Creates the out of bounds lines around the court
    outer = Rectangle((0,-50), width=94, height=50, color=color,
                      zorder=zorder, fill=False, lw=lw)

    # The left and right basketball hoops
    l_hoop = Circle((5.35,-25), radius=.75, lw=lw, fill=False, 
                    color=color, zorder=zorder)
    r_hoop = Circle((88.65,-25), radius=.75, lw=lw, fill=False,
                    color=color, zorder=zorder)
    
    # Left and right backboards
    l_backboard = Rectangle((4,-28), 0, 6, lw=lw, color=color,
                            zorder=zorder)
    r_backboard = Rectangle((90, -28), 0, 6, lw=lw,color=color,
                            zorder=zorder)

    # Left and right paint areas
    l_outer_box = Rectangle((0, -33), 19, 16, lw=lw, fill=False,
                            color=color, zorder=zorder)    
    l_inner_box = Rectangle((0, -31), 19, 12, lw=lw, fill=False,
                            color=color, zorder=zorder)
    r_outer_box = Rectangle((75, -33), 19, 16, lw=lw, fill=False,
                            color=color, zorder=zorder)

    r_inner_box = Rectangle((75, -31), 19, 12, lw=lw, fill=False,
                            color=color, zorder=zorder)

    # Left and right free throw circles
    l_free_throw = Circle((19,-25), radius=6, lw=lw, fill=False,
                          color=color, zorder=zorder)
    r_free_throw = Circle((75, -25), radius=6, lw=lw, fill=False,
                          color=color, zorder=zorder)

    # Left and right corner 3-PT lines
    # a represents the top lines
    # b represents the bottom lines
    l_corner_a = Rectangle((0,-3), 14, 0, lw=lw, color=color,
                           zorder=zorder)
    l_corner_b = Rectangle((0,-47), 14, 0, lw=lw, color=color,
                           zorder=zorder)
    r_corner_a = Rectangle((80, -3), 14, 0, lw=lw, color=color,
                           zorder=zorder)
    r_corner_b = Rectangle((80, -47), 14, 0, lw=lw, color=color,
                           zorder=zorder)
    
    # Left and right 3-PT line arcs
    l_arc = Arc((5,-25), 47.5, 47.5, theta1=292, theta2=68, lw=lw,
                color=color, zorder=zorder)
    r_arc = Arc((89, -25), 47.5, 47.5, theta1=112, theta2=248, lw=lw,
                color=color, zorder=zorder)

    # half_court
    # ax.axvline(470)
    half_court = Rectangle((47,-50), 0, 50, lw=lw, color=color,
                           zorder=zorder)

    hc_big_circle = Circle((47, -25), radius=6, lw=lw, fill=False,
                           color=color, zorder=zorder)
    hc_sm_circle = Circle((47, -25), radius=2, lw=lw, fill=False,
                          color=color, zorder=zorder)

    court_elements = [l_hoop, l_backboard, l_outer_box, outer,
                      l_inner_box, l_free_throw, l_corner_a,
                      l_corner_b, l_arc, r_hoop, r_backboard, 
                      r_outer_box, r_inner_box, r_free_throw,
                      r_corner_a, r_corner_b, r_arc, half_court,
                      hc_big_circle, hc_sm_circle]

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax
	
def SnapshotData(row):
    #Find ball and team locations for this row
    ball=np.vstack((row[4:7])).T
    team1=np.vstack(([np.hstack((row[i:(i+2)],0)) for i in np.linspace(8,20,5,dtype="int")]))
    team2=np.vstack(([np.hstack((row[i:(i+2)],0)) for i in np.linspace(23,35,5,dtype="int")]))
    
    snap_locations=pd.DataFrame(np.vstack([ball,team1,team2]),columns=["x","y","z"])
    snap_locations["colors"]=np.array(["orange"]+["red"]*5+["blue"]*5)
    
    return(snap_locations)
	
def animate(i):
    data=SnapshotData(motion.iloc[i,:].values)
    player_X=data.iloc[1:,0].values
    player_Y=-data.iloc[1:,1].values
    ball_X=data.iloc[0,0]
    ball_Y=-data.iloc[0,1]
    for j in range(10):
        player_circ[j].center = tuple(np.hstack((player_X[j],player_Y[j]))) #change each players xy position
    ball_circ.center = tuple(np.hstack((ball_X,ball_Y))) #change ball xy position
    ball_circ.radius = 0.5+0.1*data.iloc[0,2]
    return(tuple(player_circ) + (ball_circ,))

def init(): #this is what matplotlib's animation will create before drawing the first frame. 
    for i in range(10): #set up players
        ax.add_patch(player_circ[i])
    ax.add_patch(ball_circ) #create ball
    ax.axis('off') #turn off axis
    plt.xlim([0,101]) #set axis
    plt.ylim([-50,0])
    return(tuple(player_circ) + (ball_circ,))
	
fig = plt.figure(figsize=(15,7.5))
ax = plt.gca()

draw_court()
ax.set_xlim(( 0, 101))
ax.set_ylim((-50, 0))
player_circ=list(range(10))
ball_circ=plt.Circle((0,0), 1.1, color=[1, 0.4, 0])

for i in range(10): #create circle object and text object for each player
    if i < 5:
        player_circ[i] = plt.Circle((0,0), 1.2, facecolor="blue",edgecolor='k')
    else:
        player_circ[i] = plt.Circle((0,0), 1.2, facecolor="purple",edgecolor='k')

ani = animation.FuncAnimation(fig, animate, frames=5000, init_func=init, blit=True, interval=50, repeat=False,save_count=0)

HTML(anim.to_html5_video())