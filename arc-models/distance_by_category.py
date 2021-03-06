import os
import sys
import arcpy


inws = arcpy.GetParameterAsText(0)
arcpy.env.workspace = inws

opws = arcpy.GetParameterAsText(1)
arcpy.env.outworkspace = opws

arcpy.env.overwriteOutput = True

#inMXD = "C:/SAR/Test5.mxd"
#mxd = arcpy.mapping.MapDocument(inMXD)
#df = arcpy.mapping.ListDataFrames(mxd)[0]
#newExtent = df.extent
#arcpy.env.extent = newExtent

#namelist = [];
#subject_category = [];
#stateabbrv = [];
#ecoregion_domain = [];
#terrain = [];
#lat_ = [];
#long_ = [];
#key = [];
#keystr = ''
#ptList = [];
#pointlist = [];
#pt = arcpy.Point()
#ptGeoms = []
#Distances = []
#DistancePlus = []
perct = ['25%','50%','75%','95%','100%']
ptlist = []
cat_list = ["Abduction", "Aircraft", "Angler_temperate_mountainous", \
"Angler_temperate_else", "Angler_dry","Angler_else", "All_terrain_vehicle", "Autistic_Urban",\
"Autistic_else", "Camper_mountainous_dry","Camper_mountainous_else",\
"Camper_else", "Child_1_3_Dry", "Child_1_3_urban","Child_1_3_temperate_mountainous","Child_1_3_else",\
"Child_4_6_dry", "Child_4_6_urban", "Child_4_6_temperature_mountainous",\
"Child_4_6_else", "Child_7_9_dry", "Child_7_9_urban", "Child_7_9_temperature_mountainous",\
"Child_7_9_else","Child_10_12_dry", "Child_10_12_urban", "Child_10_12_temperature_mountainous",\
"Child_10_12_else", "Child_13_15_dry", "Child_13_15_temperature_mountainous",\
"Child_13_15_else", "Climber", "Dementia_dry_mountainous", "Dementia_dry_flat",\
"Dementia_urban","Dementia_temperate_mountainous","Dimentia_else", "Despondent_dry_mountainous",\
"Despondent_dry_flat", "Despondent_urban","Despondent_temperate_mountainous", "Despondent_else",\
"Gatherer_dry", "Gatherer_else", "Hiker_dry_mountainous", "Hiker_dry_flat",\
"Hiker_temperate_mountainous","Hiker_else", "Horsebackrider", "Hunter_dry_mountainous",\
"Hunter_dry_flat", "Hunter_temperate_mountainous", "Hunter_else", "Mental_illness_urban",\
"Mental_illness_temperate_mountainous", "Mental_illness_else", "Mental_retardation_dry",\
"Mental_retardation_urban", "Mental_retardation_temperate_mountainous",\
"Mental_retardation_else", "Mountain_biker_dry", "Mountain_biker_else",\
"Other_Exsport", "Runner", "Skier_alpine", "Skier_nordic_dry", "Skier_nordic_else",\
"Snowboarder", "Snowmobiler_dry", "Snowmobiler_temperate_flat", "Snowmobiler_else",\
"Other"]


Distances = [[0.2,1.5,12.0],[0.4,0.9,3.7,10.4],[0.2,0.9,3.4,6.1],[0.5,1.0,3.4,6.1],\
[2.0,6.0,6.5,8.0], [0.5,1.0,3.4,6.1],[1.0,2.0,3.5,5.0],[0.2,0.6,2.4,5.0],\
[0.4,1.0,2.3,9.5], [0.1,1.4,1.9,24.7], [0.1,0.7,2.0,8.0], [0.4,0.8,2.4,5.6],\
[0.1,0.3,0.5,0.7], [0.1,0.2,0.6,2.0], [0.1,0.2,0.6,2.0], [0.4,1.2,2.0,5.1],\
[0.06,0.3,0.6,2.1], [0.1,0.5,0.9,2.3], [0.1,0.4,0.9,4.1], [0.3,0.8,2.0,4.5],\
[0.1,0.3,0.9,3.2], [0.5,1.0,2.0,7.0], [0.1,0.5,1.3,5.0], [0.5,1.3,4.5,10.0],\
[0.2,0.9,1.8,3.6], [0.5,1.0,2.0,5.6], [0.3,1.0,3.0,6.2], [1.5,2.0,3.0,7.4],\
[0.5,1.3,3.0,13.3],[0.4,0.8,2.0,6.2], [0.1,1.0,2.0,9.2], [0.6,1.2,1.9,3.8],\
[0.3,1.0,2.2,7.3], [0.2,0.7,2.0,7.8], [0.2,0.5,1.2,5.1], [0.2,0.6,1.5,7.9],\
[0.5,1.0,2.1,11.1], [0.3,1.2,2.3,12.8], [0.06,0.3,0.9,8.1], [0.2,0.7,2.0,13.3],\
[0.2,0.5,1.4,10.7], [1.0,1.6,3.6,6.9], [0.9,2.0,4.0,8.0], [1.0,2.0,4.0,11.9],\
[0.8,1.3,4.1,8.1], [0.7,1.9,3.6,11.3], [0.4,1.1,2.0,6.1], [0.2,2.0,5.0,12.2],\
[1.3,3.0,5.0,13.8], [1.0,1.9,4.0,7.0], [0.6,1.3,3.0,10.7], [0.4,1.0,1.9,8.5],\
[0.2,0.4,0.9,7.7], [0.4,1.4,5.1,9.0], [0.5,0.6,1.4,5.0], [0.7,2.5,5.4,38.9],\
[0.2,0.5,2.3,6.14], [0.4,1.0,2.0,7.0], [0.2,0.6,1.3,7.3], [1.7,4.0,8.2,18.1],\
[1.9,2.5,7.0,15.5], [0.3,1.6,3.5,8.3], [0.9,1.6,2.1,3.6], [0.7,1.7,3.0,9.4],\
[1.2,2.7,4.0,12.1], [1.0,2.2,4.0,12.2], [1.0,2.0,3.8,9.5], [1.0,3.0,8.7,18.9],\
[0.8,2.9,25.5,59.7], [2.0,4.0,6.9,10.0], [0.3,0.7,2.6,6.0], [0.4,1.1,2.0,6.1]]


fctable = 'lostperson'

sr = arcpy.SpatialReference("C:/Users/Eric Cawi/Documents/SAR/database_stuff/prjfile.prj")

sr1 = arcpy.SpatialReference("WGS 1984")

#spatialref = arcpy.SpatialReference(prjFile)

#I only really need one point of reference to create a bunch of different rings around
x = 34.434933
y = -110.232333
fname= "C:/Users/Eric Cawi/Documents/SAR/"
fctemp = fname + "b25temp" + ".shp"
fcclip = fname + "Clipregion" + ".shp"
point = arcpy.Point(x,y)
pointgeometry = arcpy.PointGeometry(point)
ptlist.append(pointgeometry)
arcpy.CreateFeatureclass_management("C:/Users/Eric Cawi/Documents/SAR/database_stuff/DistanceRings.gdb", "Ptfile","Point")
ptfile = "C:/Users/Eric Cawi/Documents/SAR/database_stuff/DistanceRings.gdb/"+ "Ptfile"
cursor = arcpy.da.InsertCursor( ptfile,["SHAPE@"])
cursor.insertRow(list(ptlist))
        
del cursor
arcpy.DefineProjection_management(ptfile, sr1)
arcpy.Project_management(ptfile, "C:/Users/Eric Cawi/Documents/SAR/database_stuff/DistanceRings.gdb/" + "Ptfile_Project", sr, "WGS_1984_(ITRF00)_To_NAD_1983")
arcpy.Buffer_analysis("C:/Users/Eric Cawi/Documents/SAR/database_stuff/DistanceRings.gdb/" + "Ptfile_Project" , fctemp, "12.5 Kilometers")
arcpy.FeatureEnvelopeToPolygon_management(fctemp, fcclip)#creates the box? yes this creates the box for clipping everything


for i in range(len(cat_list)):
        

        Buf_Distance = Distances[i] #this is a list of distances for the current category
        DistancePlus = list(Distances)
        val = Buf_Distance[-1]
        val = val * 2
        Buf_Distance.append(val) #adding twice the longest distance for some reason, was in original
        
        
        
        fc = fname + "DissRings" + cat_list[i] + ".shp"
       
        f_clipped = fname + "Clipped_Rings" + cat_list[i] + ".shp"
        f_clip_raster = fname +"tifs/"+ cat_list[i] + ".tif"
        f_png_db= fname + "final_pngs"
        

        
               
        arcpy.MultipleRingBuffer_analysis("C:/Users/Eric Cawi/Documents/SAR/database_stuff/DistanceRings.gdb/" + "Ptfile_Project",fc , Buf_Distance, "Miles", "", "ALL")
        #arcpy.FeatureClassToGeodatabase_conversion([fc,fcclip],"C:/SAR/DistanceModel/DistanceRings_ClipR.gdb/" )
        

fieldname = arcpy.ValidateFieldName("Descrip")
        arcpy.AddField_management(fc,fieldname,"TEXT","","",12)
        #cursor = arcpy.da.InsertCursor(fc,["Descrip"])
        cursor = arcpy.da.UpdateCursor(fc,["Descrip"])
        x = 0;
        for row in cursor:
            if x > 4:
                break;
            else:
                row[0] = str(perct[x])
                cursor.updateRow(row)
                x +=1
            #cursor.insertRow([perct[x]])
        #add fields for area and density and calculate those fields with the goal of getting probability density for each thingy
        arcpy.AddField_management(fc, "Percent", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(fc, "Percent", "CalcPercent (!Descrip!)", "PYTHON_9.3", "def CalcPercent( Descrip):\\n if Descrip in ['25%','50%','75%']:\\n return 25\\n elif Descrip == '95%':\\n return 20\\n else:\\n return 5")
        arcpy.AddField_management(fc, "PolyArea", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(fc, "PolyArea", "!shape.area@SQUAREMILES!", "PYTHON_9.3", "")
        arcpy.AddField_management(fc, "Pden", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(fc, "Pden", "(!Percent!/!PolyArea!)/100", "PYTHON_9.3", "")
        #our box is standard 25 km always and want a 5001x5001 pixel png to input so i clip the dataset based on the box - not all of the probability is necessarily contained in this box
        arcpy.Clip_analysis(fc, fcclip, f_clipped)
        #now I convert to a raster, theoretically with cell size 5 m
        arcpy.FeatureToRaster_conversion(f_clipped, "Pden", f_clip_raster, 5) # this works, creates raster with percentage values
        #arcpy.RasterToOtherFormat_conversion(f_clip_raster, fname, "PNG") # don't know if this will be in le greyscale
        arcpy.FeatureClassToGeodatabase_conversion(fc,"C:/Users/Eric Cawi/Documents/SAR/database_stuff/DistanceRings.gdb") #Storing ring sets in a database
        #once final png is obtained don't need the rest of hte guys, plus the rings are stored in a database already so they can be accessed if necessary
        arcpy.Delete_management(fc)
        arcpy.Delete_management(f_clipped)

        
#now I'm done and will write another python script based off of the original to pick a png based off of the getDistances function

#put clipping guy in geodatabase once, don't need to every iteration since I'm just using one base point
arcpy.FeatureClassToGeodatabase_conversion(fcclip, "C:/Users/Eric Cawi/Documents/SAR/database_stuff/DistanceRings.gdb")
arcpy.Delete_management(fctemp)
exit;

    Status
    API
    Training
    Shop
    Blog
    About

    © 2014 GitHub, Inc.
    Terms
    Privacy
    Security
    Contact

