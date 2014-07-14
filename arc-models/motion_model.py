#motion model simulation
import numpy as np
import arcpy as arc #need to convert rasters to np arrays
from arcpy.sa import * #spatial analyst for the thing

#have land cover and slope, reclassify land cover for impedance
#have elevation map, use arcpy to calculate slope for each cell might not need this
#use raster to numpy array to get numpy arrays of each thing
#use formula from ... to calculate walking speed across each cell
arc.env.workspace = "C:\Users\Eric Cawi\Documents\SAR\Motion Model"
elev_slope = Slope("NED","DEGREE",1)
impedance = Reclassify("land_cover","Value", RemapValue([[
impedance_weight = .5
slope_weight = .5
sl = arc.RasterToNumpyArray(elev_slope)
imp = arc.RasterToNumpyArray(impedance)
imp = 1/imp #lower impedance is higher here, will work for probabilities
#create easy numpy array for walking speed accross cell for walking speed calculations later
walking speeds = function of slope and impedance
#time interval: 15 minutes or .25 hours

dt = 15#integer for step in for loop
end_time = 120 #arbitrary 2 hours
#establish initial conditions in polar coordinates, using polar coordinates because i think it's easier to deal with the angles
#r is the radius from the last known point, theta is the angle from "west"/the positive x axis through the lkp
r = np.zeros(1000,1)#simulates 1000 hikers starting at ipp
theta = np.random.uniform(0,360,1000) #another 1000x1 array of angles, uniformly distributing heading for simulation
stay = .05
rev = .05#arbitrary values right now, need to discuss
sweep = [-45 , -35 , -25 , -15 , -5 , 5 , 15 , 25 , 35, 45 , 0 , 180] #0 represents staying put 180 is a change in heading
#for each lookahead, have ten angles between -45 and plus 45 degrees of the current heading
#get average impedance around 100 meters ahead, average flatness, weight each one by half
#then scale to 1 - (prob go back + prob stay put)  these guys are all free parameters I think
def slope_attract(current_r, current_theta,  sl):
	#this function will look at the attractiveness of the slope based on current position and looking direction

def imp_attract(current_r, current_theta, imp):
	#this function will look at the attractiveness of the land cover based on how it impedes walking


def walk_speed(current_r, new_theta, walking_speeds):
	#will figure out average speed/distance, need to clarify with Dr. Twardy

for t in range(0,end_time+dt, dt):
	print t
	for i in range(1000):
		current_r = r[i]
		current_theta = theta[i]
		#look in current direction, need to figure out how to do the sweep of slope
                slope_sweep = something(current_r, current_theta,sl)
                impedance_sweep = something_else(current_r,current_theta,imp,sl)
                #goal: have relative attractiveness of both slope and land cover by taking values
                #for slope might have a function that takes the least average change in each direction
                #then take reciprocal to make smaller numbers bigger and take each change/sum of total to get relative goodness
                #land cover take average 1/impedance in each direction and get relative attractiveness
                attract = (1-(stay+rev))*(slope_weight * slope_sweep+imp_weight*impedance_sweep)
                probabilities = np.concatenate(attract,[stay,rev])
                #create a random variable with each of the 12 choices assigned the appropriate probability
                dist = rv_discrete(values = (range(len(sweep)), probabilities))
                index = dist.rvs(size = 1)
                dtheta = sweep[index]
                updtae
                new_theta = current_theta + dtheta
                if (dtheta ==0):
                	v = 0 #staying put, no change
                else:
                	v = walk_speed(current_r,new_theta,imp,sl)#some way to figure out either average speed or distance traveled along the line chosen
                  distance = v *dt
                #update the current hiker's new radius
                r[i] = vector addition of the two vectors to get the new radius from the center

#now that we have final positions for 1000 hikers at endtime the goal is to display/plot

#convert radius and angle to x and y on the grid, 
#for each x,y, figure out which grid cell it corresponds to
#update that cell in counts array, divide by 1000 for total probability
#give cells with 0 counts a small probability, rescale other probabilities by (1-sum(smallstuff)
#potential issue:  memory sizes in arrays, won't get a 5001x5001 array, will have to scale up, changing probability density?





