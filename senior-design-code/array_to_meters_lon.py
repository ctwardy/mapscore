import math
import numpy as np
def array_to_meters_lon(arr, center_lat, center_lon,HFOV, VFOV, L,theta, alt,met_or_lon)
#arr - numpy array- probabilities or a portion of the picture with possible object in it
#center_lat, center_lon - central coordinates of the array
#hfov,vfov- horizontal and vertical fields of view
#L - focal length of camera
#theta - yaw of quad, in radians
#alt - altitude of quad
#met_or_lon - does the user want global coordinates in meters or longitude, 0 for meters, 1 for lat/lon
#this function takes arrays, along with a central point-for example tagged from a picture, and returns x,y,z or lat lon coordinates
#equations based off of "Robot Navigation", 2011 by Gerald Cook
	shp = arr.shape
	xs = np.zeros(shp)
	ys = np.zeros(shp)
	N = shp[0]
	M = shp[1]
	#convert central point to meters
	c_index = [shp[0]/2 - 1,shp[1]/2 -1]
	#convert to cartesian
	for i in range(shp[0]) #rows of array
		ys[i][:] = float(L* (N+1.0-2.0*i)/(N-1.0) * np.tan(VFOV/2)) 
	for j in range(shp[1])
		xs[:][j] = float(L* (2*j - M -1.0)/(M-1.0) * np.tan(HFOV/2)) 
	#azimuth and zenith
	az = np.atan(-1*xs/L)
	zen = np.atan(np.divide(ys, np.sqrt(L*L + np.square(xs))))
	#camera coordinates
	xc = Z*np.tan(az)
	yc = Z*np.tan(zen)
	#world coordinates, 2x2 rotation matrix * [xc,yc], rotates by yaw
	xw = xc*np.cos(theta) - yc*np.sin(theta)
	yw = xc*np.sin(theta) + yc*np.cos(theta)
	#global coordinates in meters
	R = 6371000 #average radius of earth, equatorial radius is 6378137 meters
	lat_rad = center_lat*math.pi/180.0
	lon_rad = center_lon*math.pi/180.0
	xg = np.add(R*np.cos(lat_rad), xw)
	yg = np.add(R*np.cos(lat_rad)*np.sin(lon_rad),yw)
	zg = R*np.sin(lat_rad)+Z
	if met_or_lon == 0  #users
		return xg,yg,zg
	elif met_or_lon == 1
		lats = np.atan(np.divide(Zg,np.sqrt(np.add(np.square(xg),np.square(yg)))))
		lons = np.atan(np.divide(yg,xg))#in design document it's yw/xw but I think it should be yg/xg
		return lats, lons #returns array of x,y coordinates for each element of the array
	else
		return 'bad input'

