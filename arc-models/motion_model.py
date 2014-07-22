#motion model simulation
import numpy as np
#import arcpy as arc #need to convert rasters to np arrays
#from arcpy.sa import * #spatial analyst for the thing
import matplotlib.pyplot as plt                      
import matplotlib.image as img
from PIL import Image
from PIL import PngImagePlugin
from scipy.stats import rv_discrete

def tag_image(filename, p_out):#for saving and adding images
        im = Image.open(filename)
        meta = PngImagePlugin.PngInfo()
        meta.add_text("prob outside", str(p_out))
        im.save(filename,"png",pnginfo = meta)

def attract(current_r, current_theta, current_cell, sweep, rast, rast_res,dr):
        #this function will look at the attractiveness of the 10 directions based on current position and looking direction and an input raster
        #need to use current theta to figure out which cells of slope to access
        
        attract_data= np.zeros(10)
        rel_attract = np.zeros(10)
        for i in range(10):
                sweep_cell = np.zeros(2)
                sweep_angle = current_theta + sweep[i]
                #convert negative angles to a 360 degree version and greater than 360 to right range, this should keep the angles between 0 and 360
                if (sweep_angle<0):
                        sweep_angle = sweep_angle +2*np.pi
                if (sweep_angle>2*np.pi): 
                        sweep_angle = sweep_angle -2*np.pi

                #this should work for all quadrants with the right positive negative additions
                dx = dr*np.cos(sweep_angle)
                dy = dr*np.sin(sweep_angle)#x and y components of sweep angle
                sweep_cell[0] = np.floor(dy/rast_res)
                sweep_cell[1] =  np.floor(dx/rast_res)#get the number of cells to move up/down to look
                attract_data[i] = rast[current_cell[0]+sweep_cell[0]][current_cell[1]+sweep_cell[1]]#gets actual inverses of slopes
        attract_sum = np.sum(attract_data)
        #to get relative attractiveness of slope take 1nverse of slope so that less change is bigger, than take each one over the sum over the whole thing
        rel_attract = attract_data/attract_sum
        return rel_attract#returns relative attractiveness scaled from 0 to 1
        
def avg_speed(current_cell_sl, new_theta,dr, walking_speeds, sl_res):
        #will figure out average speed/distance, need to clarify with Dr. Twardy
        #for simplicity, take average of walking speed of current cell and new cell, as long as there aren;t huge spikes this should be somewhat accurate for the average walking speed of the two places
        dx = np.floor(dr*np.cos(new_theta)/sl_res)
        dy = np.floor(dr*np.sin(new_theta)/sl_res)
        newy = current_cell_sl[0]+dy
        newx = current_cell_sl[1] + dx
        first_speed = walking_speeds[current_cell_sl[0]][current_cell_sl[1]]
        last_speed = walking_speeds[newy][newx]
        speed = (first_speed+last_speed)/2
        return speed
        
def main():

        #have land cover and slope, reclassify land cover for impedance
        #have elevation map, use arcpy to calculate slope for each cell might not need this
        #use raster to numpy array to get numpy arrays of each thing
        #use formula from ... to calculate walking speed across each cell
        #arc.env.workspace = "C:\Users\Eric Cawi\Documents\SAR\Motion Model Test"
        #elev_slope = Slope("NED","DEGREE",1)
        #impedance = Reclassify("land_cover","Value", RemapValue([[]]
        impedance_weight = .5
        slope_weight = .5
        sl = np.pi*np.ones((833,833))/180 #1 degree in radians, so there is no divide by 0 later
        #before getting inverse of slope use array to make walking speed array
        # for simplicity right now using tobler's hiking function and multiplying with the impedance weight
        walking_speeds = 6*np.exp(-3.5*np.abs(np.add(np.tan(sl),.05)))*1000/60 # speed in kmph*1000 m/km *1hr/60min
        sl = np.divide(1,sl)
        imp = np.ones((833,833))
        #walking speed weighted with land cover here from doherty paper, which uses a classification as 25 = 25% slower than normal, 100 = 100% slower than normal walking speed
        vel_weight = np.divide(np.subtract(100,imp),100)
        walking_speeds = np.multiply(vel_weight, walking_speeds) #since 1 arcsecond is roughy 30 meters the dimensions will hopefully work out
        imp = 1/imp #lower impedance is higher here, will work for probabilities
        #create easy numpy array for walking speed accross cell for walking speed calculations later

        #time interval: 15 minutes or .25 hours
        imp_res = 30 #30 meter impedance resolution from the land cover dataset
        imp_shape = imp.shape
        sl_shape = sl.shape
        sl_res = 25000/sl_shape[0] #NED should be a square so this should work for both ways, should be integer division

        end_time = 240 #arbitrary 4 hours
        #establish initial conditions in polar coordinates, using polar coordinates because i think it's easier to deal with the angles
        #r is the radius from the last known point, theta is the angle from "west"/the positive x axis through the lkp
        r = np.zeros(1000)#simulates 1000 hikers starting at ipp
        theta = np.random.uniform(0,2*np.pi,1000) #another 1000x1 array of angles, uniformly distributing heading for simulation
        stay = .05
        rev = .05#arbitrary values right now, need to discuss
        sweep = [-45 , -35 , -25 , -15 , -5 , 5 , 15 , 25 , 35, 45 , 0 , 180] #0 represents staying put 180 is a change in heading
        for i in range(len(sweep)):
                sweep[i] = sweep[i]*np.pi/180 #convert sweep angles to radians
        dr = 120 #120 meters is four cells ahead in the land cover raster which gives 9 specific cells for the sweeping angles

        #for each lookahead, have ten angles between -45 and plus 45 degrees of the current heading
        #get average impedance around 100 meters ahead, average flatness, weight each one by half
        #then scale to 1 - (prob go back + prob stay put)  these guys are all free parameters I think

        current_cell_imp = [imp_shape[0]/2 - 1, imp_shape[1]/2 - 1] #-1 is to compensate for the indeces starting at 0, starting at middle of array should represent the ipp
        current_cell_sl = [sl_shape[0]/2 - 1, sl_shape[1]/2 - 1]
        
        for i in range(1000):
                print i
                t = 0
                current_r = r[i]
                current_theta = theta[i]
                while t < end_time:
                        print t
                        
                        #look in current direction, need to figure out how to do the sweep of slope
                        slope_sweep = attract(current_r, current_theta,current_cell_sl,sweep,sl, sl_res,dr)
                        impedance_sweep = attract(current_r,current_theta,current_cell_imp,sweep, imp, imp_res,dr)
                        #goal: have relative attractiveness of both slope and land cover by taking values
                        #for slope might have a function that takes the least average change in each direction
                        #then take reciprocal to make smaller numbers bigger and take each change/sum of total to get relative goodness
                        #land cover take average 1/impedance in each direction and get relative attractiveness
                        sl_w = np.multiply(slope_sweep,slope_weight)
                        imp_w = np.multiply(impedance_sweep, impedance_weight)
                        slimp = np.add(sl_w, imp_w)
                        slimp = np.multiply(slimp,(1-(stay+rev)))
                        probabilities = np.concatenate((slimp,[stay,rev]))
                        #create a random variable with each of the 12 choices assigned the appropriate probability
                        dist = rv_discrete(values = (range(len(sweep)), probabilities))
                        ind = dist.rvs(size = 1)
                        dtheta = sweep[ind]
                        
                        if (dtheta ==0):
                                v = 0 #staying put, no change
                                dt = 10 #stay arbitrarily put for 10 minutes before making next decision
                                r_new = current_r
                                theta_new = current_theta + dtheta
                        elif (dtheta ==180):#reversal case
                                v = avg_speed(current_cell_sl, dtheta,dr,walking_speeds, sl_res)
                                dt = 120/v
                                r_new = current_r-120
                                theta_new = -1*current_theta
                        else:
                                #update the current hiker's new radius                          
                                if r[i]==0:
                                        r_new = 120
                                        theta_new = current_theta + dtheta 
                                else:
                                        r_new = np.sqrt(current_r**2 + 120**2 -2*current_r*120*np.cos(180-dtheta))#law of cosines to find new r
                                #law of sines to find new theta relative to origin, walking speeds treats each original cell as origin to calculate walking velocity
                                asin = np.arcsin(120/r_new * np.sin(180-dtheta))
                                theta_new = current_theta+asin
                                v = avg_speed(current_cell_sl,dtheta,dr,walking_speeds,sl_res)#some way to figure out either average speed or distance traveled along the line chosen
                                dt = 120/v
                        #update for current time step
                        current_r= r_new
                        current_theta= theta_new
                        t=t+dt
                        #update current_cell for slope and impedance
                        x = r[i]*np.cos(theta[i])
                        y = r[i]*np.sin(theta[i])
                        impx = np.floor(x/imp_res)
                        impy = np.floor(y/imp_res)
                        slx = np.floor(x/sl_res)
                        sly = np.floor(y/sl_res)
                        current_cell_imp = np.add(current_cell_imp , [impx,impy])
                        current_cell_sl = np.add(current_cell_sl, [slx,sly])
                #update r and theta
                r[i] = current_r
                theta[i] = current_theta
        #now that we have final positions for 1000 hikers at endtime the goal is to display/plot
        probs = np.zeros((500,500))#represents 50 meter cells with ipp at center, will get resized
        prob_outside = 0
        for i in range(1000):
                #convert radius and angle to x and y on the grid
                x = r[i]*np.cos(theta[i])/50
                y = r[i]*np.sin(theta[i])/50
                if x>499 or y>499 or x<0 or y<0:#the hiker ran far away out of hte bounding box
                        prob_outside+=1/1000
                else:
                        probs[250+y][250+x]+=1/1000 #adding 1, dividing by total number of counts to get probability, these numbers should have both positive and negative values
        #now add a small probability to those squares with 0, or something like that    
        num_0_cells = 0
        prob_0 = 0
        for i in range(500):
                for j in range(500):
                        if probs[i][j] ==0:
                                probs[i][j] = .00001#may have to change this number
                                num_0_cells +=1
                                prob_0 += .00001
        prob_outside = prob_outside*(1-prob_0)
        for i in range(500):
                for j in range(500):
                        if probs[i][j]>.00001:
                                probs[i][j] = probs[i][j]*(1-prob_0)#scaling everything to sum to 1
        print probs
        print prob_outside
        case_name = 'test'
        #example plotting for testing:
        plt.title("Motion Model Test")
        plt.imshow(probs,cmap = 'cist_gray')
        plt.colorbar()
        name = 'C:/Users/Eric Cawi/Documents/SAR/motion_model_test/%s.png' %case_name
        plt.imsave(name, probs, cmap = 'gist_gray')
        tag_image(name, prob_outside)
        #now want to resize the image to be 5001 x5001 as required by mapscore
        img = Image.open(name)
        img = img.resize((5001,5001), Image.BILINEAR)
        img.save(name)
main()
