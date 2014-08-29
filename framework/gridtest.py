# Grid Test code extracted from Models.py
# We have disabled grid tests for now, maybe forever.
# Really needs to be refactored.

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


        self.gridfresh = 0
        self.Validated = False
        self.generate_testpoints()
        
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
        self.Lon6 = ''
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

    
    
    
##################################################
# From Views.py active_test()

        # If you have not passed  or conducted current test
    if int(active_test.nav) == 0:
        active_test = request.session['active_test']
        active_case = active_test.test_case
        pt1 = '(' + str(active_test.Lat1) + ',' + str(active_test.Lon1) +')'
        pt2 = '(' + str(active_test.Lat2 )+ ',' + str(active_test.Lon2)+ ')'
        pt3 = '(' + str(active_test.Lat3 )+ ',' + str(active_test.Lon3)+ ')'
        pt4 = '(' + str(active_test.Lat4 )+ ',' + str(active_test.Lon4)+ ')'
        pt5 = '(' + str(active_test.Lat5 )+ ',' + str(active_test.Lon5)+ ')'
        pt6 = '(' + str(active_test.Lat6 )+ ',' + str(active_test.Lon6)+ ')'
        pt7 = '(' + str(active_test.Lat7 )+ ',' + str(active_test.Lon7)+ ')'
        pt8 = '(' + str(active_test.Lat8 )+ ',' + str(active_test.Lon8)+ ')'
        pt9 = '(' + str(active_test.Lat9 )+ ',' + str(active_test.Lon9)+ ')'

        url = active_test.test_url
        LKP = '('+active_case.lastlat + ',' +active_case.lastlon + ')'
        totalcells = active_case.totalcellnumber
        sidecells = active_case.sidecellnumber
        uplat = active_case.upright_lat
        rightlon = active_case.upright_lon
        downlat = active_case.downright_lat
        leftlon = active_case.upleft_lon

        inputdic = {'pt1':pt1,'pt2':pt2,'pt3':pt3,'pt4':pt4,'pt5':pt5,'pt6':pt6,'pt7':pt7,'pt8':pt8,'pt9':pt9,'pic':url,'LKP':LKP,'totalcells':totalcells,'sidecells':sidecells,'uplat':uplat,'rightlon':rightlon,'downlat':downlat,'leftlon':leftlon}
        inputdic['rand'] = str(random.randint(1,1000000000000))
        return render_to_response('grid_intest.html',inputdic)

    # If you have failed current test
    elif int(active_test.nav) == 1:
        time.sleep(1)
        return redirect('/grid_testresult/')


    # If you passed your test
    elif int(active_test.nav) == 2 and request.session['active_test'].Validated == True:



######################################
# Stuff from Views.py
######################################

#---------------------------------------------------------------
# grid_test_result: surely this can be done in about 2 dozen lines?

def grid_test_result(request):

    AUTHENTICATE()

    active_test = request.session['active_test']
    active_case = active_test.test_case

    # If test already run; not regenerated

    if int(active_test.nav) == 1:
        pt1x = active_test.usr_p1x
        pt1y = active_test.usr_p1y
        pt2x = active_test.usr_p2x
        pt2y = active_test.usr_p2y
        pt3x = active_test.usr_p3x
        pt3y = active_test.usr_p3y
        pt4x = active_test.usr_p4x
        pt4y = active_test.usr_p4y
        pt5x = active_test.usr_p5x
        pt5y = active_test.usr_p5y
        pt6x = active_test.usr_p6x
        pt6y = active_test.usr_p6y
        pt7x = active_test.usr_p7x
        pt7y = active_test.usr_p7y
        pt8x = active_test.usr_p8x
        pt8y = active_test.usr_p8y
        pt9x = active_test.usr_p9x
        pt9y = active_test.usr_p9y

    # if test not already run
    else:
        # Get user input of points
        pt1x = request.GET['pt1x']
        pt1y = request.GET['pt1y']

        pt2x = request.GET['pt2x']
        pt2y = request.GET['pt2y']

        pt3x = request.GET['pt3x']
        pt3y = request.GET['pt3y']

        pt4x = request.GET['pt4x']
        pt4y = request.GET['pt4y']

        pt5x = request.GET['pt5x']
        pt5y = request.GET['pt5y']

        pt6x = request.GET['pt6x']
        pt6y = request.GET['pt6y']

        pt7x = request.GET['pt7x']
        pt7y = request.GET['pt7y']

        pt8x = request.GET['pt8x']
        pt8y = request.GET['pt8y']

        pt9x = request.GET['pt9x']
        pt9y = request.GET['pt9y']

        # run match and verify input

        pattern ='^[0-9]+$'

        count = 0

        LKP = '('+active_case.lastlat + ',' +active_case.lastlon + ')'
        totalcells = active_case.totalcellnumber
        sidecells = active_case.sidecellnumber
        uplat = active_case.upright_lat
        rightlon = active_case.upright_lon
        downlat = active_case.downright_lat
        leftlon = active_case.upleft_lon


        inputdic01 ={'pt1x_i':pt1x,'pt1y_i':pt1y,'pt2x_i':pt2x,'pt2y_i':pt2y,'pt3x_i':pt3x,'pt3y_i':pt3y,'pt4x_i':pt4x,'pt4y_i':pt4y,'pt5x_i':pt5x,'pt6x_i':pt6x,'pt6y_i':pt6y,'pt7x_i':pt7x,'pt7y_i':pt7y,'pt8x_i':pt8x,'pt8y_i':pt8y,'pt9x_i':pt9x,'pt9y_i':pt9y,'LKP':LKP,'totalcells':totalcells,'sidecells':sidecells,'uplat':uplat,'rightlon':rightlon,'downlat':downlat,'leftlon':leftlon}
        if re.match(pattern,pt1x) == None or re.match(pattern,pt1y) == None:
            inputdic01['fail1'] = True
            count = count + 1

        if re.match(pattern,pt2x) == None or re.match(pattern,pt2y) == None:
            inputdic01['fail2'] = True
            count = count + 1

        if re.match(pattern,pt3x) == None or re.match(pattern,pt3y) == None:
            inputdic01['fail3'] = True
            count = count + 1

        if re.match(pattern,pt4x) == None or re.match(pattern,pt4y) == None:
            inputdic01['fail4'] = True
            count = count + 1

        if re.match(pattern,pt5x) == None or re.match(pattern,pt5y) == None:
            inputdic01['fail5'] = True
            count = count + 1

        if re.match(pattern,pt6x) == None or re.match(pattern,pt6y) == None:
            inputdic01['fail6'] = True
            count = count + 1

        if re.match(pattern,pt7x) == None or re.match(pattern,pt7y) == None:
            inputdic01['fail7'] = True
            count = count + 1

        if re.match(pattern,pt8x) == None or re.match(pattern,pt8y) == None:
            inputdic01['fail8'] = True
            count = count + 1

        if re.match(pattern,pt9x) == None or re.match(pattern,pt9y) == None:
            inputdic01['fail9'] = True
            count = count + 1

        # IF input errors, return input form to user with suggestions
        if count >0:

            pt1 = '(' + str(active_test.Lat1) + ',' + str(active_test.Lon1) +')'
            pt2 = '(' + str(active_test.Lat2 )+ ',' + str(active_test.Lon2)+ ')'
            pt3 = '(' + str(active_test.Lat3 )+ ',' + str(active_test.Lon3)+ ')'
            pt4 = '(' + str(active_test.Lat4 )+ ',' + str(active_test.Lon4)+ ')'
            pt5 = '(' + str(active_test.Lat5 )+ ',' + str(active_test.Lon5)+ ')'
            pt6 = '(' + str(active_test.Lat6 )+ ',' + str(active_test.Lon6)+ ')'
            pt7 = '(' + str(active_test.Lat7 )+ ',' + str(active_test.Lon7)+ ')'
            pt8 = '(' + str(active_test.Lat8 )+ ',' + str(active_test.Lon8)+ ')'
            pt9 = '(' + str(active_test.Lat9 )+ ',' + str(active_test.Lon9)+ ')'

            url = active_test.test_url

            inputdic01['pt1'] = pt1
            inputdic01['pt2'] = pt2
            inputdic01['pt3'] = pt3
            inputdic01['pt4'] = pt4
            inputdic01['pt5'] = pt5
            inputdic01['pt6'] = pt6
            inputdic01['pt7'] = pt7
            inputdic01['pt8'] = pt8
            inputdic01['pt9'] = pt9
            inputdic01['pic'] = url

            inputdic01['fail'] = True





            return render_to_response('grid_intest.html',inputdic01)


    #run assessment and capture result

#    result = request.session['active_test'].Assessment(pt1x,pt1y,pt2x,pt2y,pt3x,pt3y,pt4x,pt4y,pt5x,pt5y,pt6x,pt6y,pt7x,pt7y,pt8x,pt8y,pt9x,pt9y)


    #-------------------------------------------------
    #status input

    status = []
    for i in result:
        if i == True:
            status.append('Pass')
        if i == False:
            status.append('Fail')
    #-----------------------------------------------------

    #pt_sgrid coordinate

    pt_sgrid =[]
    pt_sgrid.append('(' + str(pt1x) + ',' + str(pt1y) + ')')
    pt_sgrid.append('(' + str(pt2x) + ',' + str(pt2y) + ')')
    pt_sgrid.append('(' + str(pt3x) + ',' + str(pt3y) + ')')
    pt_sgrid.append('(' + str(pt4x) + ',' + str(pt4y) + ')')
    pt_sgrid.append('(' + str(pt5x) + ',' + str(pt5y) + ')')
    pt_sgrid.append('(' + str(pt6x) + ',' + str(pt6y) + ')')
    pt_sgrid.append('(' + str(pt7x) + ',' + str(pt7y) + ')')
    pt_sgrid.append('(' + str(pt8x) + ',' + str(pt8y) + ')')
    pt_sgrid.append('(' + str(pt9x) + ',' + str(pt9y) + ')')

    #---------------------------------------------------------------
    # pt_latlon coordinates

    pt_latlon = []
    pt_latlon.append('(' + str(active_test.Lat1) + ',' + str(active_test.Lon1) + ')')
    pt_latlon.append('(' + str(active_test.Lat2) + ',' + str(active_test.Lon2 )+ ')')
    pt_latlon.append('(' + str(active_test.Lat3) + ',' + str(active_test.Lon3 )+ ')')
    pt_latlon.append('(' + str(active_test.Lat4 )+ ',' + str(active_test.Lon4 )+ ')')
    pt_latlon.append( '(' + str(active_test.Lat5 )+ ',' + str(active_test.Lon5) + ')')
    pt_latlon.append('(' + str(active_test.Lat6 )+ ',' + str(active_test.Lon6 )+ ')')
    pt_latlon.append('(' + str(active_test.Lat7 )+ ',' + str(active_test.Lon7) + ')')
    pt_latlon.append('(' + str(active_test.Lat8) + ',' + str(active_test.Lon8) + ')')
    pt_latlon.append('(' + str(active_test.Lat9) + ',' + str(active_test.Lon9) + ')')

    #--------------------------------------------------------------
    # pt_agrid

    pt_agrid = []

    pt_agrid.append('(' + str(active_test.pt1x) + ',' + str(active_test.pt1y) + ')')
    pt_agrid.append('(' + str(active_test.pt2x) + ',' + str(active_test.pt2y) + ')')
    pt_agrid.append('(' + str(active_test.pt3x) + ',' + str(active_test.pt3y) + ')')
    pt_agrid.append('(' + str(active_test.pt4x) + ',' + str(active_test.pt4y) + ')')
    pt_agrid.append('(' + str(active_test.pt5x) + ',' + str(active_test.pt5y) + ')')
    pt_agrid.append('(' + str(active_test.pt6x) + ',' + str(active_test.pt6y) + ')')
    pt_agrid.append('(' + str(active_test.pt7x) + ',' + str(active_test.pt7y) + ')')
    pt_agrid.append('(' + str(active_test.pt8x) + ',' + str(active_test.pt8y) + ')')
    pt_agrid.append('(' + str(active_test.pt9x) + ',' + str(active_test.pt9y) + ')')


    url = request.session['active_test'].test_url

    active_case = active_test.test_case

    LKP = '('+active_case.lastlat + ',' +active_case.lastlon + ')'
    totalcells = active_case.totalcellnumber
    sidecells = active_case.sidecellnumber
    uplat = active_case.upright_lat
    rightlon = active_case.upright_lon
    downlat = active_case.downright_lat
    leftlon = active_case.upleft_lon
    inputdic = {'pic':url, 'pt_agrid':pt_agrid,'status':status,'pt_latlon':pt_latlon,'pt_sgrid':pt_sgrid,'LKP':LKP,'totalcells':totalcells,'sidecells':sidecells,'uplat':uplat,'rightlon':rightlon,'downlat':downlat,'leftlon':leftlon}

    # If you passed, mark on test
    if False not in result:

        request.session['active_test'].nav = 1
        request.session['active_test'].save()

        return render_to_response('grid_affirmation_Pass.html',inputdic)

    # If you fail, progress
    else:

        request.session['active_test'].nav = 1
        request.session['active_test'].save()
        #Prevent Cached image
        inputdic['rand'] = str(random.randint(1,1000000000000))
        return render_to_response('grid_affirmation_Fail.html',inputdic)

#----------------------------------------------------------------------
def regen_test(request):
    '''Regenerate the grid test.'''

    AUTHENTICATE()

    request.session['active_test'].nav = 0
    os.remove(request.session['active_test'].test_url2)
    request.session['active_test'].generate_testpoints()
    request.session['active_test'].save()
    return redirect('/test_active/')

#----------------------------------------------------------------------
def passtest(request):

    AUTHENTICATE()

    active_test = request.session['active_test']
    request.session['active_test'].Validated = True
    request.session['active_test'].nav = 2
    request.session['active_test'].save()
    os.remove(request.session['active_test'].test_url2)

    request.session['active_test'].show_instructions = True
    request.session['active_test'].save()

    request.session['active_model'].gridvalidated = True
    request.session['active_model'].save()
    return redirect('/test_instructions/')

#-------------------------------------------------------------------------

def Bulkin(request):
    '''Get all gridtest coordinates at once.'''

    AUTHENTICATE()

    active_test = request.session['active_test']
    inall = request.GET['Bulkin']
    stringlst = request.GET['Bulkin'].split()
    active_case = active_test.test_case

    # Verify input
    pattern ='^[0-9]+$'

    LKP = '('+active_case.lastlat + ',' +active_case.lastlon + ')'
    totalcells = active_case.totalcellnumber
    sidecells = active_case.sidecellnumber
    upright = '('+active_case.upright_lat  + ',' +active_case.upright_lon + ')'
    downleft = '('+active_case.downleft_lat     + ',' +active_case.downleft_lon + ')'
    downright = '('+active_case.downright_lat  + ',' +active_case.downright_lon + ')'
    upleft = '('+active_case.upleft_lat  + ',' +active_case.upleft_lon + ')'


    inputdic01 ={'inall':inall,'LKP':LKP,'totalcells':totalcells,'sidecells':sidecells,'upright':upright,'downleft':downleft,'downright':downright,'upleft':upleft}

    count01 = 0
    if len(stringlst) > 18:
        count01 = count01 + 1
        inputdic01['fail_10'] = True


    if len(stringlst) < 18:
        count01 = count01 + 1
        inputdic01['fail_11'] = True

    # If length failure

    if count01 > 0:

        pt1 = '(' + str(active_test.Lat1) + ',' + str(active_test.Lon1) +')'
        pt2 = '(' + str(active_test.Lat2 )+ ',' + str(active_test.Lon2)+ ')'
        pt3 = '(' + str(active_test.Lat3 )+ ',' + str(active_test.Lon3)+ ')'
        pt4 = '(' + str(active_test.Lat4 )+ ',' + str(active_test.Lon4)+ ')'
        pt5 = '(' + str(active_test.Lat5 )+ ',' + str(active_test.Lon5)+ ')'
        pt6 = '(' + str(active_test.Lat6 )+ ',' + str(active_test.Lon6)+ ')'
        pt7 = '(' + str(active_test.Lat7 )+ ',' + str(active_test.Lon7)+ ')'
        pt8 = '(' + str(active_test.Lat8 )+ ',' + str(active_test.Lon8)+ ')'
        pt9 = '(' + str(active_test.Lat9 )+ ',' + str(active_test.Lon9)+ ')'

        url = active_test.test_url

        inputdic01['pt1'] = pt1
        inputdic01['pt2'] = pt2
        inputdic01['pt3'] = pt3
        inputdic01['pt4'] = pt4
        inputdic01['pt5'] = pt5
        inputdic01['pt6'] = pt6
        inputdic01['pt7'] = pt7
        inputdic01['pt8'] = pt8
        inputdic01['pt9'] = pt9
        inputdic01['pic'] = url

        inputdic01['fail_t'] = True

        return render_to_response('grid_intest.html',inputdic01)

    # If length proper ...test content

    active_test.usr_p1x = stringlst[0]
    active_test.usr_p1y = stringlst[1]
    active_test.usr_p2x = stringlst[2]
    active_test.usr_p2y = stringlst[3]
    active_test.usr_p3x = stringlst[4]
    active_test.usr_p3y = stringlst[5]
    active_test.usr_p4x = stringlst[6]
    active_test.usr_p4y = stringlst[7]
    active_test.usr_p5x = stringlst[8]
    active_test.usr_p5y = stringlst[9]
    active_test.usr_p6x = stringlst[10]
    active_test.usr_p6y = stringlst[11]
    active_test.usr_p7x = stringlst[12]
    active_test.usr_p7y = stringlst[13]
    active_test.usr_p8x = stringlst[14]
    active_test.usr_p8y = stringlst[15]
    active_test.usr_p9x = stringlst[16]
    active_test.usr_p9y = stringlst[17]






    count = 0
    if re.match(pattern,stringlst[0]) == None or re.match(pattern,stringlst[1]) == None :
        count = count + 1
        inputdic01['fail_1'] = True

    if re.match(pattern,stringlst[2]) == None or  re.match(pattern,stringlst[3]) == None :
        count = count + 1
        inputdic01['fail_2'] = True

    if re.match(pattern,stringlst[4]) == None or re.match(pattern,stringlst[5]) == None:
        count = count + 1
        inputdic01['fail_3'] = True

    if re.match(pattern,stringlst[6]) == None or re.match(pattern,stringlst[7]) == None :
        count = count + 1
        inputdic01['fail_4'] = True


    if re.match(pattern,stringlst[8]) == None or re.match(pattern,stringlst[9]) == None :
        count = count + 1
        inputdic01['fail_5'] = True

    if re.match(pattern,stringlst[10]) == None or  re.match(pattern,stringlst[11]) == None :
        count = count + 1
        inputdic01['fail_6'] = True

    if re.match(pattern,stringlst[12]) == None or re.match(pattern,stringlst[13]) == None:
        count = count + 1
        inputdic01['fail_7'] = True

    if re.match(pattern,stringlst[14]) == None or re.match(pattern,stringlst[15]) == None  :
        count = count + 1
        inputdic01['fail_8'] = True

    if re.match(pattern,stringlst[16]) == None or re.match(pattern,stringlst[17]) == None:
        count = count + 1
        inputdic01['fail_9'] = True





    # If failure
    if count > 0:

        pt1 = '(' + str(active_test.Lat1) + ',' + str(active_test.Lon1) +')'
        pt2 = '(' + str(active_test.Lat2 )+ ',' + str(active_test.Lon2)+ ')'
        pt3 = '(' + str(active_test.Lat3 )+ ',' + str(active_test.Lon3)+ ')'
        pt4 = '(' + str(active_test.Lat4 )+ ',' + str(active_test.Lon4)+ ')'
        pt5 = '(' + str(active_test.Lat5 )+ ',' + str(active_test.Lon5)+ ')'
        pt6 = '(' + str(active_test.Lat6 )+ ',' + str(active_test.Lon6)+ ')'
        pt7 = '(' + str(active_test.Lat7 )+ ',' + str(active_test.Lon7)+ ')'
        pt8 = '(' + str(active_test.Lat8 )+ ',' + str(active_test.Lon8)+ ')'
        pt9 = '(' + str(active_test.Lat9 )+ ',' + str(active_test.Lon9)+ ')'

        url = active_test.test_url

        inputdic01['pt1'] = pt1
        inputdic01['pt2'] = pt2
        inputdic01['pt3'] = pt3
        inputdic01['pt4'] = pt4
        inputdic01['pt5'] = pt5
        inputdic01['pt6'] = pt6
        inputdic01['pt7'] = pt7
        inputdic01['pt8'] = pt8
        inputdic01['pt9'] = pt9
        inputdic01['pic'] = url

        inputdic01['fail_t'] = True


        return render_to_response('grid_intest.html',inputdic01)


    # If Pass
    active_test.nav = 1
    active_test.save()

    return redirect('/grid_testresult/')

#---------------------------------------------------------------------------------
@login_required
def DownloadGridsync(request):

    #------------------------------------------------------------------
    # Token Verification
    
    #----------------------------------------------------------------


    active_test = request.session['active_test']

    instring =   str(active_test.Lat1) + ',' + str(active_test.Lon1) + '\r\n' + str(active_test.Lat2 )+ ',' + str(active_test.Lon2) + '\r\n'
    instring = instring  + str(active_test.Lat3 )+ ',' + str(active_test.Lon3) + '\r\n'+ str(active_test.Lat4 )+ ',' + str(active_test.Lon4) + '\r\n'
    instring = instring  + str(active_test.Lat5 )+ ',' + str(active_test.Lon5) + '\r\n' + str(active_test.Lat6 )+ ',' + str(active_test.Lon6) + '\r\n'
    instring = instring + str(active_test.Lat7 )+ ',' + str(active_test.Lon7) + '\r\n'+ str(active_test.Lat8 )+ ',' + str(active_test.Lon8)    + '\r\n'
    instring = instring + str(active_test.Lat9 )+ ',' + str(active_test.Lon9)


    #image = Image.open(NameFile)

    #wrap = FileWrapper(NameFile)

    resp = HttpResponse(content_type = 'text/plain')

    #resp['Content-Length'] = os.path.getsize(NameFile)

    resp['Content-Disposition'] = 'attachment; filename= GridSyncPts.txt'

    #image.save(resp,'png')

    resp.write(instring)


    return resp


#---------------------------------------------------------------------------------
def DownloadGridsyncsol(request):

    AUTHENTICATE()

    active_test = request.session['active_test']

    instring =   str(active_test.pt1x) + ' ' + str(active_test.pt1y) + '\r\n' + str(active_test.pt2x )+ ' ' + str(active_test.pt2y) + '\r\n'
    instring = instring  + str(active_test.pt3x )+ ' ' + str(active_test.pt3y) + '\r\n'+ str(active_test.pt4x )+ ' ' + str(active_test.pt4y) + '\r\n'
    instring = instring  + str(active_test.pt5x )+ ' ' + str(active_test.pt5y) + '\r\n' + str(active_test.pt6x )+ ' ' + str(active_test.pt6y) + '\r\n'
    instring = instring + str(active_test.pt7x )+ ' ' + str(active_test.pt7y) + '\r\n'+ str(active_test.pt8x )+ ' ' + str(active_test.pt8y)    + '\r\n'
    instring = instring + str(active_test.pt9x )+ ' ' + str(active_test.pt9y)


    #image = Image.open(NameFile)

    #wrap = FileWrapper(NameFile)

    resp = HttpResponse(content_type = 'text/plain')

    #resp['Content-Length'] = os.path.getsize(NameFile)

    resp['Content-Disposition'] = 'attachment; filename= GridSyncPts.txt'

    #image.save(resp,'png')

    resp.write(instring)


    return resp





