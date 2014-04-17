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
from django.core.files.move import file_move_safe
from operator import itemgetter, attrgetter
from django.template import RequestContext
import random
import shutil
import math
import csv
import os
import string
import numpy as np
import sys

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
from PIL import Image
import zipfile
from django.core.servers.basehttp import FileWrapper
from django.core.context_processors import csrf
#import Documnet forms
from mapscore.forms import ZipUploadForm

##################### Media File Locations ################################
#MEDIA_DIR = 'C:/Users/Nathan Jones/Django Website/MapRateWeb/media/'
#USER_GRAYSCALE = 'C:/Users/Nathan Jones/Django Website/MapRateWeb/user_grayscale/'
MEDIA_DIR = 'media/'         # for the server
USER_GRAYSCALE = 'user_grayscale/'

# console print e.g.:
#print >>sys.stderr, 'Goodbye, cruel world!'


#--------------------------------------------------------------
def base_redirect(response):
    return redirect('/main/')


#--------------------------------------------------------------------------------
def AUTHENTICATE(token='usertoken'):
    '''token is either 'usertoken' or 'admintoken'
    '''
    # todo: fix because I don't think this works without passing the request object
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
def batch_test_upload(request):
    AUTHENTICATE() # does not work ??
    try:
         if request.session['admintoken'] == False and request.session['usertoken'] == False:
             return render_to_response('noaccess.html',{})
    except:
         return render_to_response('noaccess.html',{})

    context_instance=RequestContext(request)
    case_list = []
    update_list = []
    if request.method == 'POST':
        form = ZipUploadForm(request.POST, request.FILES)
        if form.is_valid():
            case_list = form.process_zip_file()
            gc = 0 #good count
            bc = 0 #bad count
            for index, (path, fname, file_size, model, case, status) in enumerate(case_list):
                if status == "ready":
                    model_count = Model.objects.filter(ID2 = str(request.session['active_account'].ID2 +":"+ model)).count()
                    if model_count == 0:
                        status = "model not found"
                    case_count = Case.objects.filter(case_name = str(case)).count()

                    if case_count == 0:
                        if status == "model not found":
                            status = "model nor case found"
                        else:
                            status = "case not found"
                if status == "ready":
                    gc += 1
                else:
                    os.unlink(path)
                    status += ", image deleted"
                    bc += 1
                update_list.append((path, fname, file_size, model, case, status))

            request.session['gcount'] = gc
            request.session['bcount'] = bc
            request.session['batch_list'] = update_list

            return render_to_response('batch_test_upload_confirm.html',
                {'case_list': update_list, 'gcount': gc, 'bcount': bc},
                context_instance=RequestContext(request)
            )

    else:

        form = ZipUploadForm() # A empty, unbound form

    return render_to_response('batch_test_upload.html',{'form': form},
        context_instance=RequestContext(request)
    )
#-----------------------------------------------------------------
def batch_test_upload_final(request):
    AUTHENTICATE() # this functions doesn't work, needs fixen'

    try:
         if request.session['admintoken'] == False and request.session['usertoken'] == False:
             return render_to_response('noaccess.html',{})
    except:
         return render_to_response('noaccess.html',{})

    if request.method != 'POST':
        return render_to_response('AccountScreen.html', {})

    result_data = []

    if request.session.get("batch_list") == False:
        result = "Error, contact batch_list session was not found."
        return render_to_response('batch_test_upload_final.html',{'result': result,
            'result_data': result_data})

    if request.session["batch_list"] == "completed":
        result = "completed"
        return render_to_response('batch_test_upload_final.html',{'result': result,
            'result_data': result_data})


    if 'abort' in request.POST:
        # User aborted, so delete all the ready temp grayscales
        for index, (path, fname, file_size, model, case, status) in enumerate(request.session.get("batch_list")):
            if status == "ready":
                try:
                    os.remove(path)
                except OSError:
                    pass
        result = "abort"
        return render_to_response('batch_test_upload_final.html',{'result': result,
            'result_data': result_data})

    (result, result_data) = process_batch_tests(request)

    return render_to_response('batch_test_upload_final.html',{'result': result,
        'result_data': result_data})
#-----------------------------------------------------------------
def process_batch_tests(request):

    # we need to know what the active account is, store simplify
    act_account = str(request.session['active_account'].ID2)

    tests_list = request.session.get("batch_list")
    result_data = []
    for index, (path, fname, file_size, model, case, status) in enumerate(tests_list):
        if status != "ready":
            continue
        #let's get active model object
        a_model = Model.objects.get(ID2 = act_account + ":" + str(model)) #str prolly isn't needed

        # get active case, already verified it exists so skip error check for now
        a_case = Case.objects.get(case_name=str(case))

        # note similar code to below also exists in create_test()

        # set ID2 for this test case "User:Model:Case"
        ID2 = str(a_model.ID2) + ':' + str(a_case.case_name)

        # First check to see if this test already exists
        # and if yes, delete existing one to prevent duplicates
        try:
            findtest = Test.objects.get(ID2 = ID2)
        except Test.DoesNotExist:
            findtest = None
        # Test does exist:
        if findtest != None:
            print >>sys.stderr, 'DEBUG: deleting previous test\n'
            print >>sys.stderr, str(findtest.id) + ":" + str(findtest.ID2)
            #delete the test_model_link first
            OldLink = Test_Model_Link.objects.get(test = findtest.id)
            OldLink.delete()
            #then delete existing test
            findtest.delete()

        #create new test:
        newtest = Test( test_case = a_case,
            test_name = a_case.case_name,
            ID2 = ID2 )

        newtest.save()

        Link = Test_Model_Link( test = newtest,
                    model = a_model)
        Link.save()
        newtest.setup()
        newtest.save()

        # copy grayscale from temp to media for storage
        grayrefresh = int(newtest.grayrefresh) + 1
        newtest.grayrefresh = grayrefresh

        #not sure why we have to put this in the media directory ?
        # but the single file process does it
        new_grayfile = MEDIA_DIR
        new_grayfile += str(newtest.ID2.replace(':','_'))
        new_grayfile += '_%d.png' % grayrefresh
        newtest.grayscale_path = new_grayfile
        newtest.save()

        file_move_safe(path, new_grayfile, 65536, True)

        # create string for saving thumbnail 128x128
        thumb = MEDIA_DIR + "thumb_" + str(newtest.ID2).replace(':','_') + ".png"

        newtest.grayrefresh = int(newtest.grayrefresh) + 1
        s = USER_GRAYSCALE + str(newtest.ID2).replace(':','_')
        s += '_%s.png' % str(newtest.grayrefresh)

        # Remove served Grayscale image
        file_move_safe(newtest.grayscale_path, s, 65536, True)
#        shutil.move(newtest.grayscale_path, s)
        # set the path
        newtest.grayscale_path = s
        newtest.save()

        from PIL import Image
        im = Image.open(s)
        im = im.convert('RGB')
        im.thumbnail((128,128), Image.ANTIALIAS)
        im.save(thumb,'PNG')

        # thumbnail is saved in MEDIA_DIR dir with name:
        # save as thumb_User_Model_Case.png

        #debugx
        print >>sys.stderr, "DEBUGX:"
        print >>sys.stderr, str(thumb)

        response = newtest.rate()
        os.unlink(newtest.grayscale_path)

        # record rating
        #---------------------------------------------------------------
        request.session['active_account'].completedtests = int(request.session['active_account'].completedtests) + 1
        request.session['active_account'].save()
        #---------------------------------------------------------------
        result_data.append((model,case,newtest.ID2,newtest.test_rating,"ok"))

    request.session['batch_list'] = "completed"
    return (0,result_data)
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
#    print "debug"
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
            request.session['active_model'] = Model.objects.get(ID2 = str(request.session['active_account'].ID2) + ':' + str(selection))

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
    country = case.country
    state = case.state
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

    # Need to avoid creating duplicate tests for given model/case
    # idea: delete exisitng test model link and test, then create new one ?
    ID2 = str(request.session['active_model'].ID2) + ':' + str(tempcase.case_name)
    try:
        findtest = Test.objects.get(ID2 = ID2)
    except Test.DoesNotExist:
        findtest = None

    if findtest != None:
        #print >>sys.stderr, 'DEBUG:\n'
        #print >>sys.stderr, str(findtest.id) + ":" + str(findtest.ID2)
        #delete the test_model_link first
        OldLink = Test_Model_Link.objects.get(test = findtest.id)
        OldLink.delete()
        #then delete existing test
        findtest.delete()

    newtest = Test( test_case = tempcase,
        test_name = tempcase.case_name,
        ID2 = ID2 )

    newtest.save()

    Link = Test_Model_Link( test = newtest,
                model = request.session['active_model'])

    Link.save()
    newtest.setup()
    newtest.save()
    request.session['active_test'] = newtest
    request.session['createcheck'] = True

    return redirect('/test_active/')

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
    '''Enables instructions screen, and calls instructions page.'''

    AUTHENTICATE()

    request.session['active_test'].show_instructions = True
    request.session['active_test'].save()
    return redirect('/test_instructions/')



#-------------------------------------------------------------------
def tst_instructions(request):
    '''Show the instructions for creating images.'''

    AUTHENTICATE()
    if request.session['active_test'].show_instructions == True:
        request.session['active_test'].show_instructions = False
        request.session['active_test'].save()
        return render_to_response('tst_instructions.html')
    else:
        return redirect('/test_active/')

#-------------------------------------------------------------------------------------------

def active_test(request):
    '''Retrieve data for the active test and render file_up.html.

    This used to administer the gridtest if you hadn't already passed.

    TODO: there is no need to define all these local variables.

    '''
    AUTHENTICATE()

    #request.session['active_test'] = Test.objects.get(ID2 = request.session['active_test'].ID2)
    active_test = request.session['active_test']
    print str(active_test.nav) + '-----nav'
    active_test.nav == 2      # Assume we passed the grid test
    active_test = request.session['active_test']
    active_case = active_test.test_case

    age = active_case.Age
    name = active_case.case_name
    sex = active_case.Sex
    country = active_case.country
    state = active_case.state
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

    inputdic = {'Name_act':account_name, 'Name_m':model_name, 'name' :name, 'age':age,
                'country':country,'state':state, 'sex':sex,'LKP':LKP,'horcells':sidecells,
                'vercells':sidecells,'totcells' : totalcells, 'cellwidth' : 5,
                'regionwidth' : 25,'uplat':uplat,'rightlon':rightlon,'downlat':downlat,
                'leftlon':leftlon,'MAP':URL}
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

    # Save the grayscale file path to the test object
    active_test.grayscale_path = string
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
    image_in = Image.open(request.session['active_test'].grayscale_path)
    s = str(request.session['active_test'].ID2).replace(':','_')
    served_Location = '/%s%s_%s.png' % (MEDIA_DIR, s, str(request.session['active_test'].grayrefresh))
    inputdic = {'grayscale':served_Location}

    # Check dimensions
    if image_in.size[0] != 5001 or image_in.size[1] != 5001:
        return render_to_response('uploadfail_demensions.html',inputdic)

    data = image_in.getdata()
    bands = image_in.getbands()

    if bands[:3] == ('R','G','B'):
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
    os.remove(request.session['active_test'].grayscale_path)

    # Wipe the path
    request.session['active_test'].grayscale_path = 'none'
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

    # create string for saving thumbnail 128x128
    thumb = MEDIA_DIR + "thumb_" + str(request.session['active_test'].ID2).replace(':','_') + ".png"

    shutil.move(request.session['active_test'].grayscale_path, s)

    from PIL import Image
    im = Image.open(s)
    im = im.convert('RGB')
    im.thumbnail((128,128), Image.ANTIALIAS)
    im.save(thumb,'PNG')

    # thumbnail is saved in USER_GRAYSCALE dir with name:
    # save as thumb_User_Model_Case.png

    #debugx
    #print >>sys.stderr, "DEBUGX:"
    #print >>sys.stderr, str(thumb)

    # set the path
    request.session['active_test'].grayscale_path = s
    request.session['active_test'].save()

    return redirect('/Rate_Test/')


#-----------------------------------------------------------------------------




def Rate(request):

    AUTHENTICATE()
    response = request.session['active_test'].rate()

    # Resync Model
    request.session['active_model'] = Model.objects.get(ID2 = request.session['active_model'].ID2)

    os.remove(request.session['active_test'].grayscale_path)


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
    country = active_case.country
    state = active_case.state
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

    inputdic = {'Name_act':account_name, 'Name_m':model_name, 'name' :name, 'age':age,'country':country,'state':state, 'sex':sex,'LKP':LKP,'horcells':sidecells,'vercells':sidecells,'totcells' : totalcells, 'cellwidth' : 5, 'regionwidth' : 25,'uplat':uplat,'rightlon':rightlon,'downlat':downlat,'leftlon':leftlon,'MAP':URL}
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
    #debugx
    print >>sys.stderr, 'DEBUG:\n'
    print >>sys.stderr, intest
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
    country = active_case.country
    state = active_case.state
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

    inputdic = {'Name_act':account_name, 'Name_m':model_name, 'name' :name, 'age':age,'country':country,'state':state, 'sex':sex,'LKP':LKP,'horcells':sidecells,'vercells':sidecells,'totcells' : totalcells, 'cellwidth' : 5, 'regionwidth' : 25,'uplat':uplat,'rightlon':rightlon,'downlat':downlat,'leftlon':leftlon,'MAP':URL}
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

#------------------------------------------------------------------------------
def confidence_interval(scores):
    '''Return the 95% CI of the mean as (lowerbound, upperbound).

    @param scores: iterable of float with relevant scores

    Because we are trying to infer bounds on the actual
    (population) performance of the model, from limited samples,
    we use +- 1.96 * SEM, the standard error of the mean.
            SEM = stdev / sqrt(N)

    '''
    N,avg,stdev = 0,0.0,0.0
    try:
        N, avg, stdev = len(scores), np.mean(scores), np.std(scores)
        halfwidth = 1.96*stdev / math.sqrt(N)
        lowerbound = round(np.clip(avg-halfwidth, -1, 1),4)
        upperbound = round(np.clip(avg+halfwidth, -1, 1),4)
        return (lowerbound, upperbound)
    except:
        print >> sys.stderr, 'No 95%% CI. N=%d, avg=%6.2f, std=%6.2f' % (N, avg, stdev)
        return (0,0)

#----------------------------------------------------------------------------------------------------------------------------------------------------
def Leader_model(request):
    '''Create the leaderboard.'''
    AUTHENTICATE_EITHER()

    sorted_models = get_sorted_models(Model.objects.all())
    # Build Leaderboard
    inputlist = []
    for model in sorted_models:
        # Read info
        account = model.account_set.all()[0]
        institution = account.institution_name
        username = account.username
        name = model.model_nameID
        rating = float(model.model_avgrating)
        tests = model.model_tests.all()
        finished_tests = [x for x in tests if not x.Active]
        N = len(finished_tests)
        scores = [float(x.test_rating) for x in finished_tests]

        # Build case, depending on sample size
        case = [institution, name, '%5.3f'%rating, N, username]
        if N <= 1:
            case.extend([-1, 1, True])  # std=False, sm.sample=True
        else:
            lowerbound, upperbound = confidence_interval(scores)
            if N < 10:  # small sample=True
                case.extend([lowerbound, upperbound, True])
            else: # small sample = False
                case.extend([lowerbound, upperbound, False])
        #print >> sys.stderr, case
        inputlist.append(case)


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
    inputlist = []
    for test in sorted_tests:
        print >> sys.stderr, dir(test.model_set.all()[0])
        inputlist.append(
            # TODO: No field institution_name.  Fields are:
            # account_set, clean_fields, gridvalidated, id, model_account_link_set,
            # model_avgrating, model_nameID, model_tests, test_model_link_set,
            # update_rating, validate_unique
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
            thumb = MEDIA_DIR + "thumb_" + str(i.ID2).replace(':','_') + ".png"
            thumbexists = False
            if os.path.isfile(thumb):
                thumbexists = True
            completed_lst.append({'test_name':i.test_name, 'test_rating':i.test_rating, 'thumb':thumb, 'thumbexists':thumbexists})

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
    country = active_case.country
    state = active_case.state
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

    inputdic = { 'name' :name, 'age':age,'country':country,'state':state, 'sex':sex,'LKP':LKP,'horcells':sidecells,'vercells':sidecells,'totcells' : totalcells, 'cellwidth' : 5, 'regionwidth' : 25,'uplat':uplat,'rightlon':rightlon,'downlat':downlat,'leftlon':leftlon,'MAP':URL}
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
    # bulk add new cases to the database
    # should use a CSV file, most easily generated in Excel
    # Comma separated and quotes for text delimiter
    # be tolerant about use of carriage returns (win vs mac vs linux)

    AUTHENTICATE('admintoken')

    file = request.FILES['casecsv']
    # use python csv reader, tell it to expect excel style
    # CSV with delimiter: , and quote char as quotes ""
    data = [row for row in csv.reader(file.read().splitlines(),
                                      dialect=csv.excel_tab, delimiter=',',
                                      quotechar='"')]
    # If the first line looks like the header, ignore it
    if data[0][0] == 'Name':
        data.pop(0)
    case_report = []

    for row in data:
        #print >>sys.stderr, row #debugx
        new_case = Case(
            case_name = row[0],
            key = row[1],
            country = row[2],
            state =     row[3],
            county = row[4],
            populationdensity = row[5],
            weather = row[6],
            subject_category = row[7],
            subject_subcategory = row[8],
            scenario  = row[9],
            subject_activity = row[10],
            Age = row[11],
            Sex = row[12],
            number_lost = row[13],
            group_type = row[14],
            ecoregion_domain = row[15],
            ecoregion_division = row[16],
            terrain = row[17],
            lastlat = row[18],
            lastlon = row[19],
            findlat = row[20],
            findlon = row[21],
            total_hours = row[22],
            notify_hours = row[23],
            search_hours = row[24],
            comments = row[25],
            )
        # look and see if this case already exists, ignore it if it does
        # we may need a mechanism for updating an existing case somehow in the
        # future...
        try:
            find_case = Case.objects.get(case_name = new_case.case_name)
        except Case.DoesNotExist:
            find_case = None
        # Case does exist:
        if find_case != None:
            print >>sys.stderr, 'WARN: ' + new_case.case_name + ' already exists in framework_case, ignoring\n'
            row.append("Ignored, name exists")
        else:
            new_case.initialize()
            new_case.save()
            row.append("Success")

    return render_to_response('bulkcasereg_complete.html', {'result': data})

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

    return render_to_response('casexport_complete.html',{'data': data})

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
    AUTHENTICATE()
    return    render_to_response('help_how_edit_account.html')

#----------------------------------------------------------------------------
def switchboard_toscenario(request):
    '''Scenario-specific leaderboard'''
    AUTHENTICATE_EITHER()
    name = str(request.GET['Scenario_sort'])

    # Gather data
    inputlst = []
    for i in Account.objects.all():
        for j in i.account_models.all():
            scenarioclick = 0
            tests = j.model_tests.all()
            finished_tests = [x for x in tests
                if not x.Active
                and x.test_case.scenario == name]
            N = len(finished_tests)
            if N <= 0:
                # No finished cases
                continue

            # Build case dep. on sample size
            username = i.username
            scores = [float(x.test_rating) for x in finished_tests]
            avg_rating = np.mean(scores)
            entry = [i.institution_name, j.model_nameID,
                     '%5.3f'%avg_rating, N, username]
            if N < 2:
                entry.extend([-1, 1, True])  # std=False, sm.sample=True
            else:
                lowerbound, upperbound = confidence_interval(scores)
                if N < 10:  # small sample=True
                    entry.extend([lowerbound, upperbound, True])
                else: # small sample = False
                    entry.extend([lowerbound, upperbound, False])
            inputlst.append(entry)
            #print >> sys.stderr, entry


    # Sort Data
    # TODO Replace with Simple call!

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
