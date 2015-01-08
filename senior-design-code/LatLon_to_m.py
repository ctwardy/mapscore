import math
import numpy as np
def array_to_meters(probs, center_lat, center_lon, heading,pixel_res)
#probs - numpy array of probabilities, will need size of the array
#center_lat, center_lon - central coordinates of the array
#heading - angle of orientation of the array, measured from north/y axis
#pixel_res - number of meters per pixel
	shp = probs.shape
	xs = np.zeros(shp)
	ys = np.zeros(shp)
	#convert central point to meters
	xy_c = coord_to_meters(center_lat,center_lon)
	c_index = [shp[0]/2 - 1,shp[1]/2 -1]
	for i in range(shp[0])
		dy_index = i - c_index[0]
		dy = dy_index*pixel_res
		ys[i][:] = xy_c[1] + dy
	for j in range(shp[1])
		dx_index = j - c_index[1]
		dx = dx_index*pixel_res
		xs[:][j] = xy_c[0] + dx
	#now need to rotate each x,y by the heading
	rot_matrix = np.array([[math.cos(-1*heading), -1*math.sin(-1*heading)],[math.sin(-1*heading), math.cos(-1*heading)]])
	xy_rot = np.zeros((shp[0],shp[1],2))
	for i in range(shp[0])
		for j in range(shp[1])
			xy_vec = np.array([[xs[i][j]],[ys[i][j]])
			xy_rot[i][j][:] = np.dot(rot_matrix,xy_vec)
	return xy_rot #returns array of x,y coordinates for each element of the array
def coord_to_meters(lat,lon)
	lat_degrees = float(lat)
	long_degrees = float(lng)
	
	lat_radians = float(lat_degrees)*(math.pi/180)
	long_radians = float(long_degrees)*(math.pi/180)
	
	R = 6378137
	XY = [0,0]
	XY[0] = R*math.cos(lat_radians)*math.cos(long_radians)
	XY[1] = R*math.cos(lat_radians)*math.sin(long_radians)
	Z = R*math.sin(lat_radians) #not sure if this is right/needed if pixel resolution is known
	return XY
