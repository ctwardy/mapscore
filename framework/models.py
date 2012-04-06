from django.db import models
import math
import random
#from PIL import Image
import Image
from django import forms
import os

# Create your models here.


#----------------------------------------------------------------------------------
# Define Case Class

class Case(models.Model):

	# Define Database Table Fields

	#input parameters
	
	country = models.CharField(max_length = 50)
	state =  models.CharField(max_length = 50)
	county = models.CharField(max_length = 50)
	populationdensity = models.CharField(max_length = 50)
	weather = models.CharField(max_length = 50)
		
	lastlat = models.CharField(max_length = 50)
	lastlon = models.CharField(max_length = 50)
	findlat = models.CharField(max_length = 50)
	findlon = models.CharField(max_length = 50)
	case_name = models.CharField(max_length = 50)
	Age = models.CharField(max_length = 100)
	Sex = models.CharField(max_length = 100)
	key = models.CharField(max_length = 50)
	subject_category = models.CharField(max_length = 50)
	subject_subcategory = models.CharField(max_length = 50)
	scenario  = models.CharField(max_length = 50)
	subject_activity = models.CharField(max_length = 50)
	number_lost = models.CharField(max_length = 50)
	group_type = models.CharField(max_length = 50)
	ecoregion_domain = models.CharField(max_length = 50)
	ecoregion_division = models.CharField(max_length = 50)
	terrain = models.CharField(max_length = 50)
	total_hours = models.CharField(max_length = 50)
	notify_hours = models.CharField(max_length = 50)
	search_hours = models.CharField(max_length = 50)
	comments = models.CharField(max_length = 5000)
	LayerField = models.CharField(max_length = 50)
	UploadedLayers = models.BooleanField()



	# Other items
	showfind = models.BooleanField()
	upright_lat = models.CharField(max_length = 30)
	upright_lon = models.CharField(max_length = 30)
	downright_lat = models.CharField(max_length = 30)
	downright_lon = models.CharField(max_length = 30)
	upleft_lat = models.CharField(max_length = 30)
	upleft_lon = models.CharField(max_length = 30)
	downleft_lat = models.CharField(max_length = 30)
	downleft_lon = models.CharField(max_length = 30)
	findx = models.CharField(max_length = 10)
	findy = models.CharField(max_length = 10)

	sidecellnumber = models.CharField(max_length = 30)
	totalcellnumber = models.CharField(max_length = 30)

	URL = models.CharField(max_length = 1000)
	URLfind = models.CharField(max_length = 1000)

	horstep = models.CharField(max_length = 30)
	verstep = models.CharField(max_length = 30)

	# Define Great Sphere estimation script
	def GreatSphere(self,LatIn):


		Lat = math.radians(float(LatIn))

		# d = distance translated
		d = 5
		# a = earth radius in meters
		a = 6372.8 *1000

		num = 1 - math.cos(d/a)
		denom = math.pow(math.cos(Lat),2)
		full = 1 - (num/denom)
		rad_diff = math.acos(full)
		degree_diff = math.degrees(rad_diff)

		return degree_diff


	# Define Initialization Method
	def initialize(self):

		self.showfind = False

		# Map size control variables, map side length meters
		# cell side length meters

		SideLength_km_ex = 25
		cellside_m = 5

		# Define Variables
		SideLength_m_ex = SideLength_km_ex * 1000
		self.sidecellnumber = SideLength_m_ex/cellside_m + 1
		self.totalcellnumber = math.pow(self.sidecellnumber,2)
		LastLat = float(self.lastlat)
		LastLon = float(self.lastlon)
		FindLat = float(self.findlat)
		FindLon = float(self.findlon)

		#Generate boundry Coordinates

		Hor_step = self.GreatSphere(LastLat)
		ver_step = float(cellside_m) / 111122.19769903777

		self.horstep = Hor_step
		self.verstep = ver_step



		rightbound = LastLon + Hor_step/2 + ((SideLength_m_ex/cellside_m)/2)*Hor_step
		leftbound = LastLon - Hor_step/2 - ((SideLength_m_ex/cellside_m)/2)*Hor_step

		upbound = LastLat +  ver_step/2 + ((SideLength_m_ex/cellside_m)/2)*ver_step
		lowbound = LastLat -  ver_step/2 - ((SideLength_m_ex/cellside_m)/2)*ver_step

		# Generate Boundry points

		# upper right
		self.upright_lat = upbound
		self.upright_lon = rightbound

		# upper left

		self.upleft_lat = upbound
		self.upleft_lon = leftbound

		# Lower right

		self.downright_lat = lowbound
		self.downright_lon = rightbound

		# Lower left

		self.downleft_lat = lowbound
		self.downleft_lon = leftbound

		# Generate List Grids

		LonList = []
		LonList.append(leftbound)
		j = 0
		for i in (range(self.sidecellnumber)):
			j = j + 1
			LonList.append(LonList[j-1] + Hor_step)

		LatList = []
		LatList.append(upbound)
		j = 0
		for i in (range(self.sidecellnumber)):
			j = j + 1
			LatList.append(LatList[j-1] - ver_step)


		# Find Point

		# If Lon on bound --- given to the right

		ticker = 0
		for i in range(len(LonList)-1):
			if FindLon >= LonList[i] and FindLon < LonList[i+1]:
				self.findx = i
				ticker = ticker + 1

		if ticker == 0:	
			self.findx ='Out of Bounds'

		#if Lat on bound --- given to down	
		ticker = 0
		for i in range(len(LatList)-1):
			if FindLat <= LatList[i] and FindLat > LatList[i+1]:
				self.findy = i
				ticker = ticker + 1

		if ticker == 0:	
			self.findy = 'Out of Bounds'

	# *********************Generate Image from google URL*******************************

		sidepixels = 500
		#Generate url
		url = 'http://maps.google.com/maps/api/staticmap?center='
		url = url + str(self.lastlat) + ',' + str(self.lastlon)
		url = url + '&size=' + str(sidepixels) +'x' + str(sidepixels)
		url = url + '&path=color:0x0000ff|weight:5' 
		url = url + '|' + str(self.upleft_lat) + ',' +str(self.upleft_lon) + '|'
		url = url + str(self.upright_lat) + ',' +str(self.upright_lon) + '|'
		url = url + str(self.downright_lat) + ',' +str(self.downright_lon) + '|'
		url = url + str(self.downleft_lat) + ',' +str(self.downleft_lon)
		url = url + '|' + str(self.upleft_lat) + ',' +str(self.upleft_lon) 
		url = url + "&markers=color:red%7Clabel:L%7c" + str(self.lastlat) + ',' + str(self.lastlon)
		#url = url + "&markers=color:green%7Clabel:A%7c" + str(self.upleft_lat) + ',' +str(self.upleft_lon)
		#url = url + "&markers=color:green%7Clabel:B%7c" + str(self.upright_lat) + ',' +str(self.upright_lon)
		#url = url +   "&markers=color:green%7Clabel:C%7c" + str(self.downright_lat) + ',' +str(self.downright_lon)
		#url = url +   "&markers=color:green%7Clabel:D%7c" + str(self.downleft_lat) + ',' +str(self.downleft_lon)

		URLfind = url +  "&markers=color:yellow%7Clabel:F%7c" + str(self.findlat) + ',' +str(self.findlon)



		url = url + '&maptype=hybrid&sensor=false'
		URLfind = URLfind + '&maptype=hybrid&sensor=false'


		self.URL = url
		self.URLfind = URLfind

		#show find location for first 20 trials
		
		print self.id
		if self.id <= 20:
			self.showfind = True

		# Show find always --for now
		
		else:
			self.showfind = True


		# Set total time if unknown

		if self.total_hours == 'unknown' or self.total_hours == 'Unknown':
			if self.notify_hours != 'unknown' and self.notify_hours != 'Unknown' and self.search_hours != 'unknown' and self.search_hours != 'Unknown':

				total_hours = self.notify_hours+self.search_hours		

				stringout = str(total_hours) 

				self.total_hours = stringout
		
		
		# Set Layer Location
		self.LayerField  = "Layers/" + str(self.id) +'_' + str(self.case_name) + ".zip"
		self.UploadedLayers = False
		

#----------------------------------------------------------------------------------	


#----------------------------------------------------------------------------------
# Define Test Class


class Test(models.Model):

	# Define Database Table Fields
	test_case = models.ForeignKey(Case)
	test_name = models.CharField(max_length = 30)
	test_rating = models.CharField(max_length = 10)
	Active = models.BooleanField()
	ID2 = models.CharField(max_length = 100)
	nav = models.CharField(max_length = 2)
	show_instructions = models.BooleanField()

	Validated = models.BooleanField()

	Lat1 = models.CharField(max_length = 30)
	Lon1 = models.CharField(max_length = 30)
	Lat2 = models.CharField(max_length = 30)
	Lon2 = models.CharField(max_length = 30)
	Lat3 = models.CharField(max_length = 30)
	Lon3 = models.CharField(max_length = 30)
	Lat4 = models.CharField(max_length = 30)
	Lon4 = models.CharField(max_length = 30)
	Lat5 = models.CharField(max_length = 30)
	Lon5 = models.CharField(max_length = 30)
	Lat6 = models.CharField(max_length = 30)
	Lon6 = models.CharField(max_length = 30)
	Lat7 = models.CharField(max_length = 30)
	Lon7 = models.CharField(max_length = 30)
	Lat8 = models.CharField(max_length = 30)
	Lon8 = models.CharField(max_length = 30)
	Lat9 = models.CharField(max_length = 30)
	Lon9 = models.CharField(max_length = 30)


	pt1x = models.CharField(max_length = 10)
	pt1y = models.CharField(max_length = 10)
	pt2x = models.CharField(max_length = 10)
	pt2y = models.CharField(max_length = 10)
	pt3x = models.CharField(max_length = 10)
	pt3y = models.CharField(max_length = 10)
	pt4x = models.CharField(max_length = 10)
	pt4y = models.CharField(max_length = 10)
	pt5x = models.CharField(max_length = 10)
	pt5y = models.CharField(max_length = 10)
	pt6x = models.CharField(max_length = 10)
	pt6y = models.CharField(max_length = 10)
	pt7x = models.CharField(max_length = 10)
	pt7y = models.CharField(max_length = 10)
	pt8x = models.CharField(max_length = 10)
	pt8y = models.CharField(max_length = 10) 
	pt9x = models.CharField(max_length = 10)
	pt9y = models.CharField(max_length = 10)
	test_url = models.CharField(max_length = 300)
	test_url2 = models.CharField(max_length = 300)
	greyscale_path = models.CharField(max_length = 300)

	plot1xplot = models.CharField(max_length = 10)
	plot1yplot = models.CharField(max_length = 10)
	plot2xplot = models.CharField(max_length = 10)
	plot2yplot = models.CharField(max_length = 10)
	plot3xplot = models.CharField(max_length = 10)
	plot3yplot = models.CharField(max_length = 10)
	plot4xplot = models.CharField(max_length = 10)
	plot4yplot = models.CharField(max_length = 10)
	plot5xplot = models.CharField(max_length = 10)
	plot5yplot = models.CharField(max_length = 10)
	plot6xplot = models.CharField(max_length = 10)
	plot6yplot = models.CharField(max_length = 10)
	plot7xplot = models.CharField(max_length = 10)
	plot7yplot = models.CharField(max_length = 10)
	plot8xplot = models.CharField(max_length = 10)
	plot8yplot = models.CharField(max_length = 10)
	plot9xplot = models.CharField(max_length = 10)
	plot9yplot = models.CharField(max_length = 10)
	usr_p1x = models.CharField(max_length = 10)
	usr_p1y = models.CharField(max_length = 10)
	usr_p2x = models.CharField(max_length = 10)
	usr_p2y = models.CharField(max_length = 10)
	usr_p3x = models.CharField(max_length = 10)
	usr_p3y = models.CharField(max_length = 10)
	usr_p4x = models.CharField(max_length = 10)
	usr_p4y = models.CharField(max_length = 10)
	usr_p5x = models.CharField(max_length = 10)
	usr_p5y = models.CharField(max_length = 10)
	usr_p6x = models.CharField(max_length = 10)
	usr_p6y = models.CharField(max_length = 10)
	usr_p7x = models.CharField(max_length = 10)
	usr_p7y = models.CharField(max_length = 10)
	usr_p8x = models.CharField(max_length = 10)
	usr_p8y = models.CharField(max_length = 10)
	usr_p9x = models.CharField(max_length = 10)
	usr_p9y = models.CharField(max_length = 10)
	gridfresh =  models.CharField(max_length = 10)
	grayrefresh =  models.CharField(max_length = 10)

	def setup(self):
		self.gridfresh = 0
		self.grayrefresh = 0
		self.test_rating = 'unrated'
		self.Active = True
		self.Validated = False
		self.generate_testpoints()
		self.nav = 0
		self.show_instructions = True
		

		# Save
		self.save()
		
		if self.model_set.all()[0].gridvalidated == True:
			self.Validated = True
			self.nav = 2
			self.save()

	def generate_testpoints(self):

		# Clear variables
		self.plot1xplot= ''
		self.plot1yplot=''
		self.plot2xplot=''
		self.plot2yplot=''
		self.plot3xplot=''
		self.plot3yplot=''
		self.plot4xplot=''
		self.plot4yplot=''
		self.plot5xplot=''
		self.plot5yplot=''
		self.plot6xplot=''
		self.plot6yplot=''
		self.plot7xplot=''
		self.plot7yplot=''
		self.plot8xplot=''
		self.plot8yplot=''
		self.plot9xplot=''
		self.plot9yplot=''
		self.pt1x ='' 
		self.pt1y = ''
		self.pt2x = ''
		self.pt2y = ''
		self.pt3x = ''
		self.pt3y = ''
		self.pt4x = ''
		self.pt4y =''
		self.pt5x =''
		self.pt5y = ''
		self.pt6x = ''
		self.pt6y = ''
		self.pt7x = ''
		self.pt7y = ''
		self.pt8x = ''
		self.pt8y =  ''
		self.pt9x = ''
		self.pt9y = ''
		self.test_url = ''
		self.test_url2 = ''
		self.Lat1 = ''
		self.Lon1 = ''
		self.Lat2 = ''
		self.Lon2 = ''
		self.Lat3 = ''
		self.Lon3 = ''
		self.Lat4 = ''
		self.Lon4 = ''
		self.Lat5 = ''
		self.Lon5 = ''
		self.Lat6 = ''
		self.LON6 = ''
		self.Lat7 = ''
		self.Lon7 = ''
		self.Lat8 = ''
		self.Lon8 = ''
		self.Lat9 = ''
		self.Lon9 = ''
		self.usr_p1x = ''
		self.usr_p1y = ''
		self.usr_p2x = ''
		self.usr_p2y = ''
		self.usr_p3x = ''
		self.usr_p3y = ''
		self.usr_p4x = ''
		self.usr_p4y = ''
		self.usr_p5x = ''
		self.usr_p5y = ''
		self.usr_p6x = ''
		self.usr_p6y = ''
		self.usr_p7x = ''
		self.usr_p7y = ''
		self.usr_p8x =''
		self.usr_p8y =''
		self.usr_p9x = ''
		self.usr_p9y = ''


		upleftlat = float(self.test_case.upleft_lat)
		upleftlon = float(self.test_case.upleft_lon)
		uprightlat = float(self.test_case.upright_lat)
		uprightlon = float(self.test_case.upright_lon)
		downleftlat = float(self.test_case.downleft_lat)
		downleftlon = float(self.test_case.downleft_lon)
		downrightlat = float(self.test_case.downright_lat)
		downrightlon = float(self.test_case.downleft_lon)

		hordiv = (uprightlon - upleftlon)/3
		verdiv = (uprightlat - downrightlat)/3

		horbound1 = upleftlon + hordiv
		horbound2 = horbound1 + hordiv


		verbound1 = upleftlat - verdiv
		verbound2 = verbound1 - verdiv


		# row 1
		self.Lat1 =  upleftlat - (verdiv * random.uniform(0,1))
		self.Lon1 =  upleftlon + (hordiv * random.uniform(0,1))
		self.Lat2 =  upleftlat - (verdiv * random.uniform(0,1))
		self.Lon2 =  horbound1 + (hordiv * random.uniform(0,1))
		self.Lat3 =  upleftlat - (verdiv * random.uniform(0,1))
		self.Lon3 =  horbound2 + (hordiv * random.uniform(0,1))

		#row 2

		self.Lat4 = verbound1 - (verdiv * random.uniform(0,1))
		self.Lon4 = upleftlon + (hordiv * random.uniform(0,1))
		self.Lat5 = verbound1 - (verdiv * random.uniform(0,1))
		self.Lon5 = horbound1 + (hordiv * random.uniform(0,1))
		self.Lat6 = verbound1 - (verdiv * random.uniform(0,1))
		self.Lon6 = horbound2 + (hordiv * random.uniform(0,1))

		# row 3

		self.Lat7 = verbound2 - (verdiv * random.uniform(0,1))
		self.Lon7 = upleftlon + (hordiv * random.uniform(0,1))
		self.Lat8 = verbound2 - (verdiv * random.uniform(0,1))
		self.Lon8 = horbound1 + (hordiv * random.uniform(0,1))
		self.Lat9 = verbound2 - (verdiv * random.uniform(0,1))
		self.Lon9 = horbound2 + (hordiv * random.uniform(0,1))

		# Calculate grid locations


		 # Generate List Grids

		LonList = []
		LonList.append(upleftlon)
		j = 0
		for i in (range(int(self.test_case.sidecellnumber))):
			j = j + 1
			LonList.append(LonList[j-1] + float(self.test_case.horstep))

		LatList = []
		LatList.append(upleftlat)
		j = 0
		for i in (range(int(self.test_case.sidecellnumber))):
			j = j + 1
			LatList.append(LatList[j-1] - float(self.test_case.verstep))

#****************************************************************************************		
		# Find Point 1

		# If Lon on bound --- given to the right

		ticker = 0
		for i in range(len(LonList)-1):
			if self.Lon1 >= LonList[i] and self.Lon1 < LonList[i+1]:
				self.pt1x = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt1x ='Out of Bounds'

		#if Lat on bound --- given to down	
		ticker = 0
		for i in range(len(LatList)-1):
			if self.Lat1 <= LatList[i] and self.Lat1 > LatList[i+1]:
				self.pt1y = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt1y = 'Out of Bounds'

#****************************************************************************************		
		# Find Point 2

		# If Lon on bound --- given to the right

		ticker = 0
		for i in range(len(LonList)-1):
			if self.Lon2 >= LonList[i] and self.Lon2 < LonList[i+1]:
				self.pt2x = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt2x ='Out of Bounds'

		#if Lat on bound --- given to down	
		ticker = 0
		for i in range(len(LatList)-1):
			if self.Lat2 <= LatList[i] and self.Lat2 > LatList[i+1]:
				self.pt2y = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt2y = 'Out of Bounds'		

#****************************************************************************************		
		# Find Point 3

		# If Lon on bound --- given to the right

		ticker = 0
		for i in range(len(LonList)-1):
			if self.Lon3 >= LonList[i] and self.Lon3 < LonList[i+1]:
				self.pt3x = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt3x ='Out of Bounds'

		#if Lat on bound --- given to down	
		ticker = 0
		for i in range(len(LatList)-1):
			if self.Lat3 <= LatList[i] and self.Lat3 > LatList[i+1]:
				self.pt3y = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt3y = 'Out of Bounds'		

#****************************************************************************************		
		# Find Point 4

		# If Lon on bound --- given to the right

		ticker = 0
		for i in range(len(LonList)-1):
			if self.Lon4 >= LonList[i] and self.Lon4 < LonList[i+1]:
				self.pt4x = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt4x ='Out of Bounds'

		#if Lat on bound --- given to down	
		ticker = 0
		for i in range(len(LatList)-1):
			if self.Lat4 <= LatList[i] and self.Lat4 > LatList[i+1]:
				self.pt4y = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt4y = 'Out of Bounds'		


#****************************************************************************************		
		# Find Point 5

		# If Lon on bound --- given to the right

		ticker = 0
		for i in range(len(LonList)-1):
			if self.Lon5 >= LonList[i] and self.Lon5 < LonList[i+1]:
				self.pt5x = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt5x ='Out of Bounds'

		#if Lat on bound --- given to down	
		ticker = 0
		for i in range(len(LatList)-1):
			if self.Lat5 <= LatList[i] and self.Lat5 > LatList[i+1]:
				self.pt5y = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt5y = 'Out of Bounds'		

#****************************************************************************************		
		# Find Point 6

		# If Lon on bound --- given to the right

		ticker = 0
		for i in range(len(LonList)-1):
			if self.Lon6 >= LonList[i] and self.Lon6 < LonList[i+1]:
				self.pt6x = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt6x ='Out of Bounds'

		#if Lat on bound --- given to down	
		ticker = 0
		for i in range(len(LatList)-1):
			if self.Lat6 <= LatList[i] and self.Lat6 > LatList[i+1]:
				self.pt6y = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt6y = 'Out of Bounds'		


#****************************************************************************************		
		# Find Point 7

		# If Lon on bound --- given to the right

		ticker = 0
		for i in range(len(LonList)-1):
			if self.Lon7 >= LonList[i] and self.Lon7 < LonList[i+1]:
				self.pt7x = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt7x ='Out of Bounds'

		#if Lat on bound --- given to down	
		ticker = 0
		for i in range(len(LatList)-1):
			if self.Lat7 <= LatList[i] and self.Lat7 > LatList[i+1]:
				self.pt7y = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt7y = 'Out of Bounds'		

#****************************************************************************************		
		# Find Point 8

		# If Lon on bound --- given to the right

		ticker = 0
		for i in range(len(LonList)-1):
			if self.Lon8 >= LonList[i] and self.Lon8 < LonList[i+1]:
				self.pt8x = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt8x ='Out of Bounds'

		#if Lat on bound --- given to down	
		ticker = 0
		for i in range(len(LatList)-1):
			if self.Lat8 <= LatList[i] and self.Lat8 > LatList[i+1]:
				self.pt8y = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt8y = 'Out of Bounds'			

#****************************************************************************************		
		# Find Point 9

		# If Lon on bound --- given to the right

		ticker = 0
		for i in range(len(LonList)-1):
			if self.Lon9 >= LonList[i] and self.Lon9 < LonList[i+1]:
				self.pt9x = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt9x ='Out of Bounds'

		#if Lat on bound --- given to down	
		ticker = 0
		for i in range(len(LatList)-1):
			if self.Lat9 <= LatList[i] and self.Lat9 > LatList[i+1]:
				self.pt9y = i
				ticker = ticker + 1

		if ticker == 0:	
			self.pt9y = 'Out of Bounds'			




# Save points
#---------------------------------------------------------------------------------------
		Str = ''
		Str = Str +str( self.pt1x) + '\t' + str(self.pt1y )
		Str = Str +'\n'+str( self.pt2x) + '\t' + str(self.pt2y )
		Str = Str+'\n' +str( self.pt3x) + '\t' + str(self.pt3y )
		Str = Str +'\n'+str( self.pt4x) + '\t' + str(self.pt4y )
		Str = Str+'\n' +str( self.pt5x) + '\t' + str(self.pt5y )
		Str = Str +'\n'+str( self.pt6x) + '\t' + str(self.pt6y )
		Str = Str +'\n'+str( self.pt7x) + '\t' + str(self.pt7y )
		Str = Str+'\n' +str( self.pt8x) + '\t' + str(self.pt8y )
		Str = Str +'\n'+str( self.pt9x) + '\t' + str(self.pt9y )




		file = open('temp.txt','w')
		file.write(Str)
		file.close()
		print Str
#----------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------		


		# Build Image

		# ****** Update Path ********
		#im = Image.open('C:/Users/Nathan Jones/Django Website/MapRateWeb/in_images/base_grid.png')
		im = Image.open('in_images/base_grid.png')
		pix = im.load()

		pt1x_plot = round(float(self.pt1x)/10)
		pt1y_plot = round(float(self.pt1y)/10)
		pt2x_plot = round(float(self.pt2x)/10)
		pt2y_plot = round(float(self.pt2y)/10)
		pt3x_plot = round(float(self.pt3x)/10)
		pt3y_plot = round(float(self.pt3y)/10)
		pt4x_plot = round(float(self.pt4x)/10)
		pt4y_plot = round(float(self.pt4y)/10)
		pt5x_plot = round(float(self.pt5x)/10)
		pt5y_plot = round(float(self.pt5y)/10)
		pt6x_plot = round(float(self.pt6x)/10)
		pt6y_plot = round(float(self.pt6y)/10)
		pt7x_plot = round(float(self.pt7x)/10)
		pt7y_plot = round(float(self.pt7y)/10)
		pt8x_plot = round(float(self.pt8x)/10)
		pt8y_plot = round(float(self.pt8y)/10)
		pt9x_plot = round(float(self.pt9x)/10)
		pt9y_plot = round(float(self.pt9y)/10)

		# Set Image

		pixelwidth = 11
		halfwidth = 5

		# cell 1
		if pt1x_plot <10:
			pt1x_plot = 10



		if pt1y_plot <10:
			pt1y_plot = 10


		for i in range (pixelwidth):
			for j in range(pixelwidth):

				pix[pt1x_plot - halfwidth + j,pt1y_plot + halfwidth -i] = (173,255,47,255)

		self.plot1xplot = int(pt1x_plot)
		self.plot1yplot = int(pt1y_plot)


		# cell 2


		if pt2y_plot <10:
			pt2y_plot = 10


		for i in range (pixelwidth):
			for j in range(pixelwidth):

				pix[pt2x_plot - halfwidth + j,pt2y_plot + halfwidth -i] = (173,255,47,255)

		self.plot2xplot = int(pt2x_plot)
		self.plot2yplot = int(pt2y_plot)

		# cell 3
		if pt3x_plot >493:
			pt3x_plot = 493

		if pt3y_plot <10:
			pt3y_plot = 10


		for i in range (pixelwidth):
			for j in range(pixelwidth):

				pix[pt3x_plot - halfwidth + j,pt3y_plot + halfwidth -i] = (173,255,47,255)

		self.plot3xplot = int(pt3x_plot)
		self.plot3yplot = int(pt3y_plot)

		# cell 4


		if pt4x_plot <10:
			pt4x_plot = 10		

		for i in range (pixelwidth):
			for j in range(pixelwidth):

				pix[pt4x_plot - halfwidth + j,pt4y_plot + halfwidth -i] = (173,255,47,255)


		self.plot4xplot = int(pt4x_plot)
		self.plot4yplot = int(pt4y_plot)

		# cell 5


		for i in range (pixelwidth):
			for j in range(pixelwidth):

				pix[pt5x_plot - halfwidth + j,pt5y_plot + halfwidth -i] = (173,255,47,255)

		self.plot5xplot = int(pt5x_plot)
		self.plot5yplot = int(pt5y_plot)

		# cell 6

		if pt6x_plot > 493:
			pt6x_plot = 493

		for i in range (pixelwidth):
			for j in range(pixelwidth):

				pix[pt6x_plot - halfwidth + j,pt6y_plot + halfwidth -i] = (173,255,47,255)

		self.plot6xplot = int(pt6x_plot)
		self.plot6yplot = int(pt6y_plot)

		# cell 7

		if pt7x_plot <10:
			pt7x_plot = 10

		if pt7y_plot > 493:
			pt7y_plot = 493

		for i in range (pixelwidth):
			for j in range(pixelwidth):

				pix[pt7x_plot - halfwidth + j,pt7y_plot + halfwidth -i] = (173,255,47,255)

		self.plot7xplot = int(pt7x_plot)
		self.plot7yplot = int(pt7y_plot)
		# cell 8

		if pt8y_plot > 493:
			pt8y_plot = 493


		for i in range (pixelwidth):
			for j in range(pixelwidth):

				pix[pt8x_plot - halfwidth + j,pt8y_plot + halfwidth -i] = (173,255,47,255)

		self.plot8xplot = int(pt8x_plot)
		self.plot8yplot = int(pt8y_plot)
		# cell 9

		if pt9y_plot > 493:
			pt9y_plot = 493


		if pt9x_plot > 493:
			pt9x_plot = 493

		for i in range (pixelwidth):
			for j in range(pixelwidth):

				pix[pt9x_plot - halfwidth + j,pt9y_plot + halfwidth -i] = (173,255,47,255)

		self.plot9xplot = int(pt9x_plot)
		self.plot9yplot = int(pt9y_plot)

		# reformat ID2
		st = str(self.ID2)
		temp = ''
		for i in st:
			if i == ':':
				temp = temp +'_'
			else:
				temp = temp + str(i)
		
		# Iterate counter
		self.gridfresh = int(self.gridfresh) + 1
		self.save()

		#string = 'C:/Users/Nathan Jones/Django Website/MapRateWeb/media'
		string = 'media'
		string = string + '/t_' + str(temp) + '_' + str(self.gridfresh) +  '.png'

		string2 = '/media'+ '/t_' + str(temp) + '_' + str(self.gridfresh) +'.png'
		self.test_url = string2
		self.test_url2 = string
		im.save(string)

		# Save
		self.save()
#****************************************************************************************
# Define assessment function
	def Assessment(self, p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y,p5x,p5y,p6x,p6y,p7x,p7y,p8x,p8y,p9x,p9y):

		# Define input variable
		in_p1x = int(p1x)
		in_p1y = int(p1y)
		in_p2x = int(p2x)
		in_p2y = int(p2y)
		in_p3x = int(p3x)
		in_p3y = int(p3y)
		in_p4x = int(p4x)
		in_p4y = int(p4y)
		in_p5x = int(p5x)
		in_p5y = int(p5y)
		in_p6x = int(p6x)
		in_p6y = int(p6y)
		in_p7x = int(p7x)
		in_p7y = int(p7y)
		in_p8x = int(p8x)
		in_p8y = int(p8y)
		in_p9x = int(p9x)
		in_p9y = int(p9y)

		self.usr_p1x = in_p1x
		self.usr_p1y = in_p1y
		self.usr_p2x = in_p2x
		self.usr_p2y = in_p2y
		self.usr_p3x = in_p3x
		self.usr_p3y = in_p3y
		self.usr_p4x = in_p4x
		self.usr_p4y = in_p4y
		self.usr_p5x = in_p5x
		self.usr_p5y = in_p5y
		self.usr_p6x = in_p6x
		self.usr_p6y = in_p6y
		self.usr_p7x = in_p7x
		self.usr_p7y = in_p7y
		self.usr_p8x = in_p8x
		self.usr_p8y = in_p8y
		self.usr_p9x = in_p9x
		self.usr_p9y = in_p9y



		# Compile into lists to make comparison easier
		inlist = [[in_p1x,in_p1y],[in_p2x,in_p2y],[in_p3x,in_p3y],[in_p4x,in_p4y],[in_p5x,in_p5y],[in_p6x,in_p6y],[in_p7x,in_p7y],[in_p8x,in_p8y],[in_p9x,in_p9y]]
		existlist = [[int(self.pt1x),int(self.pt1y)],[int(self.pt2x),int(self.pt2y)],[int(self.pt3x),int(self.pt3y)],[int(self.pt4x),int(self.pt4y)],[int(self.pt5x),int(self.pt5y)],[int(self.pt6x),int(self.pt6y)],[int(self.pt7x),int(self.pt7y)],[int(self.pt8x),int(self.pt8y)],[int(self.pt9x),int(self.pt9y)]]


		# get actual plot points
		pt1x_plot = int(self.plot1xplot)
		pt1y_plot = int(self.plot1yplot)
		pt2x_plot = int(self.plot2xplot)
		pt2y_plot = int(self.plot2yplot)
		pt3x_plot = int(self.plot3xplot)
		pt3y_plot = int(self.plot3yplot)
		pt4x_plot = int(self.plot4xplot)
		pt4y_plot = int(self.plot4yplot)
		pt5x_plot = int(self.plot5xplot)
		pt5y_plot = int(self.plot5yplot)
		pt6x_plot = int(self.plot6xplot)
		pt6y_plot = int(self.plot6yplot)
		pt7x_plot = int(self.plot7xplot)
		pt7y_plot = int(self.plot7yplot)
		pt8x_plot = int(self.plot8xplot)
		pt8y_plot = int(self.plot8yplot)
		pt9x_plot = int(self.plot9xplot)
		pt9y_plot = int(self.plot9yplot)


		existlist_scaled =[[pt1x_plot,pt1y_plot],[pt2x_plot,pt2y_plot],[pt3x_plot,pt3y_plot],[pt4x_plot,pt4y_plot],[pt5x_plot,pt5y_plot],[pt6x_plot,pt6y_plot],[pt7x_plot,pt7y_plot],[pt8x_plot,pt8y_plot],[pt9x_plot,pt9y_plot]]
		correctlist =[]

	#import graph

	# ****** Update Path ********
		im = Image.open(self.test_url2)
		pix = im.load()


		pixelwidth = 11
		halfwidth = 5

		for m in range(len(inlist)):


			# if correct
			if inlist[m][0] == existlist[m][0]  and inlist[m][1] == existlist[m][1]:
				correctlist.append(True)

				for i in range (pixelwidth):
					for j in range(pixelwidth):

						pix[existlist_scaled[m][0] - halfwidth + j,existlist_scaled[m][1] + halfwidth -i] = (255,255,255,255)

				for i in range (5):
					for j in range(11-2*(i)):

						pix[existlist_scaled[m][0] - 5 + i+ j,existlist_scaled[m][1] -5 + i] = (0,0,255,255)

				pix[existlist_scaled[m][0],existlist_scaled[m][1]] = (0,0,255,255)

				for i in range (5):
					for j in range(11-2*(i)):

						pix[existlist_scaled[m][0] - 5 + i+ j,existlist_scaled[m][1] +5 - i] = (0,0,255,255)


			# Else

			else:

				ptx_plot = round(float(inlist[m][0])/10)
				pty_plot = round(float(inlist[m][1])/10)

				if pty_plot <10:
					pty_plot = 10

				if ptx_plot <10:
					ptx_plot = 10

				if pty_plot > 493:
					pty_plot = 493

				if ptx_plot >493:
					ptx_plot = 493

				correctlist.append(False)



				for i in range (5):
					for j in range(11-2*(i)):

						pix[ptx_plot - 5 + i,pty_plot -5 +j + i] = (255,0,0,255)

				pix[ptx_plot,pty_plot] = (255,0,0,255)

				for i in range (5):
					for j in range(11-2*(i)):

						pix[ptx_plot + 5 - i,pty_plot -5 +j + i] = (255,0,0,255)


		# Remove Old Image
		os.remove(self.test_url2)
		
		
		# reformat ID2
		st = str(self.ID2)
		temp = ''
		for i in st:
			if i == ':':
				temp = temp +'_'
			else:
				temp = temp + str(i)
		
		
		# Iterate counter
		self.gridfresh = int(self.gridfresh) + 1
		self.save()

		#string = 'C:/Users/Nathan Jones/Django Website/MapRateWeb/media'
		string = 'media'
		string = string + '/t_' + str(temp) + '_' + str(self.gridfresh) +  '.png'

		string2 = '/media'+ '/t_' + str(temp) + '_' + str(self.gridfresh) +'.png'
		self.test_url = string2
		self.test_url2 = string
		im.save(string)

		# Save
		self.save()


		return correctlist

#...............................................................................................
# Rating script
#..............................................................................................

	def rate(self):

		Path =self.greyscale_path

		Im = Image.open(Path)
		PixelArray = Im.load()
		Bands = Im.getbands()
		AllValues = Im.getdata()

		#Determine if ImageRGB 

		if Bands[0] == "R" and Bands[1] =="G" and Bands[2] == "B":

			#Ensure Image is Greyscale
			Check = 0
			for i in AllValues:
				if i[0] == i[1] and i[1] == i[2]:
					Check = Check
				else:
					Check = Check + 1

			if Check == 0:
				# Extract find location pixel value
				FindArray = PixelArray[int(self.test_case.findx),int(self.test_case.findy)]
				FindValue = FindArray[1]

				TotalUnits = 0
				Greater = 0
				Equal = 0
				for i in AllValues:
					TotalUnits = TotalUnits + 1
					if i[1] > FindValue:
						Greater = Greater + 1
					if i[1] == FindValue:
						Equal = Equal + 1

				# get r value
				r = (float(Greater)+ (float(Equal)/2)) / float(TotalUnits)

				#Get r value
				R = (0.5 - r)/0.5

				# Set rating
				self.test_rating = round(R,6)

				# ping Model

				self.Active = False
				self.save()
				self.model_set.all()[0].update_rating()


				return 0


			# Not Greyscale
			else:		
				return 1


		# Determine if image greyscale		
		elif Bands[0] == "L" or Bands[0] == "P":



			# Extract find location pixel value
			FindArray = PixelArray[int(self.test_case.findx),int(self.test_case.findy)]
			FindValue = FindArray

			TotalUnits = 0
			Greater = 0
			Equal = 0
			for i in AllValues:
				TotalUnits = TotalUnits + 1
				if i > FindValue:
					Greater = Greater + 1
				elif i == FindValue:
					Equal = Equal + 1	

			# get r value
			r = (float(Greater)+ (float(Equal)/2)) / float(TotalUnits)

			#Get r value
			R = (0.5 - r)/0.5

			#Set rating 
			self.test_rating =  round(R,5)

			# ping Model

			self.Active = False
			self.save()
			self.model_set.all()[0].update_rating()


			return 0

		# Not Greyscale or Rgb
		else:

			return 2


		# Save
		self.save()

#----------------------------------------------------------------------------------
# Define Model Class



class Model(models.Model):

	# Define Database Table Fields
	Completed_cases = models.CharField(max_length = 30)
	model_nameID = models.CharField(max_length = 30)
	gridvalidated = models.BooleanField()
	model_tests = models.ManyToManyField(Test, through = 'Test_Model_Link')
	model_avgrating = models.CharField(max_length = 10)
	ID2 = models.CharField(max_length = 100)
	Description = models.TextField()
	
	
	def setup(self):
		self.model_avgrating = 'unrated'
		self.Completed_cases = 0
		self.gridvalidated = False
		# Save
		self.save()

	def update_rating(self):

		counter = 0
		add = float(0)
		for i in self.model_tests.all():

			if i.Active == False:
				counter = counter + 1
				add = add + float(i.test_rating)



		if counter == 0:

			self.model_avgrating = 'unrated'

		else:

			self.model_avgrating = round(add / len(self.model_tests.all()),5)


		# Save
		self.save()

#----------------------------------------------------------------------------------			



#----------------------------------------------------------------------------------
# Define Account Class


class Account(models.Model):

	# Define Database Table Fields
	sessionticker = models.CharField(max_length = 30)
	completedtests = models.CharField(max_length = 30)
	photolocation = models.CharField(max_length = 30)
	photourl = models.CharField(max_length = 30)
	institution_name = models.CharField(max_length = 40)
	firstname_user = models.CharField(max_length = 30)
	lastname_user = models.CharField(max_length = 30)
	username = models.CharField(max_length = 30)
	password  = models.CharField(max_length = 30)
	account_models = models.ManyToManyField(Model, through = 'Model_Account_Link')
	Email = models.EmailField()
	Website = models.URLField()
	ID2 = models.CharField(max_length = 100)
	photosizex = models.CharField(max_length = 10)
	photosizey = models.CharField(max_length = 10)
	deleted_models = models.CharField(max_length = 10)
	profpicrefresh =  models.CharField(max_length = 10)

#----------------------------------------------------------------------------------


class Model_Account_Link(models.Model):

	account = models.ForeignKey(Account)
	model = models.ForeignKey(Model)

#------------------------------------------------------------------------------------

class Test_Model_Link(models.Model):

	test = models.ForeignKey(Test)
	model = models.ForeignKey(Model)
#---------------------------------------------------------------------------------


class Mainhits(models.Model):
	hits = models.CharField(max_length = 10)

	def setup(self):
		self.hits = 0
#----------------------------------------------------------------------------------
class terminated_accounts(models.Model):
	username = models.CharField(max_length = 30)
	sessionticker = models.CharField(max_length = 30)
	completedtests = models.CharField(max_length = 30)
	institution_name = models.CharField(max_length = 30)
	modelsi = models.CharField(max_length = 30)
	deleted_models = models.CharField(max_length = 10)

