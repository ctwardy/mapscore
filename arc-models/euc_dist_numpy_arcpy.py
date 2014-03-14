#children eucdist
import os
import sys
import arcpy
from arcpy.sa import *
import math #want the math library for the 
import shutil
import numpy
from osgeo import gdal

#function that creates a raster based on my array from the open source geomapping people
def array_to_raster(array,target_file):


    # You need to get those values like you did.
    x_pixels = 5001  # number of pixels in x
    y_pixels = 5001  # number of pixels in y
    PIXEL_SIZE = 5  # size of the pixel...        
    x_min = 5482529.99134679 
    y_max = -6041295.0177 # x_min & y_max are like the "top left" corner.
    #projection taken from project.prj projection parameters
    wkt_projection = 'PROJCS["USA_Contiguous_Albers_Equal_Area_Conic_USGS_version",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-96.0],PARAMETER["Standard_Parallel_1",29.5],PARAMETER["Standard_Parallel_2",45.5],PARAMETER["Latitude_Of_Origin",23.0],UNIT["Meter",1.0],AUTHORITY["ESRI",102039]]'
                             
    driver = gdal.GetDriverByName('GTiff')

    dataset = driver.Create(
        target_file,
        x_pixels,
        y_pixels,
        1,
        gdal.GDT_Float32, )

    dataset.SetGeoTransform((
        x_min,    # 0
        PIXEL_SIZE,  # 1
        0,                      # 2
        y_max,    # 3
        0,                      # 4
        -PIXEL_SIZE))  

    dataset.SetProjection(wkt_projection)
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.FlushCache()  # Write to disk.
    #return dataset, dataset.GetRasterBand(1)  #If you need to return, remenber to return  also the dataset because the band don`t live without dataset.
    #will experiment with necessity of returning
    
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

#creating euclidean distances based off of 5 meter cells
#initialize arrays
dist_array = numpy.zeros(5001,5001)
lognormal_array = numpy.zeros(5001,5001)
#make euclidean distances
for x in range(5001):
	dx = abs(2501 - x)*5
	for y in range(5001):
		dy = abs(2501 - y)*5
		euc_dist = math.sqrt(dx*dx + dy*dy)#straightline distance from central cell
		dist_array[y,x] = euc_dist #x is column index, y is row index
lognormal_array = numpy.log(dist_array) #elementwise log
for i in range(len(distances)):
	#compute normal distribution on logarithm of distances
	scaling = 1/(stdev_list[i]*math.sqrt(2*math.pi))
	temp_array = numpy.subtract(lognormal_array,mean_list(i))
	temp_array = numpy.square(temp_array)
	temp_array = numpy.negative(temp_array)
	temp_array = numpy.divide(temp_array,2*(stdev_list[i]*stdev_list[i]))
	temp_array = numpy.exp(temp_array)
	temp_array = numpy.multiply(temp_array,scaling)#final output is normal distribution of log of distances
	#create raster file using the osgeo thingamajig
	tifname = fname+"/lognormals/" + cat_list[i] +".tif"
	tranform_name = fname + "/transform_lognormals/" + cat_list[i] + ".tif"
	conversion_name = fname + "/16bitlognormals/" + cat_list[i] + ".tif"
	pngname = fname +"/lognormal_pngs/"
	array_to_raster(temp_array,tifname)
	#log transform to integersssssss  might need some tweaking
	transform_raster = 5*Int(Log2(tifname))+255
	
	transform_raster.save(transform_name)
	arcpy.CopyRaster_management(transform_name, conversion_name,"DEFAULTS","","","","","16_BIT_UNSIGNED","NONE")
	arcpy.RasterToOtherFormat_conversion(conversion_name,png_name, "PNG")
