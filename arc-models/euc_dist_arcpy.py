#children eucdist
import os
import sys
import arcpy
from arcpy.sa import *
import math #want the math library for the 
import shutil
inws = arcpy.GetParameterAsText(0)
arcpy.env.workspace = inws

opws = arcpy.GetParameterAsText(1)
arcpy.env.outworkspace = opws

arcpy.env.overwriteOutput = True
fname= inws
distances =[[0.4,0.8,2.4,5.6], [0.1,0.2,0.6,2.0], [0.1,0.2,0.6,2.0], [0.4,1.2,2.0,5.1],\
[0.1,0.5,0.9,2.3], [0.1,0.4,0.9,4.1], [0.3,0.8,2.0,4.5],\
 [0.5,1.0,2.0,7.0], [0.1,0.5,1.3,5.0], [0.5,1.3,4.5,10.0],\
 [0.5,1.0,2.0,5.6], [0.3,1.0,3.0,6.2], [1.5,2.0,3.0,7.4],\
[0.5,1.3,3.0,13.3],[0.4,0.8,2.0,6.2]]
cat_list = ["Child_1_3_Dry","Child_1_3_temperate_mountainous","Child_1_3_else",\
"Child_4_6_dry", "Child_4_6_temperature_mountainous",\
"Child_4_6_else", "Child_7_9_dry",  "Child_7_9_temperature_mountainous",\
"Child_7_9_else","Child_10_12_dry", "Child_10_12_temperature_mountainous",\
"Child_10_12_else", "Child_13_15_dry", "Child_13_15_temperature_mountainous",\
"Child_13_15_else"]
mean_list = [0.024424394, -0.315906488, -0.01235441, 0.383159187, -0.364501639,\
	-0.03288938, 0.077082908, 0.35309571, 0.250700222, 1.127894452, \
0.625782573, 0.293698202, 0.843143089, 1.135429768, 0.438267833]
stdev_list = [1.115701619, 1.375214308, 1.37931074, 1.115285789, 1.071310929, \
	1.526816248, 1.869920265, 1.319448938, 1.211225499, 1.080614521, \
1.059808558, 1.261038675, 1.613561718, 1.206598012, 1.334012835]
cell_size = 5
fctable = 'lostperson'

sr = arcpy.SpatialReference("C:/Users/Eric Cawi/Documents/SAR/database_stuff/prjfile.prj")

sr1 = arcpy.SpatialReference("WGS 1984")

#spatialref = arcpy.SpatialReference(prjFile)

#I only really need one point of reference to create a bunch of different rings around
x = 34.434933
y = -110.232333
ptlist = []
fctemp = fname  + "b25temp" + ".shp"
fcclip = fname + "Clipregion" + ".shp"
point = arcpy.Point(x,y)
pointgeometry = arcpy.PointGeometry(point)
ptlist.append(pointgeometry)
arcpy.CreateFeatureclass_management(fname + "/database_stuff/DistanceRings.gdb", "Ptfile","Point")
ptfile = fname +"/database_stuff/DistanceRings.gdb/"+  "Ptfile" 
cursor = arcpy.da.InsertCursor( ptfile,["SHAPE@"])
cursor.insertRow(list(ptlist))
del cursor
arcpy.DefineProjection_management(ptfile, sr1)
arcpy.Project_management(ptfile, fname +"/database_stuff/DistanceRings.gdb/" + "Ptfile_Project", sr, "WGS_1984_(ITRF00)_To_NAD_1983")  
arcpy.Buffer_analysis(fname +"/database_stuff/DistanceRings.gdb/" + "Ptfile_Project" , fctemp, "12.5 Kilometers")
arcpy.FeatureEnvelopeToPolygon_management(fctemp, fcclip)#creates the box? yes this creates the box for clipping everything
arcpy.env.extent = arcpy.Extent(5482529.99134679,-6066295.0177,5507529.99134679,-6041295.0177) #setting output extent to the size of the clip region
arcpy.env.outputCoordinateSystem = sr

for i in range(len(distances)):
        Buf_Distance = distances[i] #this is a list of distances for the current category
        max_dist = Buf_Distance[-1] # this sets the max distance for the eucdist function
        max_dist = max_dist * 2
        #want to convert the distance from miles to meters => 1.60934 km per mile * 1000 m/km
        max_dist = max_dist*1609.34 # sets a meter based max distance
        Euc_dist = EucDistance(ptfile, 25000,cell_size)
        Euc_dist.save(fname+"/EuclideanDistances/" + cat_list[i] +"dist.tif")
        log_dist = Ln(Euc_dist)
        const = 1/(stdev_list[i]*math.sqrt(2*math.pi))
       
        power = -(log_dist - mean_list[i])/(2*stdev_list[i]*stdev_list[i])
        log_normal_dist = const*Exp(power)
        #retransform to not logdomain, ask about pdensity
        dist_pden = Exp(log_normal_dist)#not sure if this bit is necessary or correct
        log_name = fname +"/lognormals/"+ cat_list[i] + "lognormal_dist.tif"        
        log_normal_dist.save(log_name) #saving the full lognormal files
        dist_pden.save(fname+"/normal/" + cat_list[i] + "regular_space.tif")


