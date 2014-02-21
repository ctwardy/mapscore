import os
import sys
import arcpy
import shutil

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

namelist = [];
subject_category = [];
stateabbrv = [];
ecoregion_domain = [];
terrain = [];
lat_ = [];
long_ = [];
key = [];
keystr = ''
ptList = [];
pointlist = [];
pt = arcpy.Point()
ptGeoms = []
Distances = []
DistancePlus = []
perct = ['25%','50%','75%','95%','100%']

i = 0;
j = 0;
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
def gettif(Subject_Category,EcoReg,Terrain):
    if Subject_Category == "Abduction":
        fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[0] + ".tif"

    elif Subject_Category == "Aircraft":
        fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[1] + ".tif"

    elif Subject_Category == "Angler":
        if EcoReg == "Temperate":
            if Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[2] + ".tif"
            else:
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[3] + ".tif"
        elif EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[4] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[5] + ".tif"

    elif Subject_Category == "All Terrain Vehicle":
        fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[6] + ".tif"

    elif Subject_Category == "Autistic":
        if EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[7] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[8] + ".tif"

    elif Subject_Category == "Camper":
        if Terrain == "Mountainous":
            if EcoReg == "Dry":
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[9] + ".tif"
            else:
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[10] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[11] + ".tif"

    elif Subject_Category == "Child (1-3)":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[12] + ".tif"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[13] + ".tif"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[14] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[15] + ".tif"

    elif Subject_Category == "Child (4-6)":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[16] + ".tif"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[17] + ".tif"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[18] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[19] + ".tif"

    elif Subject_Category == "Child (7-9)":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[20] + ".tif"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[21] + ".tif"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[22] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[23] + ".tif"

    elif Subject_Category == "Child (10-12)":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[24] + ".tif"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[25] + ".tif"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[26] + ".tif"]
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[27] + ".tif"

    elif Subject_Category == "Child (13-15)":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[28] + ".tif"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[29] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[30] + ".tif"

    elif Subject_Category == "Climber":
        fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[31] + ".tif"

    elif Subject_Category == "Dementia":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[32] + ".tif"
        elif EcoReg == "Dry" and Terrain == "Flat":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[33] + ".tif"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[34] + ".tif"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[35] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[36] + ".tif"

    elif Subject_Category == "Despondent":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[37] + ".tif"
        elif EcoReg == "Dry" and Terrain == "Flat":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[38] + ".tif"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[39] + ".tif"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[40] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[41] + ".tif"

    elif Subject_Category == "Gatherer":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[42] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[43] + ".tif"

    elif Subject_Category == "Hiker":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[44] + ".tif"
        elif EcoReg == "Dry" and Terrain == "Flat":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[45] + ".tif"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[46] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[47] + ".tif"

    elif Subject_Category == "Horseback Rider":
        fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[48] + ".tif"

    elif Subject_Category == "Hunter":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[49] + ".tif"
        elif EcoReg == "Dry" and Terrain == "Flat":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[50] + ".tif"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[51] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[52] + ".tif"

    elif Subject_Category == "Mental Illness":
        if EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[53] + ".tif"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[54] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[55] + ".tif"

    elif Subject_Category == "Mental Retardation":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[56] + ".tif"
        elif EcoReg == "Urban":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[57] + ".tif"
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[58] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[59] + ".tif"

    elif Subject_Category == "Mountain Biker":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[60] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[61] + ".tif"

    elif Subject_Category == "Other (Extreme Sport)":
        fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[62] + ".tif"

    elif Subject_Category == "Runner":
        fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[63] + ".tif"

    elif Subject_Category == "Skier-Alpine":
        fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[64] + ".tif"

    elif Subject_Category == "Skier-Nordic":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[65] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[66] + ".tif"

    elif Subject_Category == "Snowboarder":
        fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[67] + ".tif"

    elif Subject_Category == "Snowmobiler":
        if EcoReg == "Dry":
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[68] + ".tif"
        elif EcoReg == "Temperate" and Terrain == "Flat":
                fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[69] + ".tif"
        else:
            fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[70] + ".tif"

    elif Subject_Category == "Substance Abuse":
        fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[71] + ".tif"

    else:
        fname = "C:/Users/Eric Cawi/Documents/SAR/tifs/" + cat_list[72] + ".tif"

    return Distances

fctable = 'lostperson'

sr = arcpy.SpatialReference("C:/Users/Eric Cawi/Documents/SAR/database_stuff/prjfile.prj")

sr1 = arcpy.SpatialReference("WGS 1984")

#spatialref = arcpy.SpatialReference(prjFile)
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
        fname = gettif(sc,ecoreg,terr)#gets the appropriate distance tif for each point in the pointlist
        point_name = "C:\Users\Eric Cawi\Documents\SAR\test_cases\Distance_" + key[i]+".tif" # the proper format for the thingy
        shutil.copy(fname,point_name) #arcpy copy wasn't working.  This hopefully does.

exit;


# Add a column to clipregion shapefile to keep the name of the case in its attribute table!!!