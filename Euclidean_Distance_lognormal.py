import os
import sys
import arcpy
from arcpy.sa import *
import math #want the math library for the 

inws = arcpy.GetParameterAsText(0)
arcpy.env.workspace = inws

opws = arcpy.GetParameterAsText(1)
arcpy.env.outworkspace = opws

arcpy.env.overwriteOutput = True

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
mean_list = []
std_dev_list = [] # need values for normal distribution values
Distances = [[0.2,1.5,3,12.0],[0.4,0.9,3.7,10.4],[0.2,0.9,3.4,6.1],[0.5,1.0,3.4,6.1],\
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
def gettif(Subject_Category,EcoReg,Terrain):
    if Subject_Category == "Abduction":
        fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[0] + "lognormal_clipped"

    elif Subject_Category == "Aircraft":
        fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[1] + "lognormal_clipped"

    elif Subject_Category == "Angler":
        if EcoReg == "Temperate":
            if Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[2] + "lognormal_clipped"
            else:
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[3] + "lognormal_clipped"
        elif EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[4] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[5] + "lognormal_clipped"

    elif Subject_Category == "All Terrain Vehicle":
        fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[6] + "lognormal_clipped"

    elif Subject_Category == "Autistic":
        if EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[7] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[8] + "lognormal_clipped"

    elif Subject_Category == "Camper":
        if Terrain == "Mountainous":
            if EcoReg == "Dry":
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[9] + "lognormal_clipped"
            else:
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[10] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[11] + "lognormal_clipped"

    elif Subject_Category == "Child (1-3)":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[12] + "lognormal_clipped"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[13] + "lognormal_clipped"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[14] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[15] + "lognormal_clipped"

    elif Subject_Category == "Child (4-6)":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[16] + "lognormal_clipped"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[17] + "lognormal_clipped"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[18] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[19] + "lognormal_clipped"

    elif Subject_Category == "Child (7-9)":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[20] + "lognormal_clipped"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[21] + "lognormal_clipped"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[22] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[23] + ".lognormal_clipped"

    elif Subject_Category == "Child (10-12)":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[24] + "lognormal_clipped"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[25] + "lognormal_clipped"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[26] + "lognormal_clipped"]
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[27] + "lognormal_clipped"

    elif Subject_Category == "Child (13-15)":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[28] + "lognormal_clipped"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[29] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[30] + "lognormal_clipped"

    elif Subject_Category == "Climber":
        fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[31] + "lognormal_clipped"

    elif Subject_Category == "Dementia":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[32] + "lognormal_clipped"
        elif EcoReg == "Dry" and Terrain == "Flat":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[33] + "lognormal_clipped"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[34] + "lognormal_clipped"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[35] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[36] + "lognormal_clipped"

    elif Subject_Category == "Despondent":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[37] + ".lognormal_clipped"
        elif EcoReg == "Dry" and Terrain == "Flat":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[38] + "lognormal_clipped"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[39] + "lognormal_clipped"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[40] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[41] + "lognormal_clipped"

    elif Subject_Category == "Gatherer":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[42] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[43] + "lognormal_clipped"

    elif Subject_Category == "Hiker":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[44] + "lognormal_clipped"
        elif EcoReg == "Dry" and Terrain == "Flat":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[45] + "lognormal_clipped"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[46] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[47] + "lognormal_clipped"

    elif Subject_Category == "Horseback Rider":
        fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[48] + ".lognormal_clipped"

    elif Subject_Category == "Hunter":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[49] + "lognormal_clipped"
        elif EcoReg == "Dry" and Terrain == "Flat":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[50] + "lognormal_clipped"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[51] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[52] + "lognormal_clipped"

    elif Subject_Category == "Mental Illness":
        if EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[53] + "lognormal_clipped"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[54] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[55] + "lognormal_clipped"

    elif Subject_Category == "Mental Retardation":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[56] + "lognormal_clipped"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[57] + "lognormal_clipped"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[58] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[59] + "lognormal_clipped"

    elif Subject_Category == "Mountain Biker":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[60] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[61] + "lognormal_clipped"

    elif Subject_Category == "Other (Extreme Sport)":
        fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[62] + "lognormal_clipped"

    elif Subject_Category == "Runner":
        fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[63] + "lognormal_clipped"

    elif Subject_Category == "Skier-Alpine":
        fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[64] + "lognormal_clipped"

    elif Subject_Category == "Skier-Nordic":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[65] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[66] + "lognormal_clipped"

    elif Subject_Category == "Snowboarder":
        fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[67] + "lognormal_clipped"

    elif Subject_Category == "Snowmobiler":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[68] + "lognormal_clipped"
        elif EcoReg == "Temperate" and Terrain == "Flat":
                fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[69] + "lognormal_clipped"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[70] + "lognormal_clipped"

    elif Subject_Category == "Substance Abuse":
        fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[71] + "lognormal_clipped"

    else:
        fname = "C:/Users/Eric Cawi/Documents/SAR/clipped_lognormals/" + cat_list[72] + "lognormal_clipped"

    return Distances
fctable = 'lostperson'

sr = arcpy.SpatialReference("C:/Users/Eric Cawi/Documents/SAR/database_stuff/prjfile.prj")

sr1 = arcpy.SpatialReference("WGS 1984")

#spatialref = arcpy.SpatialReference(prjFile)

#I only really need one point of reference to create a bunch of different rings around
x = 34.434933
y = -110.232333
fname= "C:/Users/Eric Cawi/Documents/SAR/"
fctemp = fname  + "b25temp" + ".shp"
fcclip = fname + "Clipregion" + ".shp"
point = arcpy.Point(x,y)
pointgeometry = arcpy.PointGeometry(point)
ptlist.append(pointgeometry)
arcpy.CreateFeatureclass_management("C:/Users/Eric Cawi/Documents/SAR/database_stuff/DistanceRings.gdb", "Ptfile","Point")
ptfile = "C:/Users/Eric Cawi/Documents/SAR/database_stuff/DistanceRings.gdb/"+  "Ptfile" 
cursor = arcpy.da.InsertCursor( ptfile,["SHAPE@"])
cursor.insertRow(list(ptlist))
        
del cursor
arcpy.DefineProjection_management(ptfile, sr1)
arcpy.Project_management(ptfile, "C:/Users/Eric Cawi/Documents/SAR/database_stuff/DistanceRings.gdb/" + "Ptfile_Project", sr, "WGS_1984_(ITRF00)_To_NAD_1983")  
arcpy.Buffer_analysis("C:/Users/Eric Cawi/Documents/SAR/database_stuff/DistanceRings.gdb/" + "Ptfile_Project" , fctemp, "12.5 Kilometers")
arcpy.FeatureEnvelopeToPolygon_management(fctemp, fcclip)#creates the box? yes this creates the box for clipping everything
cell_size = 5  #want a 5 meter cell size


for i in range(len(cat_list)
	Buf_Distance = Distances[i] #this is a list of distances for the current category
        max_dist = Buf_Distance[-1] # this sets the max distance for the eucdist function
        max_dist = max_dist * 2
        #want to convert the distance from miles to meters => 1.60934 km per mile * 1000 m/km
        max_dist = max_dist*1609.34 # sets a meter based max distance
        Euc_dist = EucDistance(ptfile,max_dist,cell_size)
        const = 1/(std_dev[i]*math.sqrt(2*math.pi))
        log_dist = math.log(Euc_dist)
        power = -(log_dist - mean[i])/(2*std_dev[i]*std_dev[i])
        log_normal_dist = const*math.exp(power)
        log_name = "C:\Users\Eric Cawi\Documents\SAR\Lognormals/" + cat_list[i] + "lognormal_dist"
        log_normal_dist.save(log_name) #saving the full lognormal files
        #do i need some other pdensity here?
        #clip this guy for the upload
        f_clipped = "C:\Users\Eric Cawi\Documents\SAR\clipped_lognormals/" + cat_list[i] + "lognormal_clipped"
        arcpy.arcpy.Clip_analysis(log_name, fcclip, f_clipped)
        
# now go through entire list of points to get the files in the right named format        
cursor = arcpy.da.SearchCursor(fctable, ["Name","State",
        "Subject_Ca","EcoRegion","Terrain","lat","long_"])
for row in cursor:
       
        namelist.append(row[0]);
        stateabbrv.append(row[1]);
        subject_category.append(row[2]);
        ecoregion_domain.append(row[3]);
        terrain.append(row[4]);
        lat_.append(row[5]);
        long_.append(row[6]);

ptList = zip(long_,lat_)

for value in range(len(stateabbrv)):
        nameval = namelist[value];
        list(nameval)
        for val in nameval:
            if (val >='0' and val <= '9'):
                keystr = keystr + val     
                   
        keyval = keystr;
        totname = stateabbrv[value] + keyval
        key.append(totname);
        keystr = ''        
        
for i in range(len(key)):
        
        sc = subject_category[i]
        ecoreg = ecoregion_domain[i]
        terr = terrain[i]
        fname = getlognormals(sc,ecoreg,terr)#gets the appropriate distance tif for each point in the pointlist
        point_name = "C:\Users\Eric Cawi\Documents\SAR\test_cases_2\DistanceLogNormal_" + key[i]+".tif" # the proper format for the thingy
        arcpy.CopyFeatures_management(fname,point_name) #copies the file raster to a raster with the proper format for file upload

exit;
