# -*- mode: python; py-indent-offset: 4 -*-
#
# MapScore Main Views File

# Import statements
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.core import exceptions
from operator import itemgetter, attrgetter
import random
import shutil
import math
import csv
import os
import string


# Import Models

from mapscore.framework.models import Account
from mapscore.framework.models import Test
from mapscore.framework.models import Case
from mapscore.framework.models import Model
from mapscore.framework.models import Model_Account_Link
from mapscore.framework.models import Test_Model_Link
from mapscore.framework.models import Mainhits
from mapscore.framework.models import terminated_accounts
import cStringIO
import time
import re
import os
#from PIL import Image
import Image
import zipfile
from django.core.servers.basehttp import FileWrapper
from django.core.context_processors import csrf

##################### Media File Locations ################################
#MEDIA_DIR = 'C:/Users/Nathan Jones/Django Website/MapRateWeb/media/'
#USER_GRAYSCALE = 'C:/Users/Nathan Jones/Django Website/MapRateWeb/user_grayscale/'
MEDIA_DIR = 'media/'         # for the server
USER_GRAYSCALE = 'user_grayscale/'



#--------------------------------------------------------------
def base_redirect(response):
    return redirect('/main/')


#--------------------------------------------------------------------------------
def AUTHENTICATE(token='usertoken'):
    '''token is either 'usertoken' or 'admintoken'
    '''
    try:
        if request.session[token] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

#-------------------------------------------------------------
def AUTHENTICATE_EITHER():
    '''Authenticates with either 'usertoken' or 'admintoken'.'''
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

#-------------------------------------------------------------------
def main_page(request):

    # record a hit on the main page
    if len(Mainhits.objects.all()) == 0:
        newhits = Mainhits()
        newhits.setup()
        newhits.save()
    mainpagehit = Mainhits.objects.all()[0]
    mainpagehit.hits = int(mainpagehit.hits) + 1
    mainpagehit.save()
    #----------------------------------------------------

    request.session['completedtest'] = ''
    request.session['completedtest_lookup'] = False
    request.session['failure'] = False
    request.session['active_case_temp'] = 'none'
    request.session['active_test'] = 'none'
    request.session['active_account'] = 'none'
    request.session['active_model'] = 'none'
    request.session['Superlogin'] = False
    request.session['userdel'] = ''
    request.session['admin_name'] = ''
    request.session['usertoken'] = False
    request.session['admintoken'] = False
    request.session['createcheck'] = False
    request.session['ActiveAdminCase'] = 'none'

    sorted_models = get_sorted_models(Model.objects.all())
    inputlist = []
    # copy values for leaderboard table
    for model in sorted_models:
        num_finished = sum((not test.Active for test in model.model_tests.all()))
        if num_finished >= 5:
            inputlist.append(
                [model.account_set.all()[0].institution_name,
                 model.model_nameID,
                 model.model_avgrating,
                 num_finished])

    # Limit to Top-10
    inputdic = {'Scorelist': inputlist[:9]}

    return render_to_response('Main.html', inputdic)


#-------------------------------------------------------------
def account_reg(request):

    return render_to_response('NewAccount.html',{})

#-------------------------------------------------------------
def create_account(request):

    # Extract form Data

    Firstname = str(request.GET['FirstName'])
    Lastname = str(request.GET['LastName'])
    Email_in = str(request.GET['Email'])
    Institution = str(request.GET['Institution'])
    Username = str(request.GET['Username'])
    Password1 = str(request.GET['Password1'])
    Password2 = str(request.GET['Password2'])
    Websitein = str(request.GET['Website'])
    #betakey = str(request.GET['Betakey'])
    captchain = str(request.GET['captcha'])

    #Verify Input

    # Beta Key ************
    actualbetakey = 'sarbayes334$$beta%Test'
    betakey = actualbetakey     # Disable betakey

    Firstname_r = r'^.+$'
    Lastname_r  = r'^.+$'
    Email_in_r  = r'^[a-zA-z0-9\.\-]+@[a-zA-z0-9\-]+[\.a-zA-z0-9\-]+$'
    Institution_r = r"^[a-zA-z\s:0-9']+$"
    Username_r = r'^[a-zA-z0-9_]+$'
    Password1_r =r'^.+$'
    Password2_r =r'^.+$'
    Websitein_r =r'.*$'
    actualcaptcha = 'H4bN'

    # Verify input
    count = 0
    inputdic = {'Firstname':Firstname,'Lastname':Lastname,'Email_in':Email_in,'Institution':Institution, 'Username':Username,'Password1':Password1,'Password2':Password2,'Websitein':Websitein}
    if re.match(Firstname_r,Firstname) == None:
        count = count + 1
        firstfail = True
        inputdic['firstfail'] = firstfail


    if re.match(Lastname_r,Lastname) == None:
        count = count + 1
        lastfail = True
        inputdic['lastfail'] = lastfail

    if re.match(Email_in_r,Email_in) == None:
        count = count + 1
        emailfail = True
        inputdic['emailfail'] = emailfail

    if re.match(Institution_r,Institution) == None:
        count = count + 1
        Institutionfail = True
        inputdic['Institutionfail'] = Institutionfail


    if re.match(Username_r,Username) == None:
        count = count + 1
        usernamefail = True
        inputdic['usernamefail'] = usernamefail

    if captchain != actualcaptcha:
        count = count + 1
        captchafail = True
        inputdic['captchafail'] = captchafail

    if betakey != actualbetakey:
        pass
        # count = count + 1
        # betafail = True
        # inputdic['betafail'] = betafail




    # For Beta Testing


    #don't allow multiple groups to have more than one username
    else:
        counter = 0
        for c in Account.objects.all():
            if Username == str(c.username):
                counter = counter + 1

        for d in terminated_accounts.objects.all():
            if Username == str(d.username):
                counter = counter + 1

        if counter >0:
            count = count + 1
            inputdic['usernamerepeat'] = True


    if re.match(Password1_r,Password1) == None:
        count = count + 1
        Pass1fail = True
        inputdic['Pass1fail'] = Pass1fail

    if re.match(Password2_r,Password2) == None:
        count = count + 1
        Pass2fail = True
        inputdic['Pass2fail'] = Pass2fail

    if re.match(Websitein_r,Websitein) == None:
        count = count + 1
        webfail =True
        inputdic['Websitein_r'] = Websitein_r

    if Password1 != Password2:
        count = count + 1
        passsyncfail = True
        inputdic['passsyncfail'] = passsyncfail

    if count >0:

        inputdic['fail'] = True
        return    render_to_response('NewAccount.html',inputdic)




    # Create User



    user = User.objects.create_user(username = Username,
                    email = Email_in,
                    password = Password1)

    user.is_active = True
    user.save()



    #Create Account

    if Websitein == '':
        Websitein = 'none'


    account = Account(institution_name = Institution,
            firstname_user = Firstname,
            lastname_user = Lastname,
            username = Username,
            password  = Password1,
            Email = Email_in,
            ID2 = Username,
            Website = Websitein,
            sessionticker = 0,
            completedtests = 0,
            deleted_models = 0,
            profpicrefresh = 0,

                )
    account.save()





    # Set up profile pic locations

    ID2 = account.ID2
    stringurl = '/media/profpic_'
    stringurl = stringurl + str(ID2)+'_'+ str(account.profpicrefresh) + '.png'
    account.photourl = stringurl


    stringlocation = 'media/profpic_' + str(ID2) + '_'+ str(account.profpicrefresh) + '.png'
    #'C:\Users\Nathan Jones\Django Website\MapRateWeb\media\profpic_' + str(ID2) + '.png'
    account.photolocation = stringlocation


    account.save()

    # set default profpic
    #shutil.copyfile('C:\Users\Nathan Jones\Django Website\MapRateWeb\in_images\Defaultprofpic.png',stringlocation)
    shutil.copyfile('in_images/Defaultprofpic.png',stringlocation)


    # Save image size parameters
    im = Image.open(account.photolocation)
    size = im.size
    xsize = size[0]
    ysize = size[1]

    account.photosizex = int(xsize)
    account.photosizey = int(ysize)
    account.save()

    request.session['active_account'] =  account
    return redirect('/uploadprofpic/')
#-------------------------------------------------------------

def account_access(request):

    request.session['createcheck'] = False
    request.session['completedtest'] = ''
    request.session['completedtest_lookup'] = False
    request.session['failure'] = False
    request.session['nav'] ='none'
    request.session['inputdic'] = 'none'
    request.session['active_case_temp'] = 'none'
    request.session['active_test'] = 'none'
    request.session['active_model'] = 'none'

    if request.session['active_account'] == 'none':

        User_in = str(request.GET['Username'])
        Pass_in = str(request.GET['Password'])

        # Verify user
        user = auth.authenticate(username = User_in , password = Pass_in)

        # User exists
        if user is not None:

            # If account deleted:
            deletedcount = 0
            for i in terminated_accounts.objects.all():
                if User_in == str(i.username):
                    deletedcount = deletedcount + 1

            if deletedcount > 0:

                return render_to_response('accountdeletedlogin.html')

            # Set user Token
            request.session['usertoken'] = True


            model_list = []
            request.session['active_account'] = Account.objects.get(ID2 = User_in)

            # record session login
            #---------------------------------------------------------------------------------
            request.session['active_account'].sessionticker = int(request.session['active_account'].sessionticker) + 1
            request.session['active_account'].save()
            #---------------------------------------------------------------------------------


            for i in request.session['active_account'].account_models.all():
                model_list.append(i.model_nameID)

            profpic = request.session['active_account'].photourl

            inputdic = {'Name':request.session['active_account'].institution_name,'modelname_list':model_list ,'profpic':profpic}

            account = request.session['active_account']

            inputdic['xsize'] = account.photosizex
            inputdic['ysize'] = account.photosizey


            return render_to_response('AccountScreen.html',inputdic)

        # User does not exist
        else:

            return render_to_response('IncorrectLogin.html',{})
    else:
        AUTHENTICATE()

        model_list = []
        for i in request.session['active_account'].account_models.all():
            model_list.append(i.model_nameID)

        profpic = request.session['active_account'].photourl

        inputdic = {'Name':request.session['active_account'].institution_name,'modelname_list':model_list,'profpic':profpic }

        account = request.session['active_account']

        inputdic['xsize'] = account.photosizex
        inputdic['ysize'] = account.photosizey


        return render_to_response('AccountScreen.html',inputdic)

#-----------------------------------------------------------------
def model_regform(request):

    AUTHENTICATE()

    return render_to_response('NewModel.html',{})

#-------------------------------------------------------------------
def PasswordReset(request):

    return render_to_response('PasswordReset.html',{})
#    -----------------------------------------------------------
def CollectingData(request):

    return render_to_response('CollectingData.html',{})
#    --------------------------------------------------------------
def email_confirmation(request):

    return render_to_response('email confirmation.html',{})
#   ----------------------------------------------------------------------
def emaillink(request):
    length = 7
    chars = string.ascii_letters + string.digits
    random.seed = (os.urandom(1024))
    print ''.join(random.choice(chars) for i in range(length))
    random.random()
    return render_to_response('emaillink.html',{})
#    ----------------------------------------------------------------------
def model_created(request):

    AUTHENTICATE()

    # if page refresh
    if request.session['createcheck'] == True:
        input_dic = {'model_name': str(request.GET['Name'])}
        return render_to_response('ModelRegComplete.html',input_dic)
    print "debug"
    # Verify Model Name

    Model_name = str(request.GET['Name'])
    description = str(request.GET['description'])
    ModelName_r = '^[a-zA-z0-9_]+$'
    baddescription = r'^\s*$'

    count = 0
    if re.match(ModelName_r,Model_name) == None:
        count = count + 1
        inputdic01 ={'namein': Model_name,'Fail':True,'description':description}

    if re.match(baddescription,description) != None:
        count = count + 1
        inputdic01 ={'namein': Model_name,'Fail1':True,'description':description}

    if count == 0:

        for k in request.session['active_account'].account_models.all():
            counter = 0
            if Model_name == str(k.model_nameID):
                counter = counter + 1

            if counter > 0:
                count = count + 1
                inputdic01 = {'namein': Model_name,'modelname': True, 'description':description}

    if count > 0:
        return render_to_response('NewModel.html',inputdic01)

    #Create new model

    new_model = Model(model_nameID = Model_name,
        ID2 = str(request.session['active_account'].ID2) + ':'+ str(Model_name),
        Description = description)

    new_model.setup()
    new_model.save()

    #Link Model to account

    Link = Model_Account_Link(    model = new_model,
                    account = request.session['active_account'])

    Link.save()

    request.session['createcheck'] = True

    request.session['model_name'] = Model_name
    request.session['model_in']=  Model_name
    request.session['active_model'] = new_model

    return redirect("/model_menu/")

#-------------------------------------------------------------------

def model_access(request):

    AUTHENTICATE()

    request.session['active_case_temp'] = 'none'
    request.session['active_test'] = 'none'
    request.session['createcheck'] = False

    # If not coming from Account
    if request.session['active_model'] != 'none':
        account_name = request.session['active_account'].institution_name
        model_name = request.session['active_model'].model_nameID
        AllTests = request.session['active_model'].model_tests.all()
        activetests = []
        for i in AllTests:
            if i.Active == True:
                activetests.append(i.test_name)

        nonactivetests = []
        for i in AllTests:
            if i.Active == False:
                nonactivetests.append(i.test_name)

        rating = request.session['active_model'].model_avgrating
        print rating
        input_dic = {'rating':rating,'Name_act':account_name, 'Name_m':model_name, 'activetest_list':activetests,'nonactivetest_list':nonactivetests}

        # If incorrect completed test entered
        if request.session['failure'] == True:
            input_dic = {'failure':True,'rating':rating,'Name_act':account_name, 'Name_m':model_name, 'activetest_list':activetests,'nonactivetest_list':nonactivetests}
            request.session['failure'] = False

        #if returning from completed selection

        if request.session['completedtest_lookup'] == True:
            input_dic['completedtest'] = request.session['completedtest']

            request.session['completedtest_lookup'] = False

        return render_to_response('ModelScreen.html',input_dic)

    # If comming frm account
    else:
        selection = request.GET['model_in']
        if selection == '0':
            return redirect('/account/')
        else:
           # request.session['active_model'] = Model.objects.get(ID2 = str(request.session['active_account'].ID2) + ':' + str(selection))

            account_name = request.session['active_account'].institution_name
            model_name = request.session['active_model'].model_nameID

            AllTests = request.session['active_model'].model_tests.all()
            activetests = []
            for i in AllTests:
                if i.Active == True:
                    activetests.append(i.test_name)


            nonactivetests = []
            for i in AllTests:
                if i.Active == False:
                    nonactivetests.append(i.test_name)

            rating = request.session['active_model'].model_avgrating
            input_dic = {'rating':rating,'Name_act':account_name, 'Name_m':model_name, 'activetest_list':activetests,'nonactivetest_list':nonactivetests}


            # If incorrect completed test entered
            if request.session['failure'] == True:

                input_dic['failure'] = True
                request.session['failure'] = False




            return render_to_response('ModelScreen.html',input_dic)

#----------------------------------------------------------------
def admin_login(request):

    request.session['Superlogin'] = False
    return render_to_response('AdminLogin.html')
#---------------------------------------------------------------

def admin_account(request):
    request.session['userdel'] = ''
    request.session['inputdic'] = 'none'

    if request.session['Superlogin'] == False:

        User_in = request.GET['Username']
        Pass_in = request.GET['Password']

        # Verify user
        user = auth.authenticate(username = User_in , password = Pass_in)

        # User exists
        if user is not None:
            if user.is_superuser == True:

                request.session['admintoken'] = True
                request.session['admin_name'] = User_in
                request.session['active_account'] ='superuser'
                request.session['Superlogin'] = True
                return render_to_response('AdminScreen.html',{})

            else:
                return render_to_response('IncorrectLogin.html',{})


        # User does not exist
        else:
            return render_to_response('IncorrectLogin.html',{})

    elif request.session['Superlogin'] == True:

        AUTHENTICATE(token='admintoken')
        request.session['active_account'] ='superuser'
        return render_to_response('AdminScreen.html',{})

#---------------------------------------------------------------------
def testcase_admin(request):

    AUTHENTICATE(token='admintoken')

    for case in Case.objects.filter(UploadedLayers = False):
        if os.path.exists(str(case.LayerField)):
            case.update(UploadedLayers = True)

    request.session['ActiveAdminCase'] = 'none'

    request.session['inputdic'] = 'none'
    caselist = []

    for i in Case.objects.all():
        inputlist = []
        inputlist.append(i.id)
        inputlist.append(i.case_name)
        inputlist.append(i.Age)
        inputlist.append(i.Sex)
        inputlist.append('(' + str(i.upright_lat  ) + ',' + str(i.upright_lon ) + ');'+'(' + str(i.downright_lat) + ',' + str(i.downright_lon ) + ');'+'(' + str(i.upleft_lat) + ',' + str(i.upleft_lon ) + ');'+'(' + str(i.downleft_lat ) + ',' + str(i.downleft_lon) + ')')
        inputlist.append('(' + str(i.findx) + ',' + str(i.findy ) + ')')
        inputlist.append(str(i.UploadedLayers))
        caselist.append(inputlist)

    return render_to_response('TestCaseMenu.html',{'case_list':caselist})

#-----------------------------------------------------------------------
def Casereg(request):

    AUTHENTICATE(token='admintoken')
    inputdic = {}
    inputdic.update(csrf(request))
    return render_to_response('Casereg.html',inputdic)


#------------------------------------------------------------------------

def newtest(request):

    AUTHENTICATE()

    # Use names requested by TestWelcome.html so we can use locals() later.
    case = request.session['active_case_temp']
    MAP = case.URL
    Name_act = request.session['active_account'].institution_name
    Name_m = request.session['active_model'].model_nameID

    age = case.Age
    name = case.case_name
    sex = case.Sex
    LKP = '('+case.lastlat + ',' +case.lastlon + ')'
    subject_category = case.subject_category
    subject_subcategory = case.subject_subcategory
    scenario   =  case.scenario
    subject_activity  = case.subject_activity
    number_lost  = case.number_lost
    group_type = case.group_type
    ecoregion_domain  = case.ecoregion_domain
    ecoregion_division = case.ecoregion_division
    terrain     = case.terrain
    total_hours = case.total_hours

    totcells = int(float(case.totalcellnumber))
    horcells = vercells = case.sidecellnumber
    cellwidth = 5 # meters
    regionwidth = 25 # km
    uplat = case.upright_lat
    rightlon = case.upright_lon
    downlat = case.downright_lat
    leftlon = case.upleft_lon

    # That's a lot of variables. We'll use the 'locals()' trick
    # instead of creating an input dictionary.

    return render_to_response('TestWelcome.html', locals())

#------------------------------------------------------------------------------------------
def create_test(request):
    AUTHENTICATE()

    # If refresh
    if request.session['createcheck'] == True:
        return redirect('/test_instructions/')

    #Old code had notification page.Clunky.
    #return render_to_response('TestCreated.html')

    tempcase = request.session['active_case_temp']
    newtest = Test( test_case = tempcase,
        test_name = tempcase.case_name,
        ID2 = str(request.session['active_model'].ID2) + ':' +str(tempcase.case_name) )

    newtest.save()

    Link = Test_Model_Link( test = newtest,
                model = request.session['active_model'])

    Link.save()
    newtest.setup()
    newtest.save()
    request.session['active_test'] = newtest
    request.session['createcheck'] = True
    return render_to_response('TestCreated.html')

#-------------------------------------------------------------------
def setactive_test(request):

    AUTHENTICATE()

    intest = request.GET['test_in_active']
    print intest
    if intest == '0':
        return redirect('/model_menu/')

    else:
        testname = str(request.session['active_model'].ID2) + ':' + str(intest)
        try:
            request.session['active_test'] = Test.objects.get(ID2 = testname)
            return redirect('/test_instructions/')
        except Test.MultipleObjectsReturned:
            # Really this shouldn't be allowed to happen
            tests = Test.objects.filter(ID2 = testname)
            request.session['active_test'] = tests[0]
            return redirect('/test_instructions/')

#-------------------------------------------------------------------------------------------
def Activate_instructions(request):

    AUTHENTICATE()

    request.session['active_test'].show_instructions = True
    request.session['active_test'].save()
    return redirect('/test_instructions/')



#-------------------------------------------------------------------
def tst_instructions(request):

    AUTHENTICATE()
    if int(request.session['active_test'].nav) == 2:

        if request.session['active_test'].show_instructions == True:
            request.session['active_test'].show_instructions = False
            request.session['active_test'].save()
            return render_to_response('tst_instruct2.html')
        else:
            return redirect('/test_active/')


    else:
        if request.session['active_test'].show_instructions == True:
            request.session['active_test'].show_instructions = False
            request.session['active_test'].save()
            return render_to_response('tst_instructions.html')
        else:
            return redirect('/test_active/')

#-------------------------------------------------------------------------------------------

def active_test(request):

    AUTHENTICATE()

    #request.session['active_test'] = Test.objects.get(ID2 = request.session['active_test'].ID2)
    active_test = request.session['active_test']
    print str(active_test.nav) + '-----nav'

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

        active_test = request.session['active_test']
        active_case = active_test.test_case


        age = active_case.Age
        name = active_case.case_name
        sex = active_case.Sex
        LKP = '('+active_case.lastlat + ',' +active_case.lastlon + ')'
        totalcells = active_case.totalcellnumber
        sidecells = active_case.sidecellnumber
        uplat = active_case.upright_lat
        rightlon = active_case.upright_lon
        downlat = active_case.downright_lat
        leftlon = active_case.upleft_lon

        account_name = request.session['active_account'].institution_name
        model_name = request.session['active_model'].model_nameID
        URL = active_case.URL

        subject_category = active_case.subject_category
        subject_subcategory = active_case.subject_subcategory
        scenario   =  active_case.scenario
        subject_activity  = active_case.subject_activity
        number_lost  = active_case.number_lost
        group_type = active_case.group_type
        ecoregion_domain  = active_case.ecoregion_domain
        ecoregion_division = active_case.ecoregion_division
        terrain     = active_case.terrain
        total_hours = active_case.total_hours





    # Create Input dictionary

        inputdic = {'Name_act':account_name, 'Name_m':model_name, 'name' :name, 'age':age, 'sex':sex,'LKP':LKP,'horcells':sidecells,'vercells':sidecells,'totcells' : totalcells, 'cellwidth' : 5, 'regionwidth' : 25,'uplat':uplat,'rightlon':rightlon,'downlat':downlat,'leftlon':leftlon,'MAP':URL}
        inputdic['subject_category'] = subject_category
        inputdic['subject_subcategory'] = subject_subcategory
        inputdic['scenario'] = scenario
        inputdic['subject_activity'] = subject_activity
        inputdic['number_lost'] = number_lost
        inputdic['group_type'] = group_type
        inputdic['ecoregion_domain'] = ecoregion_domain
        inputdic['ecoregion_division'] = ecoregion_division
        inputdic['terrain'] = terrain
        inputdic['total_hours'] = total_hours
        inputdic['layer'] = active_case.UploadedLayers

        inputdic.update(csrf(request))
        return render_to_response('file_up.html',inputdic)

#---------------------------------------------------------------

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

    result = request.session['active_test'].Assessment(pt1x,pt1y,pt2x,pt2y,pt3x,pt3y,pt4x,pt4y,pt5x,pt5y,pt6x,pt6y,pt7x,pt7y,pt8x,pt8y,pt9x,pt9y)


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

    AUTHENTICATE()

    request.session['active_test'].nav = 0
    os.remove(request.session['active_test'].test_url2)
    request.session['active_test'].generate_testpoints()
    request.session['active_test'].save()
    return redirect('/test_active/')

#-------------------------------------------------------------------------

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

#------------------------------------------------------------------------
def Bulkin(request):

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

#-------------------------------------------------------------------------
# Load Image

def load_image(request):

    AUTHENTICATE()

    # increment counter
    active_test = request.session['active_test']
    grayrefresh = int(active_test.grayrefresh) + 1
    active_test.grayrefresh = grayrefresh

    string = MEDIA_DIR
    string += str(active_test.ID2).replace(':','_')
    string += '_%d.png' % grayrefresh

    # Save the greyscale file path to the test object
    active_test.greyscale_path = string
    active_test.save()


    destination = open(string,'wb+')

    for chunk in request.FILES['grayscale'].chunks():
        destination.write(chunk)
    destination.close()

    return redirect('/confirm_grayscale/')

#--------------------------------------------------------------------------
def confirm_grayscale(request):

    AUTHENTICATE()

    # Verify Image
    image_in = Image.open(request.session['active_test'].greyscale_path)
    s = str(request.session['active_test'].ID2).replace(':','_')
    served_Location = '/%s%s_%s.png' % (MEDIA_DIR, s, str(request.session['active_test'].grayrefresh))
    inputdic = {'grayscale':served_Location}

    # Check dimensions
    if image_in.size[0] != 5001 or image_in.size[1] != 5001:
        return render_to_response('uploadfail_demensions.html',inputdic)

    data = image_in.getdata()
    bands = image_in.getbands()

    if bands[:3] == 'RGB':
        # Check that it's actually RGB, not grayscale stored as RGB
        # If it's true RGB, fail.
        for i in range(len(data)):
            if not( data[i][0] == data[i][1] == data[i][2] ):
                return render_to_response('imageupload_fail.html',inputdic)
        print 'Image OK: grayscale stored as RGB.'

    # REview
    elif bands[0] in 'LP':
        print 'actual grayscale'

    # Image not grayscale
    else:
        return render_to_response('imageupload_fail.html',inputdic)


    return render_to_response('imageupload_confirm.html',inputdic)



#-----------------------------------------------------------------------------
# deny grayscale confirmation
def denygrayscale_confirm(request):

    AUTHENTICATE()

    # Remove served Grayscale image
    os.remove(request.session['active_test'].greyscale_path)

    # Wipe the path
    request.session['active_test'].greyscale_path = 'none'
    request.session['active_test'].save()

    return redirect('/test_active/')


#-----------------------------------------------------------------------------
# accept grayscale confirmation
def acceptgrayscale_confirm(request):

    AUTHENTICATE()
    # iterate counter
    request.session['active_test'].grayrefresh = int(request.session['active_test'].grayrefresh) + 1
    request.session['active_test'].save()


    s = USER_GRAYSCALE + str(request.session['active_test'].ID2).replace(':','_')
    s += '_%s.png' % str(request.session['active_test'].grayrefresh)


    # Remove served Grayscale image
    shutil.move(request.session['active_test'].greyscale_path, s)

    # set the path
    request.session['active_test'].greyscale_path = s
    request.session['active_test'].save()

    return redirect('/Rate_Test/')


#-----------------------------------------------------------------------------




def Rate(request):

    AUTHENTICATE()
    response = request.session['active_test'].rate()

    # Resync Model
    request.session['active_model'] = Model.objects.get(ID2 = request.session['active_model'].ID2)

    os.remove(request.session['active_test'].greyscale_path)


    # record rating
    #---------------------------------------------------------------
    request.session['active_account'].completedtests = int(request.session['active_account'].completedtests) + 1
    request.session['active_account'].save()
    #---------------------------------------------------------------


    return redirect('/submissionreview/')

#-----------------------------------------------------------------------------
def submissionreview(request):

    AUTHENTICATE()
    request.session['active_model'].Completed_cases = int(request.session['active_model'].Completed_cases) + 1
    request.session['active_model'].save()

    active_test = request.session['active_test']
    active_case = active_test.test_case


    age = active_case.Age
    name = active_case.case_name
    sex = active_case.Sex
    LKP = '('+active_case.lastlat + ',' +active_case.lastlon + ')'
    totalcells = active_case.totalcellnumber
    sidecells = active_case.sidecellnumber
    uplat = active_case.upright_lat
    rightlon = active_case.upright_lon
    downlat = active_case.downright_lat
    leftlon = active_case.upleft_lon

    account_name = request.session['active_account'].institution_name
    model_name = request.session['active_model'].model_nameID
    URL = active_case.URL

    subject_category = active_case.subject_category
    subject_subcategory = active_case.subject_subcategory
    scenario   =  active_case.scenario
    subject_activity  = active_case.subject_activity
    number_lost  = active_case.number_lost
    group_type = active_case.group_type
    ecoregion_domain  = active_case.ecoregion_domain
    ecoregion_division = active_case.ecoregion_division
    terrain     = active_case.terrain
    total_hours = active_case.total_hours

    findpoint = '(' + active_case.findlat  + ',' +active_case.findlon + ')'
    findgrid =  '(' + active_case.findx  + ',' +active_case.findy + ')'



    URL2 = active_case.URLfind
    rating = str(request.session['active_test'].test_rating)



    # Create Input dictionary

    inputdic = {'Name_act':account_name, 'Name_m':model_name, 'name' :name, 'age':age, 'sex':sex,'LKP':LKP,'horcells':sidecells,'vercells':sidecells,'totcells' : totalcells, 'cellwidth' : 5, 'regionwidth' : 25,'uplat':uplat,'rightlon':rightlon,'downlat':downlat,'leftlon':leftlon,'MAP':URL}
    inputdic['subject_category'] = subject_category
    inputdic['subject_subcategory'] = subject_subcategory
    inputdic['scenario'] = scenario
    inputdic['subject_activity'] = subject_activity
    inputdic['number_lost'] = number_lost
    inputdic['group_type'] = group_type
    inputdic['ecoregion_domain'] = ecoregion_domain
    inputdic['ecoregion_division'] = ecoregion_division
    inputdic['terrain'] = terrain
    inputdic['total_hours'] = total_hours
    inputdic['MAP2'] = URL2
    inputdic['find_pt'] = findpoint
    inputdic['find_grid'] = findgrid
    inputdic['rating'] = rating

    if active_case.showfind == True:
        inputdic['showfind'] = True




    request.session['active_test'].save()

    return render_to_response('Submissionreview.html',inputdic)


#------------------------------------------------------------------------------------------------
def setcompletedtest(request):

    AUTHENTICATE()
    intest_raw = str(request.GET['Nonactive_Testin'])
    intest = intest_raw.strip()
    completed_lst = []

    for i in list(request.session['active_model'].model_tests.all()):
        if i.Active == False:
            completed_lst.append(str(i.test_name))

    if intest not in completed_lst :
        request.session['failure'] = True
        return redirect('/model_menu/')

    else:
        request.session['active_test'] = request.session['active_model'].model_tests.get(test_name = intest)
        return redirect('/Nonactive_test/')

#--------------------------------------------------------------------------------------------------
def nonactivetest(request):

    AUTHENTICATE()

    active_test = request.session['active_test']
    active_case = active_test.test_case


    age = active_case.Age
    name = active_case.case_name
    sex = active_case.Sex
    LKP = '('+active_case.lastlat + ',' +active_case.lastlon + ')'
    totalcells = active_case.totalcellnumber
    sidecells = active_case.sidecellnumber
    uplat = active_case.upright_lat
    rightlon = active_case.upright_lon
    downlat = active_case.downright_lat
    leftlon = active_case.upleft_lon

    account_name = request.session['active_account'].institution_name
    model_name = request.session['active_model'].model_nameID
    URL = active_case.URL

    subject_category = active_case.subject_category
    subject_subcategory = active_case.subject_subcategory
    scenario   =  active_case.scenario
    subject_activity  = active_case.subject_activity
    number_lost  = active_case.number_lost
    group_type = active_case.group_type
    ecoregion_domain  = active_case.ecoregion_domain
    ecoregion_division = active_case.ecoregion_division
    terrain     = active_case.terrain
    total_hours = active_case.total_hours

    findpoint = '(' + active_case.findlat  + ',' +active_case.findlon + ')'
    findgrid =  '(' + active_case.findx  + ',' +active_case.findy + ')'



    URL2 = active_case.URLfind
    rating = str(request.session['active_test'].test_rating)



    # Create Input dictionary

    inputdic = {'Name_act':account_name, 'Name_m':model_name, 'name' :name, 'age':age, 'sex':sex,'LKP':LKP,'horcells':sidecells,'vercells':sidecells,'totcells' : totalcells, 'cellwidth' : 5, 'regionwidth' : 25,'uplat':uplat,'rightlon':rightlon,'downlat':downlat,'leftlon':leftlon,'MAP':URL}
    inputdic['subject_category'] = subject_category
    inputdic['subject_subcategory'] = subject_subcategory
    inputdic['scenario'] = scenario
    inputdic['subject_activity'] = subject_activity
    inputdic['number_lost'] = number_lost
    inputdic['group_type'] = group_type
    inputdic['ecoregion_domain'] = ecoregion_domain
    inputdic['ecoregion_division'] = ecoregion_division
    inputdic['terrain'] = terrain
    inputdic['total_hours'] = total_hours
    inputdic['MAP2'] = URL2
    inputdic['find_pt'] = findpoint
    inputdic['find_grid'] = findgrid
    inputdic['rating'] = rating

    if active_case.showfind == True:
        inputdic['showfind'] = True

    return render_to_response('nonactive_test.html',inputdic)

#----------------------------------------------------------------------------------------------------------------------------------------------------
def get_sorted_models(allmodels):
    '''Return list of rated models, highest-rated first.
    Uses model_avgrating attribute and operator.attrgetter method.

    '''
    rated_models = [x for x in allmodels
                    if x.model_avgrating != 'unrated']
    return sorted(rated_models,
                  key=attrgetter('model_avgrating'),
                  reverse=True)

#----------------------------------------------------------------------------------------------------------------------------------------------------
def Leader_model(request):

    AUTHENTICATE_EITHER()

    sorted_models = get_sorted_models(Model.objects.all())
    # copy values for leaderboard table
    for model in sorted_models:
        institution = str(model.account_set.all()[0].institution_name)
        username = str(model.account_set.all()[0].username)
        rating = float(model.avgrating)
        tests = model.model_tests.all()
        num_finished = sum((not test.Active for test in tests))

        # 95% Confidence Interval
        sumdevsquared, lowerbound, upperbound = 0.0, -1.0, 1.0
        if num_finished > 1:
            sumdevsquared = sum(((float(x.test_rating) - rating)**2
                                 for x in tests))
            stdev = math.sqrt(sumdevsquared / (num_finished - 1))
            halfwidth = round(1.96 * stdev / math.sqrt(num_finished), 4)
            lowerbound = max(rating - halfwidth, -1)
            upperbound = min(rating + halfwidth, 1)

        inputlist.append([institution,
                          model.model_nameID,
                          rating,
                          num_finished,
                          username,
                          lowerbound,
                          upperbound,
                          num_finished < 10])  # Bare Boolean is error-prone


    # Prepare variables to send to HTML template
    inputdic ={'Scorelist':inputlist}
    if request.session['active_account'] =='superuser':
        inputdic['superuser'] = True
    request.session['nav']    = '1'
    # Sort flags
    instname = '0'
    modelname ='0'
    avgrating ='1'
    tstcomplete ='0'
    inputdic['sortlst'] = [instname, modelname, avgrating, tstcomplete]

    request.session['inputdic'] = inputdic

    return render_to_response('Leader_Model.html', inputdic)

#----------------------------------------------------------------
def switchboard(request):

#********************************************
# Switchboard Nav values
# 1-- Model
# 2-- model -> test
# 3-- test
# 4-- scenario
# 5-- test -> scenario
# 6-- model -> scenario
# 7-- scenario -> test
#*********************************************


    AUTHENTICATE_EITHER()
    # anything to model

    if request.GET['Sort_by'] == '0':
        return redirect('/Leader_model/')

    #Model to test

    elif request.GET['Sort_by'] == '1' and (request.session['nav']    == '1' or request.session['nav'] == '6'):
        return redirect('/model_to_test_switch/')

    # model to scenario

    elif request.GET['Sort_by'] == '2' and (request.session['nav']    == '1' or request.session['nav'] == '2'):
        return redirect('/model_to_Scenario_switch/')

    #test to scenario

    elif request.GET['Sort_by'] == '2' and request.session['nav']    == '3':
        return redirect('/test_to_Scenario_switch/')

    #test bottom to test
    elif request.GET['Sort_by'] == '1' and request.session['nav']    == '5':
        return redirect('/test_to_test_switch/')

    # scenario to test
    elif request.GET['Sort_by'] == '1' and request.session['nav']    == '4':
        return redirect('/scenario_to_test_switch/')

    # scenario to scenario
    elif request.GET['Sort_by'] == '2' and request.session['nav']    == '7':
        return redirect('/scenario_to_scenario_switch/')
#-----------------------------------------------------------------
def model_to_test_switch(request):

    AUTHENTICATE_EITHER()
    request.session['nav']    = '2'
    inputdic = request.session['inputdic']

    return render_to_response('Leaderboard_testname.html',inputdic)

#--------------------------------------------------------------------------
def switchboard_totest(request):

    AUTHENTICATE_EITHER()

    casename_raw = str(request.GET['casename'])
    casename = casename_raw.replace(' ', '')
    cases = Case.objects.all()

    # check if the given casename is in the database
    active_cases = [x for x in cases if x.case_name == casename]

    if len(active_cases) == 0:
        # Entry is invalid
        inputdic = request.session['inputdic']
        if request.session['nav'] == '3':
            return render_to_response('Leaderboard_Testfail.html',inputdic)
        elif request.session['nav'] == '7':
            return render_to_response('scenario_to_testfail.html',inputdic)
        elif request.session['nav'] == '2':
            return render_to_response('Leaderboard_testname_fail.html',inputdic)
        else:
            # For now just ensure we exit this function.  TODO
            return render_to_response('Leaderboard_Testfail.html',inputdic)

    # If entry is valid
    alltests = Test.objects.all()
    matched_tests = [x for x in alltests
                     if x.test_name == casename
                     and not x.Active]
    sorted_tests = sorted(matched_tests,
                          key=attrgetter('test_rating'),
                          reverse=True)

    # copy values for leaderboard table
    for test in sorted_tests:
        inputlist.append(
            [test.model_set.all()[0].institution_name,
             test.model_set.all()[0].model_nameID,
             test.test_name,
             test.test_rating,
             test.model_set.all()[0].account_set.all()[0].username])

    inputdic ={'Scorelist':inputlist}
    inputdic['casename'] = casename_raw
    if request.session['active_account'] =='superuser':
        inputdic['superuser'] = True
    instname = '0'
    modelname ='0'
    tstname ='0'
    tstrtg ='1'
    inputdic['sortlst'] = [instname, modelname, tstname, tstrtg]
    request.session['inputdic'] = inputdic
    request.session['nav'] = '3'
    return render_to_response('Leaderboard_test.html',inputdic)



#----------------------------------------------------------------------------
def model_to_Scenario_switch(request):

    AUTHENTICATE_EITHER()

    inputdic =  request.session['inputdic']

    scenario_lst = []
    for i in Case.objects.all():
        if str(i.scenario) not in  scenario_lst:
            scenario_lst.append(str(i.scenario))

    inputdic['scenario_lst'] = scenario_lst
    request.session['nav'] = '6'
    request.session['inputdic']  = inputdic

    return render_to_response('model_to_scenario.html',inputdic)

#----------------------------------------------------------------------------
def testcaseshow(request):

    AUTHENTICATE_EITHER()

    if request.session['active_account'] =='superuser':

        AllCases =[]
        for i in list(Case.objects.all()):
            AllCases.append(str(i.case_name))

        inputdic = { 'all_lst':AllCases}

        return render_to_response('case_info_admin.html',inputdic)




    Account = request.session['active_account']

    # construct a list of completed test cases

    Completed_list = []
    for i in list(Account.account_models.all()):
        name =    'Model Name: ' + str(i.model_nameID)
        lst = []
        lst.append(name)
        for j in list(i.model_tests.all()):
            if j.Active == False:
                lst.append(str( j.test_name))

        Completed_list.append(lst)


    AllCases =[]
    for i in list(Case.objects.all()):
        AllCases.append(str(i.case_name))

    inputdic = {'completed_lst':Completed_list, 'all_lst':AllCases}

    return render_to_response('case_info.html',inputdic)

#------------------------------------------------------------------------------
def return_leader(request):

    AUTHENTICATE_EITHER()

    inputdic = request.session['inputdic']

    if request.session['nav'] == '3':
        return render_to_response('Leaderboard_test.html',inputdic)

    elif request.session['nav'] == '2':

        return render_to_response('Leaderboard_testname.html',inputdic)

    elif request.session['nav'] == '1':

        return render_to_response('Leader_Model.html',inputdic)

    elif request.session['nav'] == '4':

        return render_to_response('Leaderboard_scenario.html',inputdic)

    elif request.session['nav'] == '5':
        return render_to_response('test_to_scenario.html',inputdic)

    elif request.session['nav'] == '6':
        return render_to_response('model_to_Scenario.html',inputdic)

    elif request.session['nav'] == '7':
        return render_to_response('scenario_to_test.html',inputdic)
#------------------------------------------------------------------------------
def completedtest_info(request):

    AUTHENTICATE_EITHER()

    completed_lst = []

    for i in list(request.session['active_model'].model_tests.all()):
        if i.Active == False:
            completed_lst.append(str(i.test_name))

    inputdic ={'completed_lst': completed_lst}

    return render_to_response('completedtest_info.html',inputdic)

#-----------------------------------------------------------------------------
def case_ref(request):

    AUTHENTICATE_EITHER()

    Input = request.GET['CaseName2']

    active_case = Case.objects.get(case_name = Input)

    age = active_case.Age
    name = active_case.case_name
    sex = active_case.Sex
    LKP = '('+active_case.lastlat + ',' +active_case.lastlon + ')'
    totalcells = active_case.totalcellnumber
    sidecells = active_case.sidecellnumber
    uplat = active_case.upright_lat
    rightlon = active_case.upright_lon
    downlat = active_case.downright_lat
    leftlon = active_case.upleft_lon

    URL = active_case.URL

    subject_category = active_case.subject_category
    subject_subcategory = active_case.subject_subcategory
    scenario   =  active_case.scenario
    subject_activity  = active_case.subject_activity
    number_lost  = active_case.number_lost
    group_type = active_case.group_type
    ecoregion_domain  = active_case.ecoregion_domain
    ecoregion_division = active_case.ecoregion_division
    terrain     = active_case.terrain
    total_hours = active_case.total_hours



    # Create Input dictionary

    inputdic = { 'name' :name, 'age':age, 'sex':sex,'LKP':LKP,'horcells':sidecells,'vercells':sidecells,'totcells' : totalcells, 'cellwidth' : 5, 'regionwidth' : 25,'uplat':uplat,'rightlon':rightlon,'downlat':downlat,'leftlon':leftlon,'MAP':URL}
    inputdic['subject_category'] = subject_category
    inputdic['subject_subcategory'] = subject_subcategory
    inputdic['scenario'] = scenario
    inputdic['subject_activity'] = subject_activity
    inputdic['number_lost'] = number_lost
    inputdic['group_type'] = group_type
    inputdic['ecoregion_domain'] = ecoregion_domain
    inputdic['ecoregion_division'] = ecoregion_division
    inputdic['terrain'] = terrain
    inputdic['total_hours'] = total_hours



    return render_to_response('case_ref.html',inputdic)

#------------------------------------------------------------------------------------
def caseref_return(request):

    AUTHENTICATE_EITHER()

    inputdic = request.session['inputdic']

    if request.session['nav'] == '3':
        return render_to_response('Leaderboard_test.html',inputdic)

    elif request.session['nav'] == '2':

        return render_to_response('Leaderboard_testname.html',inputdic)

    elif request.session['nav'] == '1':

        return render_to_response('Leader_Model.html',inputdic)

    elif request.session['nav'] == '4':

        return render_to_response('Leaderboard_scenario.html',inputdic)

    elif request.session['nav'] == '5':
        return render_to_response('test_to_scenario.html',inputdic)

    elif request.session['nav'] == '6':
        return render_to_response('model_to_Scenario.html',inputdic)

    elif request.session['nav'] == '7':
        return render_to_response('scenario_to_test.html',inputdic)
#----------------------------------------------------------------------------------

def Account_Profile(request):

    AUTHENTICATE_EITHER()

    Account_in = request.GET['Account']

    Active_account = Account.objects.get(username = Account_in)

    Name = str(Active_account.institution_name)
    Email = str(Active_account.Email)
    RegisteredUser = str(Active_account.firstname_user) + ' ' + str(Active_account.lastname_user)
    website = str(Active_account.Website)
    profpic = str(Active_account.photourl)

    inputdic = {'Name':Name, 'Email':Email, 'RegisteredUser':RegisteredUser, 'website':website,'profpic':profpic}

    if website !='none':
        inputdic['websitexists'] = True

    inputdic['xsize'] = int(Active_account.photosizex)
    inputdic['ysize'] = int(Active_account.photosizey)

    # get model descriptions

    modellst = []
    for i in Active_account.account_models.all():
        templst = []
        templst.append(i.model_nameID)
        templst.append(i.Description)
        templst.append(Account_in)
        modellst.append(templst)

    inputdic['modellst'] = modellst
    return render_to_response('Account_Profile.html',inputdic)
#---------------------------------------------------------------------------------
def returnfrom_profile(request):

    AUTHENTICATE_EITHER()

    inputdic = request.session['inputdic']

    if request.session['nav'] == '3':
        return render_to_response('Leaderboard_test.html',inputdic)

    elif request.session['nav'] == '2':

        return render_to_response('Leaderboard_testname.html',inputdic)

    elif request.session['nav'] == '1':

        return render_to_response('Leader_Model.html',inputdic)

    elif request.session['nav'] == '4':

        return render_to_response('Leaderboard_scenario.html',inputdic)

    elif request.session['nav'] == '5':
        return render_to_response('test_to_scenario.html',inputdic)

    elif request.session['nav'] == '6':
        return render_to_response('model_to_Scenario.html',inputdic)

    elif request.session['nav'] == '7':
        return render_to_response('scenario_to_test.html',inputdic)

#-------------------------------------------------------------------------------------
def completedtest_modellink(request):


    AUTHENTICATE_EITHER()

    completedtest = str(request.GET['completedtest'])
    request.session['completedtest'] = completedtest
    request.session['completedtest_lookup'] = True
    return redirect('/model_menu/')


#----------------------------------------------------------------------------------
def case_hyperin(request):

    AUTHENTICATE_EITHER()
    inputdic = request.session['inputdic']


    caseselection = str(request.GET['casein'])



    if request.session['nav'] == '2':
        inputdic['caseselection'] = caseselection
        return render_to_response('Leaderboard_testname.html',inputdic)

    if request.session['nav'] == '3':
        inputdic['caseselection'] = caseselection
        return render_to_response('Leaderboard_test.html',inputdic)

    if request.session['nav'] == '7':
        inputdic['caseselection'] = caseselection
        return render_to_response('scenario_to_test.html',inputdic)
#------------------------------------------------------------------------------------

def upload_casefile(request):

    AUTHENTICATE('admintoken')
    # Take in file - save to server
    #string = 'C:\Users\Nathan Jones\Django Website\MapRateWeb\case_in\input_unsorted.txt'
    string = 'case_in/input_unsorted.csv'
    destination = open(string,'wb+')

    for chunk in request.FILES['casecsv'].chunks():
        destination.write(chunk)
    destination.close()

    # Filter input file
    filea = open(string,'rb')
    csvreader = csv.reader(filea,delimiter = '|')
    masterlist = []

    # Write new CSV String, add to masterlist
    counttotal = 0
    for csvlist in csvreader:
        count = 0
        csvstring = ""

        if counttotal > 0:

            for i in csvlist:


                count = count + 1

                if count == len(csvlist):

                    csvstring = csvstring + i + "$"

                else:
                    csvstring = csvstring + i + "|"

            masterlist.append(csvstring)

        counttotal = counttotal + 1

    filea.close()

    input1 = str(masterlist)

    print "\n\n------------------------------------------------------------\n\n"
    print masterlist

    input1 = input1[2:len(input1)-2]


    newstring = ''
    store = None
    store1 = None
    store2 = None
    store3 = None
    for n in input1:

        if store != None and (n =='t' or n =='n'):
            store = None

        elif store1 != None and n == ',':
            store2 = store1 + n
            store1 = None

        elif store2 != None and n == ' ':
            store3 = store2 + n
            store2 = None
        elif store3 != None and (n == "'" or n == '"' ):
            store3 = None
            newstring = newstring + ' '


        else:
            if store != None:
                newstring = newstring + str(store)
                store = None

            if store1 != None:
                newstring = newstring + str(store1)
                store1 = None

            if store2 != None:
                newstring = newstring + str(store2)
                store2 = None

            if store3 != None:
                newstring = newstring + str(store3)
                store3 = None

            if n == '$':
                newstring = newstring +'\n'

            elif n == "\\":
                store = '\\'

            elif n == "'" or n=='"':
                store1 = n

            else:
                newstring = newstring + n



    # get rid of " characters (of no use)
    finalstring = ''
    for g in newstring:
        g = str(g)
        if g != '"':
            finalstring = finalstring + g



    # Save filtered file
    sortedaddress = 'case_in/input_srt.txt'
    file2 = open(sortedaddress,'wb+')

    file2.write(finalstring)
    file2.close()


    filein = open(sortedaddress,'r')

    line = filein.readline()
    #remove whitespace
    pattern = r'^\s*(.*)\s*$'


    while line != '':
        items = ''

        #Accounting for server adding \r after \n
        if line[0] =='\\' and line[1] == 'r':
            line = line[2:]

        if line == '':

            break

        items = line.split('|')



        name = str(re.match(pattern,items[0]).group(1))
        key = str(re.match(pattern,items[1]).group(1))

        country1 = str(re.match(pattern,items[2]).group(1))
        state1 =  str(re.match(pattern,items[3]).group(1))
        county1 = str(re.match(pattern,items[4]).group(1))
        populationdensity1 = str(re.match(pattern,items[5]).group(1))
        weather1 = str(re.match(pattern,items[6]).group(1))

        subject_category = str(re.match(pattern,items[7]).group(1))
        subject_subcategory = str(re.match(pattern,items[8]).group(1))
        scenario = str(re.match(pattern,items[9]).group(1))
        subject_activity = str(re.match(pattern,items[10]).group(1))
        age = str(re.match(pattern,items[11]).group(1))
        sex = str(re.match(pattern,items[12]).group(1))
        number_lost = str(re.match(pattern,items[13]).group(1))
        group_type = str(re.match(pattern,items[14]).group(1))
        ecoregion_Domain = str(re.match(pattern,items[15]).group(1))
        ecoregion_Division = str(re.match(pattern,items[16]).group(1))
        terrain = str(re.match(pattern,items[17]).group(1))
        LKP_lat = str(re.match(pattern,items[18]).group(1))
        LKP_lon = str(re.match(pattern,items[19]).group(1))
        find_lat = str(re.match(pattern,items[20]).group(1))
        find_lon = str(re.match(pattern,items[21]).group(1))
        total_hours = str(re.match(pattern,items[22]).group(1))
        notify_hours = str(re.match(pattern,items[23]).group(1))
        search_hours = str(re.match(pattern,items[24]).group(1))
        comments = str(re.match(pattern,items[25]).group(1))


        New_Case = Case(

            lastlat = LKP_lat,
            lastlon = LKP_lon,
            findlat = find_lat,
            findlon = find_lon,
            case_name = name,
            Age = age,
            Sex = sex,
            key = key,
            subject_category = subject_category,
            subject_subcategory = subject_subcategory,
            scenario  = scenario,
            subject_activity = subject_activity,
            number_lost = number_lost,
            group_type = group_type,
            ecoregion_domain = ecoregion_Domain,
            ecoregion_division = ecoregion_Division,
            terrain = terrain,
            total_hours = total_hours,
            notify_hours = notify_hours,
            search_hours = search_hours,
            comments = comments,
            country = country1,
            state =     state1,
            county = county1,
            populationdensity = populationdensity1,
            weather = weather1,




            )
        New_Case.save()
        New_Case.initialize()

        # Only save if find location in bounds
        if New_Case.findx == "Out of Bounds" or New_Case.findy == "Out of Bounds":

            New_Case.delete()
        else:
            New_Case.save()

        line = filein.readline()

    filein.close()
    os.remove(string)
    os.remove(sortedaddress)

    for case in Case.objects.all():

        case.UploadedLayers = False
        case.save()

        if os.path.exists(str(case.LayerField)):
            case.UploadedLayers = True
            case.save()




    return render_to_response('bulkcasereg_complete.html')


#-------------------------------------------------------------------------------
def exportcaselibrary(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------


    #string = 'C:\Users\Nathan Jones\Django Website\MapRateWeb\case_in\exported_case_Library.txt'
    string = 'case_in/exported_case_Library.csv'
    file = open(string,'wb')

    tempexport = ['Name','Key#','Subject Category','Subject Sub-Category', 'Scenario', 'Subject Activity', 'Age','Sex','Number Lost','Group Type','EcoRegion Domain','EcoRegion Division', 'Terrain','LKP Coord. (N/S)','LKP Coord. (E/W)','Find Coord. (N/S)','Fid Coord. (E/W)','Total Hours','Notify Hours','Search Hours','Comments']
    writer = csv.writer(file, delimiter = '|')

    writer.writerow(tempexport)

    for i in Case.objects.all():

        tempexport = [str(i.case_name),str(i.key),str(i.subject_category),str(i.subject_subcategory),str(i.scenario),str(i.subject_activity),str(i.Age),str(i.Sex),str(i.number_lost),str(i.group_type),str(i.ecoregion_domain),str(i.ecoregion_division),str(i.terrain),str(i.lastlat),str(i.lastlon),str(i.findlat),str(i.findlon),str(i.total_hours),str(i.notify_hours),str(i.search_hours),str(i.comments)]
        writer.writerow(tempexport)


    file.close

    return render_to_response('casexport_complete.html')

#--------------------------------------------------------------------------------------
def Manage_Account(request):

    AUTHENTICATE()
    request.session['active_model'] = 'none'

    return render_to_response('Account_manage.html')

#-----------------------------------------------------------------------------------------
def edit_user(request):

    AUTHENTICATE()

    Account = request.session['active_account']

    Firstname_in = str(Account.firstname_user)
    Lastname_in = str(Account.lastname_user)
    Email_in = str(Account.Email)

    inputdic ={'Firstname_in':Firstname_in,'Lastname_in':Lastname_in,'Email_in':Email_in}

    return render_to_response('account_useredit.html',inputdic)

#-------------------------------------------------------------------------------------------
def edit_user_run(request):

    AUTHENTICATE()

    Account = request.session['active_account']

    # read in information
    Firstname = str(request.GET['FirstName'])
    Lastname = str(request.GET['LastName'])
    Email_in = str(request.GET['Email'])
    Password = str(request.GET['Password'])
    #identify regular expressions

    Firstname_r = r'^.+$'
    Lastname_r  = r'^.+$'
    Email_in_r  = r'^[a-zA-z0-9\.\-]+@[a-zA-z0-9\-]+\.[a-zA-z0-9\-]+$'


    # Verify input
    count = 0
    count2 = 0
    inputdic = {'Firstname':Firstname,'Lastname':Lastname,'Email_in':Email_in}
    if re.match(Firstname_r,Firstname) == None:
        count = count + 1
        firstfail = True
        inputdic['firstfail'] = firstfail


    if re.match(Lastname_r,Lastname) == None:
        count = count + 1
        lastfail = True
        inputdic['lastfail'] = lastfail

    if re.match(Email_in_r,Email_in) == None:
        count = count + 1
        emailfail = True
        inputdic['emailfail'] = emailfail

    if Password != str(Account.password):
        count2 = 1
        passfail = True
        inputdic['passfail'] = True

    if count >0:

        inputdic['fail'] = True
        return    render_to_response('account_useredit.html',inputdic)


    if count2 == 1:

        inputdic['fail2'] = True
        return    render_to_response('account_useredit.html',inputdic)


    # Update Account

    Account.firstname_user = Firstname
    Account.lastname_user = Lastname
    Account.Email = Email_in
    Account.save()

    return    render_to_response('account_update_complete.html')


#----------------------------------------------------------------------------------------
def edit_inst(request):

    AUTHENTICATE()

    Account = request.session['active_account']

    Institution_in = str(Account.institution_name)
    Websitein_in = str(Account.Website)


    inputdic ={'Institution_in':Institution_in,'Websitein_in':Websitein_in}

    return render_to_response('account_editinstitution.html',inputdic)
#----------------------------------------------------------------------------------------
def edit_inst_run(request):

    AUTHENTICATE()

    Account = request.session['active_account']

    # read in information
    Institution = str(request.GET['Institution'])
    Website = str(request.GET['Website'])
    Password = str(request.GET['Password'])

    #identify regular expressions

    Institution_r = r"^[a-zA-z\s:0-9']+$"
    Websitein_r =r'.*$'

    # Verify input
    count = 0
    count2 = 0
    inputdic = {'Institution':Institution,'Websitein':Website}

    # Match regular expressions --- Perform verification

    if re.match(Institution_r,Institution) == None:
        count = count + 1
        Institutionfail = True
        inputdic['Institutionfail'] = Institutionfail


    if re.match(Websitein_r,Website) == None:
        count = count + 1
        webfail =True
        inputdic['Websitein_r'] = Websitein_r


    if Password != str(Account.password):
        count2 = 1
        passfail = True
        inputdic['passfail'] = True

    if count >0:

        inputdic['fail'] = True
        return    render_to_response('account_editinstitution.html',inputdic)


    if count2 == 1:

        inputdic['fail2'] = True
        return    render_to_response('account_editinstitution.html',inputdic)


    # Update Account

    if Website == '':
        Website = 'none'

    Account.institution_name = Institution
    Account.Website = Website

    Account.save()

    return    render_to_response('account_update_complete.html')


#-------------------------------------------------------------------

def edit_pw(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    return render_to_response('account_editpw.html')

#-------------------------------------------------------------------

def edit_pw_run(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    Account = request.session['active_account']

    # read in information
    Password1 = str(request.GET['Password1'])
    Password2 = str(request.GET['Password2'])
    Password = str(request.GET['Password'])

    #identify regular expressions

    Password1_r ='^.+$'
    Password2_r ='^.+$'

    # Verify input
    count = 0
    count2 = 0
    inputdic = {'Password1':Password1,'Password2':Password2}

    # Match regular expressions --- Perform verification

    if re.match(Password1_r,Password1) == None:
        count = count + 1
        Pass1fail = True
        inputdic['Pass1fail'] = Pass1fail

    if re.match(Password2_r,Password2) == None:
        count = count + 1
        Pass2fail = True
        inputdic['Pass2fail'] = Pass2fail

    if Password != str(Account.password):
        count2 = 1
        passfail = True
        inputdic['passfail'] = True

    if Password2 != Password1:
        count2 = 1
        passmatchfail = True
        inputdic['passmatchfail'] = passmatchfail

    if count >0:

        inputdic['fail'] = True
        return    render_to_response('account_editpw.html',inputdic)


    if count2 == 1:

        inputdic['fail2'] = True
        return    render_to_response('account_editpw.html',inputdic)


    # Update Account

    Account.password = Password1
    Account.save()

    User_in = User.objects.get(username = str(Account.username))
    User_in.set_password(Password1)
    User_in.save()

    return    render_to_response('account_update_complete.html')

#---------------------------------------------------------------------
def uploadprofpic(request):

    inputdic = {}
    inputdic.update(csrf(request))
    return    render_to_response('uploadaccountpic.html',inputdic)

#-----------------------------------------------------------------------
def accountregcomplete(request):

    return    render_to_response('RegistrationComplete.html',{})

#-----------------------------------------------------------------------
def confirm_prof_pic(request):
    account = request.session['active_account']

    os.remove(account.photolocation)

    destination = open(account.photolocation,'wb+')

    for chunk in request.FILES['profilephoto'].chunks():
        destination.write(chunk)
    destination.close()

    #------------------------------------------------------
    #resize image

    im = Image.open(account.photolocation)
    size = im.size
    xsize = size[0]
    ysize = size[1]

    if xsize > ysize:
        diffx = xsize - 350
        if diffx > 0:
            totaldiff = diffx
            xpixels = xsize - totaldiff
            percentdiff = float(xpixels)/float(xsize)
            ypixels = int(ysize * percentdiff)
            im = im.resize((xpixels,ypixels) )


    elif xsize < ysize:
        diffy = ysize - 350
        if diffy > 0:
            totaldiff = diffy
            ypixels = ysize - totaldiff
            percentdiff = float(ypixels)/float(ysize)
            xpixels = int(xsize * percentdiff)
            im = im.resize((xpixels,ypixels))

    elif xsize == ysize:

        im = im.resize((350,350))


    # Remove old picture

    os.remove(account.photolocation)

    # iterate profpic request

    account.profpicrefresh = int(account.profpicrefresh) + 1
    account.save()

    # Set up profile pic locations

    ID2 = account.ID2
    stringurl = '/media/profpic_'
    stringurl = stringurl + str(ID2)+'_'+ str(account.profpicrefresh) + '.png'
    account.photourl = stringurl


    stringlocation = 'media/profpic_' + str(ID2) + '_'+ str(account.profpicrefresh) + '.png'
    #'C:\Users\Nathan Jones\Django Website\MapRateWeb\media\profpic_' + str(ID2) + '.png'
    account.photolocation = stringlocation

    account.save()




    # Save new profpic

    im.save(str(account.photolocation))


    #-----------------------------------------------------------------------------
    inputdic = {'account_photo':account.photourl}

    # Save image size parameters
    im = Image.open(account.photolocation)
    size = im.size
    xsize = size[0]
    ysize = size[1]

    account.photosizex = int(xsize)
    account.photosizey = int(ysize)
    account.save()

    inputdic['xsize'] = account.photosizex
    inputdic['ysize'] = account.photosizey

    return    render_to_response('profpic_confirm.html',inputdic)

#-------------------------------------------------------------------------
def denyprofpic_confirm(request):
    account = request.session['active_account']

    # Remove old picture

    os.remove(account.photolocation)

    # iterate profpic request

    account.profpicrefresh = int(account.profpicrefresh) + 1
    account.save()

    # Set up profile pic locations

    ID2 = account.ID2
    stringurl = '/media/profpic_'
    stringurl = stringurl + str(ID2)+'_'+ str(account.profpicrefresh) + '.png'
    account.photourl = stringurl


    stringlocation = 'media/profpic_' + str(ID2) + '_'+ str(account.profpicrefresh) + '.png'
    #'C:\Users\Nathan Jones\Django Website\MapRateWeb\media\profpic_' + str(ID2) + '.png'
    account.photolocation = stringlocation

    account.save()



    #shutil.copyfile('C:\Users\Nathan Jones\Django Website\MapRateWeb\in_images\Defaultprofpic.png',account.photolocation)
    shutil.copyfile('in_images/Defaultprofpic.png',account.photolocation)

    # Save image size parameters
    im = Image.open(account.photolocation)
    size = im.size
    xsize = size[0]
    ysize = size[1]

    account.photosizex = int(xsize)
    account.photosizey = int(ysize)
    account.save()

    return redirect('/uploadprofpic/')

#-------------------------------------------------------------------------
def confirmprofpic_confirm(request):


    return redirect('/accountregcomplete/')

#----------------------------------------------------------------------------
def edit_picture(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    account = request.session['active_account']
    inputdic = {'account_photo':account.photourl}

    inputdic['xsize'] = account.photosizex
    inputdic['ysize'] = account.photosizey


    return    render_to_response('edit_profpic.html',inputdic)

#----------------------------------------------------------------------------
def remove_profpic(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    account = request.session['active_account']

    # Remove old picture

    os.remove(account.photolocation)


    # iterate profpic request

    account.profpicrefresh = int(account.profpicrefresh) + 1
    account.save()

    # Set up profile pic locations

    ID2 = account.ID2
    stringurl = '/media/profpic_'
    stringurl = stringurl + str(ID2)+'_'+ str(account.profpicrefresh) + '.png'
    account.photourl = stringurl


    stringlocation = 'media/profpic_' + str(ID2) + '_'+ str(account.profpicrefresh) + '.png'
    #'C:\Users\Nathan Jones\Django Website\MapRateWeb\media\profpic_' + str(ID2) + '.png'
    account.photolocation = stringlocation

    account.save()



    #shutil.copyfile('C:\Users\Nathan Jones\Django Website\MapRateWeb\in_images\Defaultprofpic.png',account.photolocation)
    shutil.copyfile('in_images/Defaultprofpic.png',account.photolocation)


    # Save image size parameters
    im = Image.open(account.photolocation)
    size = im.size
    xsize = size[0]
    ysize = size[1]

    account.photosizex = int(xsize)
    account.photosizey = int(ysize)
    account.save()

    return redirect('/edit_picture/')


#---------------------------------------------------------------------
def alterprofpic(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    inputdic = {}
    inputdic.update(csrf(request))

    return    render_to_response('change_accountpic.html',inputdic)

#-----------------------------------------------------------------------

def change_accountpic(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------


    account = request.session['active_account']

    os.remove(account.photolocation)

    destination = open(account.photolocation,'wb+')

    for chunk in request.FILES['profilephoto'].chunks():
        destination.write(chunk)
    destination.close()

    #------------------------------------------------------
    #resize image

    im = Image.open(account.photolocation)
    size = im.size
    xsize = size[0]
    ysize = size[1]

    if xsize > ysize:
        diffx = xsize - 350
        if diffx > 0:
            totaldiff = diffx
            xpixels = xsize - totaldiff
            percentdiff = float(xpixels)/float(xsize)
            ypixels = int(ysize * percentdiff)
            im = im.resize((xpixels,ypixels) )


    elif xsize < ysize:
        diffy = ysize - 350
        if diffy > 0:
            totaldiff = diffy
            ypixels = ysize - totaldiff
            percentdiff = float(ypixels)/float(ysize)
            xpixels = int(xsize * percentdiff)
            im = im.resize((xpixels,ypixels))

    elif xsize == ysize:

        im = im.resize((350,350))


    # Remove raw image

    os.remove(account.photolocation)

    # iterate profpic request

    account.profpicrefresh = int(account.profpicrefresh) + 1
    account.save()

    # Set up profile pic locations

    ID2 = account.ID2
    stringurl = '/media/profpic_'
    stringurl = stringurl + str(ID2)+'_'+ str(account.profpicrefresh) + '.png'
    account.photourl = stringurl


    stringlocation = 'media/profpic_' + str(ID2) + '_'+ str(account.profpicrefresh) + '.png'
    #'C:\Users\Nathan Jones\Django Website\MapRateWeb\media\profpic_' + str(ID2) + '.png'
    account.photolocation = stringlocation

    account.save()

    # Save image

    im.save(str(account.photolocation))

    # Save image size parameters
    im = Image.open(account.photolocation)
    size = im.size
    xsize = size[0]
    ysize = size[1]

    account.photosizex = int(xsize)
    account.photosizey = int(ysize)
    account.save()

    return redirect('/edit_picture/')
#-----------------------------------------------------------------------------
def traffic(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    mainhits = int(Mainhits.objects.all()[0].hits)

    inputlst = []
    for i in Account.objects.all():
        tmplst = []
        tmplst.append(str(i.username))
        tmplst.append(str(i.institution_name))
        tmplst.append(str(i.sessionticker))
        tmplst.append(str(len(i.account_models.all())))
        tmplst.append(str(i.deleted_models))
        tmplst.append(str(i.completedtests))
        inputlst.append(tmplst)

    deletedlst = []
    for i in terminated_accounts.objects.all():
        tmplst = []
        tmplst.append(str(i.username))
        tmplst.append(str(i.institution_name))
        tmplst.append(str(i.sessionticker))
        tmplst.append(str(i.modelsi))
        tmplst.append(str(i.deleted_models))
        tmplst.append(str(i.completedtests))

        deletedlst.append(tmplst)



    inputdic = {'mainhits':mainhits,'inputlst':inputlst,'deletedlst':deletedlst}

    return    render_to_response('traffic.html',inputdic)


#------------------------------------------------------------------------------
def delete_account(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    return    render_to_response('Deleteaccount.html')

#-------------------------------------------------------------------------------
def deleteaccount_confirm(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    password = str(request.GET['Password'])
    account =  request.session['active_account']

    # If invalid password
    if password != str(account.password):

        inputdic ={'passfail':True}
        return    render_to_response('Deleteaccount.html',inputdic)


    # If account is to be deleted
    else:
        # create new deleted object

        t = terminated_accounts()
        t.username = str(account.username)
        t.sessionticker = str(account.sessionticker)
        t.completedtests = str(account.completedtests)
        t.institution_name = str(account.institution_name)
        t.modelsi = str(len(account.account_models.all()))
        t.deleted_models = str(account.deleted_models)
        t.save()

        #Delete Tests / models

        for i in account.account_models.all():



            for j in i.model_tests.all():
                j.delete()

            # delete all model test links
            for k in Test_Model_Link.objects.all():
                if str(k.model.ID2) == str(i.ID2):
                    k.delete()

            i.delete()

         # Delete Picture
        os.remove(account.photolocation)


        #Delete model account links

        for i in Model_Account_Link.objects.all():
            if str(i.account.ID2) == str(account.ID2):
                i.delete()

        # delete account

        account.delete()

        return    render_to_response('Accountdeleted.html')

#--------------------------------------------------------------------------------
def terminate_accounts(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------


    inputdic = {}

    if str(request.session['userdel']) != '':
        username = str(request.session['userdel'])
        inputdic['accountin'] = username
        request.session['userdel'] = ''

    return    render_to_response('adminaccountermination.html',inputdic)

#--------------------------------------------------------------------------------
def view_username_admin(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    inputlist = []
    for i in Account.objects.all():
        tmplst = []
        tmplst.append(i.username)
        tmplst.append(i.institution_name)
        inputlist.append(tmplst)

    inputdic = {'inputlist':inputlist}

    return    render_to_response('account_admin_terminfo.html',inputdic)

#------------------------------------------------------------------------------
def delaccountlink(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    user = str(request.GET['username'])
    request.session['userdel'] = user

    return redirect('/terminate_accounts/')

#-------------------------------------------------------------------------------
def adminterminate_account(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    username = request.GET['account']
    password_in = request.GET['Password']

    failcount = 0
    inputdic = {'accountin':username}
    if auth.authenticate(username = request.session['admin_name'] , password = password_in) == None:
        failcount = failcount +1
        inputdic['invalidpw'] = True


    truecount = 0
    for i in Account.objects.all():
        if str(username) == i.username:
            truecount = truecount + 1

    if truecount == 0:
        failcount = failcount +1
        inputdic['invalidaccount'] = True

    if  failcount > 0:
        inputdic['Fail'] = True
        return    render_to_response('adminaccountermination.html',inputdic)


    # If pass -- proceed with delete

    account = Account.objects.get(username = username)

    # create new deleted object

    t = terminated_accounts()
    t.username = str(account.username)
    t.sessionticker = str(account.sessionticker)
    t.completedtests = str(account.completedtests)
    t.institution_name = str(account.institution_name)
    t.modelsi = str(len(account.account_models.all()))
    t.deleted_models = str(account.deleted_models)
    t.save()


     #Delete Tests / models

    for i in account.account_models.all():

        for j in i.model_tests.all():
            j.delete()

        # delete all model test links
        for k in Test_Model_Link.objects.all():
            if str(k.model.ID2) == str(i.ID2):
                k.delete()

        i.delete()

     # Delete Picture
    os.remove(account.photolocation)


    #Delete model account links

    for i in Model_Account_Link.objects.all():
        if str(i.account.ID2) == str(account.ID2):
            i.delete()


     # delete account

    account.delete()


    return    render_to_response('accountdeleted_admin.html')

#-------------------------------------------------------------------------------
def delete_model(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    model_list = []
    account = request.session['active_account']

    for i in request.session['active_account'].account_models.all():
        model_list.append(i.model_nameID)


    inputdic = {'modelname_list':model_list}

    return    render_to_response('delete_model.html',inputdic)


#-------------------------------------------------------------------------------
def deletemodel_confirm(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    selection = request.GET['model_in']
    if selection == '0':
        return redirect('/delete_model/')

    pw = request.GET['Password']
    if pw != str(request.session['active_account'].password):
        model_list = []
        account = request.session['active_account']

        for i in request.session['active_account'].account_models.all():
            model_list.append(i.model_nameID)

        inputdic = {'modelname_list':model_list, 'passfail':True}
        return render_to_response('delete_model.html',inputdic)



    # Retrieve active model
    request.session['active_model'] = Model.objects.get(ID2 = str(request.session['active_account'].ID2) + ':' + str(selection))
    model = request.session['active_model']



    # Delete all tests

    for j in model.model_tests.all():
        j.delete()


    # delete Test Model Links
    for i in Test_Model_Link.objects.all():
        if str(i.model.ID2) == str(model.ID2):
            i.delete()

    # delete Account Model Links
    for i in Model_Account_Link.objects.all():
        if str(i.model.ID2) == str(model.ID2):
            i.delete()

    # Delete Model

    model.delete()

    # move along deleted models

    account = request.session['active_account']
    account.deleted_models = int(account.deleted_models) + 1
    account.save()

    return    render_to_response('Modeldeleted.html')

#--------------------------------------------------------------------------------------
def help(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    return    render_to_response('help.html')

#----------------------------------------------------------------------------------------
def help_how_alter_account(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    return    render_to_response('help_how_edit_account.html')

#----------------------------------------------------------------------------
# Leaderboard Again

def switchboard_toscenario(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------


    name = str(request.GET['Scenario_sort'])


    # Gather data

    inputlst = []
    for i in Account.objects.all():
        for j in i.account_models.all():
            scenarioclick = 0
            ratingsum = float(0)
            for k in j.model_tests.all():
                if k.Active == False:
                    if str(k.test_case.scenario) == name:
                        scenarioclick = scenarioclick + 1
                        ratingsum = ratingsum + float(k.test_rating)




            if scenarioclick > 0:
                avg = ratingsum / float(scenarioclick)
                username = str(i.username)

                # Create 95% Confidence Interval

                count = 0
                sumdeviationsquared = float(0)
                for k in j.model_tests.all():
                    if k.Active == False:
                        if str(k.test_case.scenario) == name:
                            count = count + 1
                            sumdeviationsquared = sumdeviationsquared + math.pow((float(k.test_rating) - float(avg)),2)


                if count > 1:

                    standarddeviation = math.sqrt(float((sumdeviationsquared / (count - 1))))

                    halfwidth = 1.96 * (standarddeviation) / math.sqrt(count)
                    halfwidth = round(halfwidth,4)

                    lowerbound = float(avg) - halfwidth

                    if lowerbound > 1:
                        lowerbound = 1
                    if lowerbound < -1:
                        lowerbound = -1

                    upperbound = float(avg) + halfwidth

                    if upperbound > 1:
                        upperbound = 1
                    if upperbound < -1:
                        upperbound = -1


                # End Confidence Interval


                entry = []
                entry.append(str(i.institution_name))
                entry.append(str(j.model_nameID))
                entry.append(str(avg))
                entry.append(str(scenarioclick))
                entry.append(username)
                if count > 1:
                    entry.append(lowerbound)
                    entry.append(upperbound)
                else:
                    entry.append(False)

                if scenarioclick < 10:
                    entry.append(True)
                else:
                    entry.append(False)



                inputlst.append(entry)
    # Sort Data

    tempterm = ''

    count = 1
    while count > 0:

        count = 0

        if len(inputlst) < 2:
            break

        for s in range(len(inputlst)-1):
            if inputlst[s][2] < inputlst[s+1][2]:
                tempterm = inputlst[s]
                inputlst[s] = inputlst[s+1]
                inputlst[s+1] = tempterm
                tempterm = ''
                count = count + 1



    inputdic = {'scenario':name,'inputlst':inputlst}



    request.session['nav'] = '4'

    scenario_lst = []
    for i in Case.objects.all():
        if str(i.scenario) not in  scenario_lst:
            scenario_lst.append(str(i.scenario))

    inputdic['scenario_lst'] = scenario_lst

    if request.session['active_account'] =='superuser':
        inputdic['superuser'] = True


    instname = '0'
    modelname ='0'
    catrating ='1'
    catcompleted ='0'

    sortinfo = []
    sortinfo.append(instname)
    sortinfo.append(modelname)
    sortinfo.append(catrating)
    sortinfo.append(catcompleted)

    inputdic['sortlst'] = sortinfo

    request.session['inputdic'] = inputdic

    return render_to_response('Leaderboard_scenario.html',inputdic)

#-------------------------------------------------------------------------------
def test_to_Scenario_switch(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------

    inputdic = request.session['inputdic']

    scenario_lst = []
    for i in Case.objects.all():
        if str(i.scenario) not in  scenario_lst:
            scenario_lst.append(str(i.scenario))

    inputdic['scenario_lst'] = scenario_lst

    request.session['nav'] = '5'

    request.session['inputdic'] = inputdic

    return render_to_response('test_to_scenario.html',inputdic)

#-------------------------------------------------------------------------------
def test_to_test_switch(request):


    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------
    inputdic = request.session['inputdic']

    request.session['nav']    = '3'


    request.session['inputdic'] = inputdic

    return render_to_response('Leaderboard_test.html',inputdic)

#--------------------------------------------------------------------------------
def scenario_to_test_switch(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------

    inputdic = request.session['inputdic']

    request.session['nav']    = '7'

    return render_to_response('scenario_to_test.html',inputdic)

#------------------------------------------------------------------------------
def scenario_to_scenario_switch(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------

    inputdic = request.session['inputdic']

    request.session['nav']    = '4'


    request.session['inputdic'] = inputdic

    scenario_lst = []
    for i in Case.objects.all():
        if str(i.scenario) not in  scenario_lst:
            scenario_lst.append(str(i.scenario))

    inputdic['scenario_lst'] = scenario_lst

    return render_to_response('Leaderboard_scenario.html',inputdic)

#---------------------------------------------------------------------------------
def hyper_leaderboard(request):
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------

    request.session['inputdic'] = ''

    return redirect('/Leader_model/')

#---------------------------------------------------------------------------------
def password_reset(request):

   return render_to_response('PasswordReset.html')


#-----------------------------------------------------------------------------------
def password_email(request):
     User_in = request.GET['Username']
     try:
        Active_account = Account.objects.get(username = User_in)
     except exceptions.ObjectDoesNotExist:
        return render_to_response('PasswordReset.html')
#     Active_account.Email
#debugx
     print Active_account.password
     length = 7
     chars = string.ascii_letters + string.digits
     random.seed = (os.urandom(1024))
     Active_account.password = ''.join(random.choice(chars) for i in range(length))
     Active_account.save()
     print Active_account.Email
     try:
        s = 'Your new password is:' + Active_account.password
        send_mail("Temporary MapScore Password", s, 'mapscore@c4i.gmu.edu', ["Active_account.Email"], fail_silently=False)
     except:
        print 'Tried to send this email:', s
        print 'To this account         :', Active_account.Email
     return render_to_response('Password_email.html')
   #fill in later

#------------------------------------------------------------------------------------
def CollectingData(request):
    return render_to_response('CollectingData.html')


#------------------------------------------------------------------------------------
def model_inst_sort(request):
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    avgrating = str(request.GET['avgrating'])
    tstcomplete = str(request.GET['tstcomplete'])
    page = str(request.GET['page'])

    modelname = '0'
    avgrating = '0'
    tstcomplete = '0'

    inputdic = request.session['inputdic']

    scorelist = inputdic['Scorelist']

    if 'caseselection' in inputdic.keys():
        caseselection = inputdic['caseselection']
    else:
        caseselection = None

    # sort depending on various circumstances

    if instname == '0':
        instname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][0] > scorelist[i+1][0] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1



    elif instname == '1':
        instname = '2'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][0] < scorelist[i+1][0] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1


    elif instname == '2':
        instname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][0] > scorelist[i+1][0] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1




    sortinfo = []
    sortinfo.append(instname)
    sortinfo.append(modelname)
    sortinfo.append(avgrating)
    sortinfo.append(tstcomplete)

    inputdic = {'Scorelist':scorelist, 'sortlst':sortinfo}

    if caseselection != None:
        inputdic['caseselection'] = caseselection

    request.session['inputdic'] = inputdic

    if page == 'model_leader':
        return render_to_response('Leader_Model.html',inputdic)

    elif page == 'model_to_scenario_move':

        scenario_lst = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_lst:
                scenario_lst.append(str(i.scenario))

        inputdic['scenario_lst'] = scenario_lst
        request.session['inputdic'] = inputdic


        return render_to_response('model_to_scenario.html',inputdic)

    elif page == 'model_to_test':
        return render_to_response('Leaderboard_testname.html',inputdic)

    elif page == 'model_to_test_fail':
        return render_to_response('Leaderboard_testname_fail.html',inputdic)

#-------------------------------------------------------------------------------
def model_name_sort(request):


    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    avgrating = str(request.GET['avgrating'])
    tstcomplete = str(request.GET['tstcomplete'])
    page = str(request.GET['page'])

    instname = '0'
    avgrating = '0'
    tstcomplete = '0'

    inputdic = request.session['inputdic']

    scorelist = inputdic['Scorelist']

    if 'caseselection' in inputdic.keys():
        caseselection = inputdic['caseselection']
    else:
        caseselection = None

    # sort depending on various circumstances

    if modelname == '0':
        modelname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][1] > scorelist[i+1][1] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1



    elif modelname == '1':
        modelname = '2'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][1] < scorelist[i+1][1] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1


    elif modelname == '2':
        modelname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][1] > scorelist[i+1][1] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1




    sortinfo = []
    sortinfo.append(instname)
    sortinfo.append(modelname)
    sortinfo.append(avgrating)
    sortinfo.append(tstcomplete)

    inputdic = {'Scorelist':scorelist, 'sortlst':sortinfo}

    if caseselection != None:
        inputdic['caseselection'] = caseselection

    request.session['inputdic'] = inputdic

    if page == 'model_leader':
        return render_to_response('Leader_Model.html',inputdic)

    elif page == 'model_to_scenario_move':


        scenario_lst = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_lst:
                scenario_lst.append(str(i.scenario))

        inputdic['scenario_lst'] = scenario_lst
        request.session['inputdic'] = inputdic

        return render_to_response('model_to_scenario.html',inputdic)

    elif page == 'model_to_test':
        return render_to_response('Leaderboard_testname.html',inputdic)

    elif page == 'model_to_test_fail':
        return render_to_response('Leaderboard_testname_fail.html',inputdic)

#------------------------------------------------------------------------------
def model_rtg_sort(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------


    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    avgrating = str(request.GET['avgrating'])
    tstcomplete = str(request.GET['tstcomplete'])
    page = str(request.GET['page'])

    modelname = '0'
    instname = '0'
    tstcomplete = '0'

    inputdic = request.session['inputdic']

    scorelist = inputdic['Scorelist']

    if 'caseselection' in inputdic.keys():
        caseselection = inputdic['caseselection']
    else:
        caseselection = None

    # sort depending on various circumstances

    if avgrating == '0':

        avgrating = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][2]) < float(scorelist[i+1][2]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1



    elif avgrating == '1':

        avgrating = '2'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][2]) > float(scorelist[i+1][2]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1


    elif avgrating == '2':
        avgrating = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][2]) < float(scorelist[i+1][2]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1




    sortinfo = []
    sortinfo.append(instname)
    sortinfo.append(modelname)
    sortinfo.append(avgrating)
    sortinfo.append(tstcomplete)

    inputdic = {'Scorelist':scorelist, 'sortlst':sortinfo}

    if caseselection != None:
        inputdic['caseselection'] = caseselection

    request.session['inputdic'] = inputdic

    if page == 'model_leader':
        return render_to_response('Leader_Model.html',inputdic)

    elif page == 'model_to_scenario_move':


        scenario_lst = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_lst:
                scenario_lst.append(str(i.scenario))

        inputdic['scenario_lst'] = scenario_lst
        request.session['inputdic'] = inputdic


        return render_to_response('model_to_scenario.html',inputdic)

    elif page == 'model_to_test':
        return render_to_response('Leaderboard_testname.html',inputdic)

    elif page == 'model_to_test_fail':
        return render_to_response('Leaderboard_testname_fail.html',inputdic)

#--------------------------------------------------------------------------------
def model_tstscomp_sort(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------


        # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    avgrating = str(request.GET['avgrating'])
    tstcomplete = str(request.GET['tstcomplete'])
    page = str(request.GET['page'])

    modelname = '0'
    instname = '0'
    avgrating = '0'

    inputdic = request.session['inputdic']

    scorelist = inputdic['Scorelist']

    if 'caseselection' in inputdic.keys():
        caseselection = inputdic['caseselection']
    else:
        caseselection = None

    # sort depending on various circumstances

    if tstcomplete == '0':

        tstcomplete = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][3]) < float(scorelist[i+1][3]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1



    elif tstcomplete == '1':

        tstcomplete = '2'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][3]) > float(scorelist[i+1][3]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1


    elif tstcomplete == '2':
        tstcomplete = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][3]) < float(scorelist[i+1][3]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1




    sortinfo = []
    sortinfo.append(instname)
    sortinfo.append(modelname)
    sortinfo.append(avgrating)
    sortinfo.append(tstcomplete)

    inputdic = {'Scorelist':scorelist, 'sortlst':sortinfo}

    if caseselection != None:
        inputdic['caseselection'] = caseselection

    request.session['inputdic'] = inputdic

    if page == 'model_leader':
        return render_to_response('Leader_Model.html',inputdic)


    elif page == 'model_to_scenario_move':

        scenario_lst = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_lst:
                scenario_lst.append(str(i.scenario))

        inputdic['scenario_lst'] = scenario_lst
        request.session['inputdic'] = inputdic

        return render_to_response('model_to_scenario.html',inputdic)

    elif page == 'model_to_test':
        return render_to_response('Leaderboard_testname.html',inputdic)

    elif page == 'model_to_test_fail':
        return render_to_response('Leaderboard_testname_fail.html',inputdic)

#----------------------------------------------------------------------------------
def test_inst_sort(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------



    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    testname = str(request.GET['testname'])
    tstrating = str(request.GET['tstrating'])
    page = str(request.GET['page'])

    modelname = '0'
    testname = '0'
    tstrating = '0'

    inputdic = request.session['inputdic']

    scorelist = inputdic['Scorelist']

    casename = inputdic['casename']

    if 'caseselection' in inputdic.keys():
        caseselection = inputdic['caseselection']
    else:
        caseselection = None

    # sort depending on various circumstances

    if instname == '0':
        instname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][0] > scorelist[i+1][0] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1



    elif instname == '1':
        instname = '2'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][0] < scorelist[i+1][0] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1


    elif instname == '2':
        instname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][0] > scorelist[i+1][0] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1




    sortinfo = []
    sortinfo.append(instname)
    sortinfo.append(modelname)
    sortinfo.append(testname)
    sortinfo.append(tstrating)

    inputdic = {'Scorelist':scorelist, 'sortlst':sortinfo}
    inputdic['casename'] = casename

    if caseselection != None:
        inputdic['caseselection'] = caseselection


    request.session['inputdic'] = inputdic

    if page == 'test_leader':
        return render_to_response('Leaderboard_test.html',inputdic)

    elif page =='test_leader_fail':
        return render_to_response('Leaderboard_Testfail.html',inputdic)

    elif page =='TEST_TOSCENARIO_MOVE':

        scenario_lst = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_lst:
                scenario_lst.append(str(i.scenario))

        inputdic['scenario_lst'] = scenario_lst
        request.session['inputdic'] = inputdic

        return render_to_response('test_to_scenario.html',inputdic)



#----------------------------------------------------------------------------------
def test_modelname_sort(request):


    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    testname = str(request.GET['testname'])
    tstrating = str(request.GET['tstrating'])
    page = str(request.GET['page'])

    instname = '0'
    testname = '0'
    tstrating = '0'

    inputdic = request.session['inputdic']

    scorelist = inputdic['Scorelist']

    casename = inputdic['casename']

    if 'caseselection' in inputdic.keys():
        caseselection = inputdic['caseselection']
    else:
        caseselection = None

    # sort depending on various circumstances

    if modelname == '0':
        modelname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][1] > scorelist[i+1][1] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1



    elif modelname == '1':
        modelname = '2'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][1] < scorelist[i+1][1] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1


    elif modelname == '2':
        modelname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][1] > scorelist[i+1][1] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1




    sortinfo = []
    sortinfo.append(instname)
    sortinfo.append(modelname)
    sortinfo.append(testname)
    sortinfo.append(tstrating)

    inputdic = {'Scorelist':scorelist, 'sortlst':sortinfo}
    inputdic['casename'] = casename

    if caseselection != None:
        inputdic['caseselection'] = caseselection

    request.session['inputdic'] = inputdic

    if page == 'test_leader':
        return render_to_response('Leaderboard_test.html',inputdic)

    elif page =='test_leader_fail':
        return render_to_response('Leaderboard_Testfail.html',inputdic)

    elif page =='TEST_TOSCENARIO_MOVE':

        scenario_lst = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_lst:
                scenario_lst.append(str(i.scenario))

        inputdic['scenario_lst'] = scenario_lst
        request.session['inputdic'] = inputdic

        return render_to_response('test_to_scenario.html',inputdic)

#-------------------------------------------------------------------------------
def test_name_sort(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    testname = str(request.GET['testname'])
    tstrating = str(request.GET['tstrating'])
    page = str(request.GET['page'])

    instname = '0'
    modelname = '0'
    tstrating = '0'

    inputdic = request.session['inputdic']

    scorelist = inputdic['Scorelist']

    casename = inputdic['casename']

    if 'caseselection' in inputdic.keys():
        caseselection = inputdic['caseselection']
    else:
        caseselection = None

    # sort depending on various circumstances

    if testname == '0':
        testname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][2] > scorelist[i+1][2] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1



    elif testname == '1':
        testname = '2'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][2] < scorelist[i+1][2] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1


    elif testname == '2':
        testname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][2] > scorelist[i+1][2] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1




    sortinfo = []
    sortinfo.append(instname)
    sortinfo.append(modelname)
    sortinfo.append(testname)
    sortinfo.append(tstrating)

    inputdic = {'Scorelist':scorelist, 'sortlst':sortinfo}
    inputdic['casename'] = casename

    if caseselection != None:
        inputdic['caseselection'] = caseselection

    request.session['inputdic'] = inputdic

    if page == 'test_leader':
        return render_to_response('Leaderboard_test.html',inputdic)

    elif page =='test_leader_fail':
        return render_to_response('Leaderboard_Testfail.html',inputdic)

    elif page =='TEST_TOSCENARIO_MOVE':

        scenario_lst = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_lst:
                scenario_lst.append(str(i.scenario))

        inputdic['scenario_lst'] = scenario_lst
        request.session['inputdic'] = inputdic

        return render_to_response('test_to_scenario.html',inputdic)

#--------------------------------------------------------------------------------
def test_rating_sort(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    testname = str(request.GET['testname'])
    tstrating = str(request.GET['tstrating'])
    page = str(request.GET['page'])

    instname = '0'
    modelname = '0'
    testname = '0'

    inputdic = request.session['inputdic']

    scorelist = inputdic['Scorelist']

    casename = inputdic['casename']

    if 'caseselection' in inputdic.keys():
        caseselection = inputdic['caseselection']
    else:
        caseselection = None

    # sort depending on various circumstances

    if tstrating == '0':
        tstrating = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][3]) < float(scorelist[i+1][3] ):
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1



    elif tstrating == '1':
        tstrating = '2'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][3]) > float(scorelist[i+1][3]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1


    elif tstrating == '2':
        tstrating = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][3]) < float(scorelist[i+1][3]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1




    sortinfo = []
    sortinfo.append(instname)
    sortinfo.append(modelname)
    sortinfo.append(testname)
    sortinfo.append(tstrating)

    inputdic = {'Scorelist':scorelist, 'sortlst':sortinfo}
    inputdic['casename'] = casename

    if caseselection != None:
        inputdic['caseselection'] = caseselection

    request.session['inputdic'] = inputdic

    if page == 'test_leader':
        return render_to_response('Leaderboard_test.html',inputdic)

    elif page =='test_leader_fail':
        return render_to_response('Leaderboard_Testfail.html',inputdic)

    elif page =='TEST_TOSCENARIO_MOVE':

        scenario_lst = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_lst:
                scenario_lst.append(str(i.scenario))

        inputdic['scenario_lst'] = scenario_lst
        request.session['inputdic'] = inputdic

        return render_to_response('test_to_scenario.html',inputdic)


#------------------------------------------------------------------------------
def cat_inst_sort(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    catrating = str(request.GET['catrating'])
    catcompleted = str(request.GET['catcompleted'])
    page = str(request.GET['page'])

    modelname = '0'
    catrating = '0'
    catcompleted = '0'

    inputdic = request.session['inputdic']

    scorelist = inputdic['inputlst']

    name = inputdic['scenario']

    if 'caseselection' in inputdic.keys():
        caseselection = inputdic['caseselection']
    else:
        caseselection = None

    # sort depending on various circumstances

    if instname == '0':
        instname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][0] > scorelist[i+1][0] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1



    elif instname == '1':
        instname = '2'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][0] < scorelist[i+1][0] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1


    elif instname == '2':
        instname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][0] > scorelist[i+1][0] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1




    sortinfo = []
    sortinfo.append(instname)
    sortinfo.append(modelname)
    sortinfo.append(catrating)
    sortinfo.append(catcompleted)

    inputdic = {'inputlst':scorelist, 'sortlst':sortinfo}


    if caseselection != None:
        inputdic['caseselection'] = caseselection

    request.session['inputdic'] = inputdic



    if page == 'category_leader':

        scenario_lst = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_lst:
                scenario_lst.append(str(i.scenario))

        inputdic['scenario_lst'] = scenario_lst
        inputdic['scenario'] = name


        request.session['inputdic'] = inputdic


        return render_to_response('Leaderboard_scenario.html',inputdic)

    elif page == 'scenario_to_test':

        inputdic['scenario'] = name
        request.session['inputdic'] = inputdic

        return render_to_response('scenario_to_test.html',inputdic)

    elif page =='scenario_to_test_fail':

        inputdic['scenario'] = name
        request.session['inputdic'] = inputdic

        return render_to_response('scenario_to_testfail.html',inputdic)

#----------------------------------------------------------------------------
def cat_modelname_sort(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------


    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    catrating = str(request.GET['catrating'])
    catcompleted = str(request.GET['catcompleted'])
    page = str(request.GET['page'])

    instname = '0'
    catrating = '0'
    catcompleted = '0'

    inputdic = request.session['inputdic']

    scorelist = inputdic['inputlst']

    name = inputdic['scenario']

    if 'caseselection' in inputdic.keys():
        caseselection = inputdic['caseselection']
    else:
        caseselection = None

    # sort depending on various circumstances

    if modelname == '0':
        modelname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][1] > scorelist[i+1][1] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1



    elif modelname == '1':
        modelname = '2'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][1] < scorelist[i+1][1] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1


    elif modelname == '2':
        modelname = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if scorelist[i][1] > scorelist[i+1][1] :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1




    sortinfo = []
    sortinfo.append(instname)
    sortinfo.append(modelname)
    sortinfo.append(catrating)
    sortinfo.append(catcompleted)

    inputdic = {'inputlst':scorelist, 'sortlst':sortinfo}


    if caseselection != None:
        inputdic['caseselection'] = caseselection

    request.session['inputdic'] = inputdic



    if page == 'category_leader':

        scenario_lst = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_lst:
                scenario_lst.append(str(i.scenario))

        inputdic['scenario_lst'] = scenario_lst
        inputdic['scenario'] = name


        request.session['inputdic'] = inputdic


        return render_to_response('Leaderboard_scenario.html',inputdic)

    elif page == 'scenario_to_test':

        inputdic['scenario'] = name
        request.session['inputdic'] = inputdic

        return render_to_response('scenario_to_test.html',inputdic)

    elif page =='scenario_to_test_fail':

        inputdic['scenario'] = name
        request.session['inputdic'] = inputdic

        return render_to_response('scenario_to_testfail.html',inputdic)


#-----------------------------------------------------------------------------
def catrating_sort(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------


    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    catrating = str(request.GET['catrating'])
    catcompleted = str(request.GET['catcompleted'])
    page = str(request.GET['page'])

    instname = '0'
    modelname = '0'
    catcompleted = '0'

    inputdic = request.session['inputdic']

    scorelist = inputdic['inputlst']

    name = inputdic['scenario']

    if 'caseselection' in inputdic.keys():
        caseselection = inputdic['caseselection']
    else:
        caseselection = None

    # sort depending on various circumstances

    if catrating == '0':
        catrating = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][2]) < float(scorelist[i+1][2]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1



    elif catrating == '1':
        catrating = '2'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][2]) > float(scorelist[i+1][2]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1


    elif catrating == '2':
        catrating = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][2]) < float(scorelist[i+1][2]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1




    sortinfo = []
    sortinfo.append(instname)
    sortinfo.append(modelname)
    sortinfo.append(catrating)
    sortinfo.append(catcompleted)

    inputdic = {'inputlst':scorelist, 'sortlst':sortinfo}


    if caseselection != None:
        inputdic['caseselection'] = caseselection


    request.session['inputdic'] = inputdic



    if page == 'category_leader':

        scenario_lst = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_lst:
                scenario_lst.append(str(i.scenario))

        inputdic['scenario_lst'] = scenario_lst
        inputdic['scenario'] = name


        request.session['inputdic'] = inputdic


        return render_to_response('Leaderboard_scenario.html',inputdic)

    elif page == 'scenario_to_test':

        inputdic['scenario'] = name
        request.session['inputdic'] = inputdic

        return render_to_response('scenario_to_test.html',inputdic)

    elif page =='scenario_to_test_fail':

        inputdic['scenario'] = name
        request.session['inputdic'] = inputdic

        return render_to_response('scenario_to_testfail.html',inputdic)


#-------------------------------------------------------------------------------
def catcompleted_sort(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    catrating = str(request.GET['catrating'])
    catcompleted = str(request.GET['catcompleted'])
    page = str(request.GET['page'])

    instname = '0'
    catrating = '0'
    modelname = '0'

    inputdic = request.session['inputdic']

    scorelist = inputdic['inputlst']

    name = inputdic['scenario']
    if 'caseselection' in inputdic.keys():
        caseselection = inputdic['caseselection']
    else:
        caseselection = None


    # sort depending on various circumstances

    if catcompleted == '0':
        catcompleted = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][3]) < float(scorelist[i+1][3]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1



    elif catcompleted == '1':
        catcompleted = '2'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][3]) > float(scorelist[i+1][3]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1


    elif catcompleted == '2':
        catcompleted = '1'

        count = 1
        temp = ''
        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][3]) < float(scorelist[i+1][3]) :
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count = count + 1




    sortinfo = []
    sortinfo.append(instname)
    sortinfo.append(modelname)
    sortinfo.append(catrating)
    sortinfo.append(catcompleted)

    inputdic = {'inputlst':scorelist, 'sortlst':sortinfo}


    if caseselection != None:
        inputdic['caseselection'] = caseselection


    request.session['inputdic'] = inputdic



    if page == 'category_leader':

        scenario_lst = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_lst:
                scenario_lst.append(str(i.scenario))

        inputdic['scenario_lst'] = scenario_lst
        inputdic['scenario'] = name


        request.session['inputdic'] = inputdic


        return render_to_response('Leaderboard_scenario.html',inputdic)

    elif page == 'scenario_to_test':

        inputdic['scenario'] = name
        request.session['inputdic'] = inputdic

        return render_to_response('scenario_to_test.html',inputdic)

    elif page =='scenario_to_test_fail':

        inputdic['scenario'] = name
        request.session['inputdic'] = inputdic

        return render_to_response('scenario_to_testfail.html',inputdic)

#-----------------------------------------------------------------------------
def model_edit_info(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    description = str(request.session['active_model'].Description)
    name = request.session['active_model'].model_nameID

    inputdic = {}
    inputdic['description'] = description
    inputdic['model_name'] = name

    return render_to_response('edit_model_info.html',inputdic)

#----------------------------------------------------------------------------
def model_change_info(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    pw = str(request.GET['Password'])
    des = str(request.GET['description'])
    name = request.session['active_model'].model_nameID


    account = request.session['active_account']
    model = request.session['active_model']

    password = str(account.password)

    inputdic = {}
    inputdic['description'] = des
    inputdic['model_name'] = name

    count = 0
    if pw != password:
        count = count + 1
        inputdic['passfail'] = True


    baddescription = r'^\s*$'

    if re.match(baddescription,des) != None:
        count = count + 1
        inputdic['Fail1'] = True


    if count > 0:
        return render_to_response('edit_model_info.html',inputdic)





    # If everything works out

    model.Description = des
    model.save()

    return render_to_response('model_info_updated.html')

#----------------------------------------------------------------------------
def model_Profile(request):

    #-------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False and request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #-------------------------------------------------------------------

    Account_in = str(request.GET['Account'])
    Model = str(request.GET['Model'])

    Active_account = Account.objects.get(username = Account_in)
    Active_model = Active_account.account_models.get(model_nameID = Model)

    Name = str(Active_model.model_nameID)
    Accountname = str(Active_account.institution_name)
    description = str(Active_model.Description)
    username = str(Active_account.username)

    modeldic = {'Name':Name,'Accountname':Accountname,'Description':description,'username':username}

    return render_to_response('model_Profile.html',modeldic)

#------------------------------------------------------------------------------
def metric_description (request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    return render_to_response('metric_description.html')

#------------------------------------------------------------------------------
def metric_description_nonactive (request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    return render_to_response('metric_description_nonactive.html')

#------------------------------------------------------------------------------
def metric_description_submissionreview (request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    return render_to_response('metric_description_submissionreview.html')

#------------------------------------------------------------------------------
def reg_conditions(request):

    return render_to_response('regconditions.html')


#---------------------------------------------------------------------------------
def DownloadGridsync(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

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


#----------------------------------------------------------------------------------------
def DownloadParam(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------


    active_test = request.session['active_test']
    active_case = active_test.test_case




    instring =   "Case_Name: " + active_case.case_name + '\r\n'
    instring = instring + "Coordinate_System: WGS_84" + '\r\n'
    instring =  instring + "Subject_Age: " +  active_case.Age + '\r\n'
    instring =  instring +"Subject_Gender: " + active_case.Sex + '\r\n'
    instring = instring + "Subject_Category: " + active_case.subject_category  + '\r\n'
    instring = instring + "Subject_Scenario: " + active_case.scenario + '\r\n'
    instring = instring + "Subject_SubCategory: " + active_case.subject_subcategory + '\r\n'
    instring = instring + "Subject_Activity: " + active_case.subject_activity + '\r\n'
    instring = instring + "Group_Type: " + active_case.group_type   + '\r\n'
    instring = instring + "Number_Lost: " + active_case.number_lost + '\r\n'
    instring = instring + "Terrain: " + active_case.terrain + '\r\n'
    instring = instring + "Ecoregion_Domain: " + active_case.ecoregion_domain  + '\r\n'
    instring = instring + "Ecoregion_Division: " + active_case.ecoregion_division + '\r\n'
    instring = instring + "Total_Hours_Before_Location: " + active_case.total_hours  + '\r\n'
    instring = instring +"Last_Known_Position: " + '('+active_case.lastlat + ',' +active_case.lastlon + ')'  + '\r\n'
    instring = instring + "Number_Horizantal_Cells: " + active_case.sidecellnumber + '\r\n'
    instring = instring + "Number_Vertical_Cells: " + active_case.sidecellnumber + '\r\n'
    instring = instring + "Total_Number_Cells: " + active_case.totalcellnumber + '\r\n'
    instring = instring + "Estimated_Cell_Width: 5 m" + '\r\n'
    instring = instring + "Estimated_Search_Region_Width: 25 km" + '\r\n'
    instring = instring + "Search_Region_Upper_Lat: " + active_case.upleft_lat  + '\r\n'
    instring = instring + "Search_Region_Lower_Lat: " + active_case.downleft_lat  + '\r\n'
    instring = instring + "Search_Region_Right_Lon: " + active_case.downright_lon + '\r\n'
    instring = instring + "Search_Region_Left_Lon: " + active_case.upleft_lon  + '\r\n'



    #image = Image.open(NameFile)

    #wrap = FileWrapper(NameFile)

    resp = HttpResponse(content_type = 'text/plain')

    #resp['Content-Length'] = os.path.getsize(NameFile)

    resp['Content-Disposition'] = 'attachment; filename= ScenarioParameters.txt'

    #image.save(resp,'png')

    resp.write(instring)


    return resp

#----------------------------------------------------------------
def UploadLayers(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------


    request.session['ActiveAdminCase'] = int(request.GET['id'])

    admincase = Case.objects.get(id = request.session['ActiveAdminCase'])

    inputdic = {}
    inputdic['id'] = request.session['ActiveAdminCase']
    inputdic['Name'] =  admincase.case_name
    inputdic.update(csrf(request))

    if admincase.UploadedLayers == True:

        inputdic['layersexist'] = True
    else:
        inputdic['layersexist'] = False

    return render_to_response('UploadLayersMenu.html',inputdic)

#---------------------------------------------------------------

def upload_Layerfile(request):


    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------
    # Take in file - save to server

    admincase = Case.objects.get(id = request.session['ActiveAdminCase'])

    string = str(admincase.LayerField)

    if admincase.UploadedLayers == True:


        stream = "Layers/" + str(admincase.id) +'_' + str(admincase.case_name)

        os.remove(string)
        shutil.rmtree(stream)

        admincase.UploadedLayers = False
        admincase.save()







    destination = open(string,'wb+')

    for chunk in request.FILES['caselayer'].chunks():
        destination.write(chunk)
    destination.close()

    admincase.UploadedLayers = True
    admincase.save()



    zippin = zipfile.ZipFile(string,'r')

    stream = "Layers/" + str(admincase.id) +'_' + str(admincase.case_name)

    zippin.extractall(stream)



    return render_to_response('CaseLayersComplete.html')



#---------------------------------------------------------------
def DownloadLayers(request):

    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['usertoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------
    active_test = request.session['active_test']
    active_case = active_test.test_case
    string = str(active_case.LayerField)
    zippin = zipfile.ZipFile(string,'r')
    zippinlst = zippin.namelist()
    zippin.close()
    buff = cStringIO.StringIO()
    zippin2 = zipfile.ZipFile(buff,'w',zipfile.ZIP_DEFLATED)
    for name in zippinlst:

        stream = "Layers/" + str(active_case.id) +'_' + str(active_case.case_name) + "/" + name
        for i in range(len(name)-1):
            if name[i] == '/':
                term = i
                break

        name2 = name[term+1:len(name)]
        if not stream[len(stream)-1] == '/':
            filein = open(stream,'rb')
            zippin2.writestr(name2,filein.read())

    zippin2.close()
    buff.flush()
    writeinfo = buff.getvalue()
    buff.close()

    resp = HttpResponse( content_type = 'application/zip')
    resp['Content-Disposition'] = 'attachment; filename= Layers.zip'
    resp.write(writeinfo)

    return resp

#-------------------------------------------------------------------------------
def delete_Layers(request):


    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------

    # Take in file - save to server

    admincase = Case.objects.get(id = request.session['ActiveAdminCase'])

    string = str(admincase.LayerField)

    stream = "Layers/" + str(admincase.id) +'_' + str(admincase.case_name)

    os.remove(string)
    shutil.rmtree(stream)

    admincase.UploadedLayers = False
    admincase.save()

    return redirect("/admin_cases/")

#---------------------------------------------------------------
def DownloadLayersadmin(request):


    #------------------------------------------------------------------
    # Token Verification
    try:
        if request.session['admintoken'] == False:
            return render_to_response('noaccess.html',{})
    except:
        return render_to_response('noaccess.html',{})

    #----------------------------------------------------------------
    active_case = Case.objects.get(id = request.session['ActiveAdminCase'])

    string = str(active_case.LayerField)
    zippin = zipfile.ZipFile(string,'r')
    zippinlst = zippin.namelist()
    zippin.close()
    buff = cStringIO.StringIO()
    zippin2 = zipfile.ZipFile(buff,'w',zipfile.ZIP_DEFLATED)

    for name in zippinlst:
        stream = "Layers/" + str(active_case.id) +'_' + str(active_case.case_name) + "/" + name
        for i in range(len(name)-1):
            if name[i] == '/':
                term = i
                break

        name2 = name[term+1:len(name)]

        if not stream[len(stream)-1] == '/':
            filein = open(stream,'rb')
            zippin2.writestr(name2,filein.read())

    zippin2.close()
    buff.flush()
    writeinfo = buff.getvalue()
    buff.close()
    resp = HttpResponse( content_type = 'application/zip')
    resp['Content-Disposition'] = 'attachment; filename= Layers.zip'
    resp.write(writeinfo)

    return resp


#-------------------------------------------------------------------------------
def old_casetypeselect(request):
    AUTHENTICATE()
    if False:
        # only one active test at a time
        count001 = 0
        for i in request.session['active_model'].model_tests.all():
            if i.Active == True:
                count001 = count001 +1
        if count001 >0:
            return render_to_response('TestWelcome_alreadyactive.html')

        # If all tests completed
        count2 = 0
        for i in request.session['active_model'].model_tests.all():
            if i.Active == False:
                count2 = count2 +1
        if int(count2) == int(len(Case.objects.all())):
            return render_to_response('nomorecases.html')
    type_lst = []
    for i in Case.objects.all():
        if str(i.subject_category) not in  type_lst:
            type_lst.append(str(i.subject_category))

    return render_to_response('Testselect.html',{'types':type_lst})


#--------------------------------------------------------------------------------
def casetypeselect(request):
    AUTHENTICATE()

    name_lst = sorted(set([str(x.case_name) for x in Case.objects.all()]))
    type_lst = sorted(set([str(x.subject_category) for x in Case.objects.all()]))
    return render_to_response('Testselect.html',{'names':name_lst, 'types':type_lst})

#--------------------------------------------------------------------------------
def TesttypeSwitch(request):
    AUTHENTICATE()

    selection = request.GET['typein2']
    if selection ==0:
        return redirect("/casetypeselect/")

    for i in Case.objects.all():
        if i.subject_category==selection:
            counter01 = 0
            havecase = False
            for j in request.session['active_model'].model_tests.all():
                if i.case_name == j.test_case.case_name:
                    counter01 = counter01+1

            if counter01 == 0:
                request.session['active_case_temp'] = i
                havecase = True
                break

    if havecase == False:
        return render_to_response('nomorecasestype.html',{'selection':selection})

    return redirect("/new_test/")

#--------------------------------------------------------------------------------
def TestNameSwitch(request):
    AUTHENTICATE()
    selection = request.GET['casename']
    if selection ==0:
        return redirect("/casetypeselect/")

    havecase = False
    try:
        request.session['active_case_temp'] = Case.objects.get(case_name=selection)
        return redirect("/new_test/")
    except Case.DoesNotExist:
        return render_to_response('nomorecasestype.html',{'selection':selection})
    else:
        # Multiple Cases Found -- Pick the first
        cases = Case.objects.filter(case_name = selection)
        request.session['active_case_temp'] = cases[0]
        return redirect("/new_test/")

#--------------------------------------------------------------------------------

def NextSequentialTestSwitch(request):
    AUTHENTICATE()

    for i in Case.objects.all():
        counter01 = 0
        havecase = False
        for j in request.session['active_model'].model_tests.all():
            if i.case_name == j.test_case.case_name:
                counter01 = counter01+1

        if counter01 == 0:
            request.session['active_case_temp'] = i
            havecase = True
            break
    if havecase == False:
        return render_to_response('nomorecases.html')

    return redirect("/new_test/")

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





