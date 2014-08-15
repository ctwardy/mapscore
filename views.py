# -*- mode: python; py-indent-offset: 4 -*-
"""
MapScore Main Views File

"""
# Stdlib Imports
import re
import os
import sys
import csv
import math
import time
import random
import shutil
import string
import zipfile
import cStringIO
from operator import itemgetter, attrgetter

# Django Imports
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.core import exceptions
from django.core.mail import send_mail
from django.core.files.move import file_move_safe
from django.core.servers.basehttp import FileWrapper
from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.template import RequestContext

# Other 3rd-party Imports
import numpy as np
from PIL import Image

# Import models and document forms
from mapscore.framework.models import (Account, Test, Case, Model,
    ModelAccountLink, TestModelLink, Mainhits, TerminatedAccounts)
from mapscore.forms import ZipUploadForm


COORDS = '({},{})'
PHOTO_URL_TEMPLATE = '/media/profpic_{}_{}.png'
HEADERS = ['Institution Name', 'Model Name', 'Avg Scenario Rating*',
           'Interval', 'Scenario Tests Completed**']
NOTES = ['*Ranges for N>1 are 95% confidence intervals of the mean.',
         '**Red numbers indicate N<11.']

##################### Media File Locations ################################
MEDIA_DIR = 'media/'  # for the server
USER_GRAYSCALE = 'media/'


def base_redirect(response):
    return redirect('/main/')


def noaccess(request):
    return render_to_response('noaccess.html', {})


def _authenticate(request, token_type):
    if not request.session.get(token_type, False):
        raise PermissionDenied()


def authenticate_user(request):
    _authenticate(request, 'usertoken')


def authenticate_admin(request):
    _authenticate(request, 'admintoken')


def authenticate(request):
    """Authenticates with either 'usertoken' or 'admintoken'."""
    is_admin = request.session.get('admintoken', False)
    is_user = request.session.get('usertoken', False)
    admin_or_user = any((is_admin, is_user))
    if not admin_or_user:
        raise PermissionDenied()


class BadLogin(Exception):

    def __init__(self, error_page, msg):
        self.error_page = error_page
        self.msg = msg


def verify_user(request):
    """Verify user login and return verified account.

    :return: Account object
    :raise BadLogin: if the username/password is not valid or the user is
        attempting to login with a deleted account.

    """
    username = request.POST.get('Username', '')
    password = request.POST.get('Password', '')
    user = auth.authenticate(username=username, password=password)
    if user is None:
        raise BadLogin('IncorrectLogin.html', 'user does not exist')

    # Set user Token
    account = Account.objects.get(ID2=username)
    request.session['usertoken'] = True
    request.session['active_account'] = account

    # record session login
    account.sessionticker = 1 + int(account.sessionticker)
    account.save()
    return account


def main_page(request):

    # record a hit on the main page
    if not Mainhits.objects.all():
        newhits = Mainhits()
        newhits.save()

    mainpagehit = Mainhits.objects.all()[0]
    mainpagehit.hits += 1
    mainpagehit.save()

    request.session['completedtest'] = ''
    request.session['completedtest_lookup'] = False
    request.session['failure'] = False
    request.session['active_case'] = 'none'
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
    score_list = []

    # copy values for leaderboard table
    for model in sorted_models:
        num_finished = sum((not test.Active for test in model.tests.all()))
        if num_finished >= 5:
            score_list.append([
                model.account_set.all()[0].institution_name,
                model.name_id,
                model.avgrating,
                num_finished
            ])

    # Limit to Top-10
    inputdict = {'Scorelist': score_list[:9]}
    inputdict.update(csrf(request))
    return render_to_response('Main.html', inputdict)


def log_out(request):
    request.session['active_account'] = 'none'
    return redirect('/main/')


def account_reg(request):
    return render_to_response('NewAccount.html', {})


def create_account(request):

    # Extract form Data
    Firstname = request.GET['FirstName']
    Lastname = request.GET['LastName']
    Email_in = request.GET['Email']
    Institution = request.GET['Institution']
    Username = request.GET['Username']
    Password1 = request.GET['Password1']
    Password2 = request.GET['Password2']
    Websitein = request.GET['Website']
    captchain = request.GET['captcha']

    # Verify Input

    # Beta Key ************
    actualbetakey = 'sarbayes334$$beta%Test'
    betakey = actualbetakey  # Disable betakey

    Firstname_r = r'^.+$'
    Lastname_r  = r'^.+$'
    Email_in_r  = r'^[a-zA-z0-9\.\-]+@[a-zA-z0-9\-]+[\.a-zA-z0-9\-]+$'
    Institution_r = r"^[a-zA-z\s:0-9']+$"
    Username_r = r'^[a-zA-z0-9_]+$'
    Password1_r = r'^.+$'
    Password2_r = r'^.+$'
    Websitein_r = r'.*$'
    actualcaptcha = 'H4bN'

    # Verify input
    count = 0
    inputdict = {
        'Firstname': Firstname,
        'Lastname': Lastname,
        'Email_in': Email_in,
        'Institution': Institution,
        'Username': Username,
        'Password1': Password1,
        'Password2': Password2,
        'Websitein': Websitein
    }

    if re.match(Firstname_r, Firstname) is None:
        count += 1
        inputdict['firstfail'] = True

    if re.match(Lastname_r, Lastname) is None:
        count += 1
        inputdict['lastfail'] = True

    if re.match(Email_in_r, Email_in) is None:
        count += 1
        inputdict['emailfail'] = True

    if re.match(Institution_r, Institution) is None:
        count += 1
        inputdict['Institutionfail'] = True

    if re.match(Username_r, Username) is None:
        count += 1
        inputdict['usernamefail'] = True

    if captchain != actualcaptcha:
        count += 1
        inputdict['captchafail'] = True

    if betakey == actualbetakey:
        # For Beta Testing
        # don't allow multiple groups to have more than one username
        counter = 0
        for account in Account.objects.all():
            if Username == str(account.username):
                counter += 1

        for terminated_account in TerminatedAccounts.objects.all():
            if Username == str(terminated_account.username):
                counter += 1

        if counter > 0:
            count += 1
            inputdict['usernamerepeat'] = True

    if re.match(Password1_r, Password1) is None:
        count += 1
        inputdict['Pass1fail'] = True

    if re.match(Password2_r, Password2) is None:
        count += 1
        inputdict['Pass2fail'] = True

    if re.match(Websitein_r, Websitein) is None:
        count += 1
        webfail =True
        inputdict['Websitein_r'] = Websitein_r

    if Password1 != Password2:
        count += 1
        inputdict['passsyncfail'] = True

    if count > 0:
        inputdict['fail'] = True
        return render_to_response('NewAccount.html', inputdict)

    # Create User
    user = User.objects.create_user(
        username=Username,
        email=Email_in,
        password=Password1)

    user.is_active = True
    user.save()

    #Create Account
    if Websitein == '':
        Websitein = 'none'

    account = Account(
        institution_name=Institution,
        firstname_user=Firstname,
        lastname_user=Lastname,
        username=Username,
        password =Password1,
        Email=Email_in,
        ID2=Username,
        Website=Websitein)

    # Set up profile pic locations
    account.photourl = PHOTO_URL_TEMPLATE.format(
        account.ID2, account.profpicrefresh)
    account.photolocation = account.photourl[1:]
    account.save()

    # set default profpic
    shutil.copyfile('in_images/Defaultprofpic.png', account.photolocation)

    # Save image size parameters
    img = Image.open(account.photolocation)
    account.photosizex, account.photosizey = img.size
    account.save()

    request.session['active_account'] = account
    return redirect('/uploadprofpic/')


def account_access(request):
    request.session['createcheck'] = False
    request.session['completedtest'] = ''
    request.session['completedtest_lookup'] = False
    request.session['failure'] = False
    request.session['nav'] ='none'
    request.session['inputdic'] = 'none'
    request.session['active_case'] = 'none'
    request.session['active_model'] = 'none'

    if request.session.get('active_account', 'none') != 'none':
        authenticate_user(request)

    try:
        account = verify_user(request)
    except BadLogin as err:
        return render_to_response(err.error_page, {'error_msg': err.msg})

    models = account.account_models.all()
    inputdict = {
        'name': account.fullname,
        'modelname_list': [model.name_id for model in models],
        'profpic': account.photourl,
        'xsize': account.photosizex,
        'ysize': account.photosizey
    }
    return render_to_response('AccountScreen.html', inputdict)


def batch_test_upload(request):
    authenticate(request)

    context_instance = RequestContext(request)
    case_list = []
    update_list = []

    if request.method == 'POST':
        form = ZipUploadForm(request.POST, request.FILES)
        if form.is_valid():
            case_list = form.process_zip_file()
            gc = 0  # good count
            bc = 0  # bad count
            for index, (path, fname, file_size, model, case, status) in enumerate(case_list):
                if status == "ready":
                    active_id = request.session['active_account'].ID2
                    model_id = '{}:{}'.format(active_id, model)
                    model_count = Model.objects.filter(ID2=model_id).count()
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
        form = ZipUploadForm()  # A empty, unbound form

    return render_to_response('batch_test_upload.html', {'form': form},
        context_instance=RequestContext(request)
    )


def batch_test_upload_final(request):
    authenticate(request)

    if request.method != 'POST':
        return render_to_response('AccountScreen.html', {})

    result_data = []

    if not request.session.get("batch_list"):
        result = "Error, contact batch_list session was not found."
        return render_to_response('batch_test_upload_final.html',
            {'result': result, 'result_data': result_data})

    if request.session["batch_list"] == "completed":
        result = "completed"
        return render_to_response('batch_test_upload_final.html',
            {'result': result, 'result_data': result_data})

    if 'abort' in request.POST:
        # User aborted, so delete all the ready temp grayscales
        for index, (path, fname, file_size, model, case, status) in enumerate(request.session.get("batch_list")):
            if status == "ready":
                try:
                    os.remove(path)
                except OSError:
                    pass
        result = "abort"
        return render_to_response('batch_test_upload_final.html', {'result': result,
            'result_data': result_data})

    (result, result_data) = process_batch_tests(request)

    return render_to_response('batch_test_upload_final.html',
        {'result': result, 'result_data': result_data})


def process_batch_tests(request):

    # we need to know what the active account is, store simplify
    act_account = str(request.session['active_account'].ID2)

    tests_list = request.session.get("batch_list")
    result_data = []
    for index, (path, fname, file_size, model, case, status) in enumerate(tests_list):
        if status != "ready":
            continue

        # get active model object
        a_model = Model.objects.get(ID2 = act_account + ":" + str(model))

        # get active case, already verified it exists so skip error check for now
        a_case = Case.objects.get(case_name=str(case))

        # note similar code to below also exists in create_test()

        # set ID2 for this test case "User:Model:Case"
        ID2 = str(a_model.ID2) + ':' + str(a_case.case_name)

        # First check to see if this test already exists
        # and if yes, delete existing one to prevent duplicates
        try:
            findtest = Test.objects.get(ID2=ID2)
        except Test.DoesNotExist:
            findtest = None

        if findtest is not None:  # test exists
            print >>sys.stderr, 'DEBUG: deleting previous test\n'
            print >>sys.stderr, str(findtest.id) + ":" + str(findtest.ID2)

            # delete the test_model_link first
            OldLink = TestModelLink.objects.get(test = findtest.id)
            OldLink.delete()
            findtest.delete()  # delete existing test

        # create new test
        newtest = Test(test_case=a_case,
            test_name=a_case.case_name,
            ID2=ID2)

        Link = TestModelLink(test=newtest, model=a_model)
        Link.save()
        newtest.save()

        # copy grayscale from temp to media for storage
        newtest.grayrefresh += 1

        # not sure why we have to put this in the media directory ?
        # but the single file process does it
        new_grayfile = MEDIA_DIR
        new_grayfile += str(newtest.ID2.replace(':', '_'))
        new_grayfile += '_%d.png' % grayrefresh
        newtest.grayscale_path = new_grayfile
        newtest.save()

        file_move_safe(path, new_grayfile, 65536, True)

        # create string for saving thumbnail 128x128
        thumb = MEDIA_DIR + "thumb_" + str(newtest.ID2).replace(':', '_') + ".png"

        newtest.grayrefresh = int(newtest.grayrefresh) + 1
        s = USER_GRAYSCALE + str(newtest.ID2).replace(':', '_')
        s += '_%s.png' % str(newtest.grayrefresh)

        # Remove served Grayscale image
        file_move_safe(newtest.grayscale_path, s, 65536, True)

        # set the path
        newtest.grayscale_path = s
        newtest.save()

        from PIL import Image
        im = Image.open(s)
        im = im.convert('RGB')
        im.thumbnail((128, 128), Image.ANTIALIAS)
        im.save(thumb, 'PNG')

        # thumbnail is saved in MEDIA_DIR dir with name:
        # save as thumb_User_Model_Case.png
        response = newtest.rate()
        os.unlink(newtest.grayscale_path)

        # record rating
        request.session['active_account'].completedtests = int(request.session['active_account'].completedtests) + 1
        request.session['active_account'].save()
        result_data.append((model, case, newtest.ID2, newtest.test_rating, "ok"))

    request.session['batch_list'] = "completed"
    return (0, result_data)


def model_regform(request):
    authenticate_user(request)
    return render_to_response('NewModel.html', {})


def password_reset(request):
    return render_to_response('PasswordReset.html', {})


def collecting_data(request):
    return render_to_response('CollectingData.html', {})


def email_confirmation(request):
    return render_to_response('email confirmation.html', {})


def emaillink(request):
    length = 7
    chars = string.ascii_letters + string.digits
    random.seed = (os.urandom(1024))
    print ''.join(random.choice(chars) for i in range(length))
    random.random()  # TODO: what's this supposed to be doing?
    return render_to_response('emaillink.html', {})


def model_created(request):
    authenticate_user(request)

    # if page refresh
    if request.session['createcheck'] == True:
        input_dic = {'model_name': str(request.GET['Name'])}
        return render_to_response('ModelRegComplete.html', input_dic)

    # Verify Model Name
    Model_name = str(request.GET['Name'])
    description = str(request.GET['description'])
    ModelName_r = '^[a-zA-z0-9_]+$'
    baddescription = r'^\s*$'

    count = 0
    if re.match(ModelName_r, Model_name) is None:
        count += 1
        inputdict01 = {'namein': Model_name, 'Fail': True, 'description': description}

    if re.match(baddescription, description) is not None:
        count += 1
        inputdict01 = {'namein': Model_name, 'Fail1': True, 'description': description}

    if count == 0:
        for k in request.session['active_account'].account_models.all():
            counter = 0
            if Model_name == str(k.name_id):
                counter += 1

            if counter > 0:
                count += 1
                inputdict01 = {'namein': Model_name, 'modelname': True, 'description': description}

    if count > 0:
        return render_to_response('NewModel.html', inputdict01)

    #Create new model
    new_model = Model(name_id = Model_name,
        ID2 = str(request.session['active_account'].ID2) + ':'+ str(Model_name),
        Description = description)

    new_model.save()

    #Link Model to account
    Link = ModelAccountLink(model=new_model,
        account=request.session['active_account'])
    Link.save()

    request.session['createcheck'] = True
    request.session['model_name'] = Model_name
    request.session['model_in']=  Model_name
    request.session['active_model'] = new_model
    return redirect("/model_menu/")


def model_access(request):
    authenticate_user(request)

    request.session['active_case'] = 'none'
    request.session['createcheck'] = False

    # If not coming from Account
    if request.session['active_model'] != 'none':
        account_name = request.session['active_account'].institution_name
        model_name = request.session['active_model'].name_id
        AllTests = request.session['active_model'].tests.all()

        rating = request.session['active_model'].avgrating
        print rating
        input_dic = {'rating':rating,'Name_act':account_name, 'Name_m':model_name}

        # If incorrect completed test entered
        if request.session['failure']:
            input_dic = {
                'failure': True,
                'rating': rating,
                'Name_act': account_name,
                'Name_m': model_name
            }
            request.session['failure'] = False

        # if returning from completed selection
        if request.session['completedtest_lookup']:
            input_dic['completedtest'] = request.session['completedtest']
            request.session['completedtest_lookup'] = False

        return render_to_response('ModelScreen.html', input_dic)

    # If coming from account
    else:
        selection = request.GET['model_in']
        if selection == '0':
            return redirect('/account/')
        else:
            model_id = '{}:{}'.format(
                request.session['active_account'].ID2, selection)
            request.session['active_model'] = Model.objects.get(ID2=model_id)
            AllTests = request.session['active_model'].tests.all()

            input_dic = {
                'rating': request.session['active_model'].avgrating,
                'Name_act': request.session['active_account'].institution_name,
                'Name_m': request.session['active_model'].name_id
            }

            # If incorrect completed test entered
            if request.session['failure']:
                input_dic['failure'] = True
                request.session['failure'] = False

            return render_to_response('ModelScreen.html', input_dic)


def admin_login(request):
    request.session['Superlogin'] = False
    return render_to_response('AdminLogin.html', csrf(request))


def admin_account(request):
    request.session['userdel'] = ''
    request.session['inputdic'] = 'none'

    if not request.session['Superlogin']:
        username = request.GET['Username']
        password = request.GET['Password']

        # Verify user
        user = auth.authenticate(username=username, password=password)
        if user is None:  # user does not exist
            return render_to_response('IncorrectLogin.html', {})

        if user.is_superuser:
            request.session['admintoken'] = True
            request.session['admin_name'] = username
            request.session['active_account'] ='superuser'
            request.session['Superlogin'] = True
            return render_to_response('AdminScreen.html', {})
        else:
            return render_to_response('IncorrectLogin.html', {})

    elif request.session['Superlogin']:
        authenticate_admin(request)
        request.session['active_account'] = 'superuser'
        return render_to_response('AdminScreen.html', {})


def testcase_admin(request):
    authenticate_admin(request)

    for case in Case.objects.filter(UploadedLayers = False):
        if os.path.exists(str(case.LayerField)):
            case.update(UploadedLayers = True)

    request.session['ActiveAdminCase'] = 'none'
    request.session['inputdic'] = 'none'
    caselist = []

    for case in Case.objects.all():
        latlon_box = ';'.join((
            COORDS.format(case.upright_lat, case.upright_lon),
            COORDS.format(case.downright_lat, case.downright_lon),
            COORDS.format(case.upleft_lat, case.upleft_lon),
            COORDS.format(case.downleft_lat, case.downleft_lon)
        ))
        score_list = [
            case.id,
            case.case_name,
            case.Age,
            case.Sex,
            latlon_box,
            COORDS.format(case.findx, case.findy)
        ]
        caselist.append(score_list)

    return render_to_response('TestCaseMenu.html', {'case_list': caselist})


def Casereg(request):
    authenticate_admin(request)
    inputdict = {}
    inputdict.update(csrf(request))
    return render_to_response('Casereg.html', inputdict)


def tst_instructions(request):
    """Show the instructions for creating images."""
    return render_to_response('tst_instructions.html')


def make_test(model, case):
    ID2 = '{}:{}'.format(model.ID2, case.case_name)
    try:
        findtest = Test.objects.get(ID2=ID2)
    except Test.DoesNotExist:
        findtest = None

    if findtest is not None:
        OldLink = Test_Model_Link.objects.get(test = findtest.id)
        OldLink.delete()
        findtest.delete()

    newtest = Test(test_case=case, test_name=case.case_name, ID2=ID2)
    newtest.save()

    Link = Test_Model_Link(test=newtest, model=model)
    Link.save()

    newtest.save()
    return newtest


def load_image(request):
    authenticate_user(request)

    model = request.session['active_model']
    case = request.session['active_case']
    request.session['tmp_test'] = make_test(model, case)

    # increment counter
    active_test = request.session['tmp_test']
    active_test.grayrefresh += 1

    string = MEDIA_DIR
    string += str(active_test.ID2).replace(':', '_')
    string += '_%d.png' % grayrefresh

    # Save the grayscale file path to the test object
    active_test.grayscale_path = string
    active_test.save()

    with open(string, 'wb+') as destination:
        for chunk in request.FILES['grayscale'].chunks():
            destination.write(chunk)

    return redirect('/confirm_grayscale/')


def confirm_grayscale(request):
    authenticate_user(request)

    served_location = '/{}{}_{}.png'.format(
        MEDIA_DIR,
        str(request.session['tmp_test'].ID2).replace(':','_'),
        str(request.session['tmp_test'].grayrefresh))
    inputdict = {'grayscale': served_location}

    # Verify Image
    # Check dimensions
    image_in = Image.open(request.session['tmp_test'].grayscale_path)
    if image_in.size[0] != 5001 or image_in.size[1] != 5001:
        return render_to_response('uploadfail_demensions.html', inputdict)

    data = image_in.getdata()
    bands = image_in.getbands()

    # Check that it's actually RGB, not grayscale stored as RGB
    if bands[:3] == ('R', 'G', 'B'):  # fail if true RGB
        for i in range(len(data)):
            if not(data[i][0] == data[i][1] == data[i][2]):
                return render_to_response('imageupload_fail.html', inputdict)
        print 'Image OK: grayscale stored as RGB.'
    elif bands[0] in 'LP':  # actual grayscale; review
        print 'actual grayscale'
    else:  # img not grayscale
        return render_to_response('imageupload_fail.html', inputdict)

    return render_to_response('imageupload_confirm.html', inputdict)


def denygrayscale_confirm(request):
    authenticate_user(request)

    # Remove served Grayscale image
    os.remove(request.session['tmp_test'].grayscale_path)

    # Wipe the path
    request.session['tmp_test'].delete()
    request.session['tmp_test'] = 'none'
    return redirect('/model_menu/')


def acceptgrayscale_confirm(request):
    authenticate_user(request)

    # increment counter
    temp_test = request.session['tmp_test']
    temp_test.grayrefresh += 1
    temp_test.save()

    s = USER_GRAYSCALE + temp_test.ID2.replace(':','_')
    s += '_%s.png' % temp_test.grayrefresh
    shutil.move(temp_test.grayscale_path, s)

    # create string for saving thumbnail 128x128
    # thumbnail is saved in USER_GRAYSCALE dir with name:
    # thumb_User_Model_Case.png
    thumb = '{}thumb_{}.png'.format(MEDIA_DIR, temp_test.ID2.replace(':','_'))
    im = Image.open(s)
    im = im.convert('RGB')
    im.thumbnail((128, 128), Image.ANTIALIAS)
    im.save(thumb, 'PNG')

    # set the path
    temp_test.grayscale_path = s
    temp_test.save()
    return redirect('/Rate_Test/')


def Rate(request):
    authenticate_user(request)

    # TODO: unused variable
    response = request.session['tmp_test'].rate()

    # Resync Model
    request.session['active_model'] = Model.objects.get(
            ID2=request.session['active_model'].ID2)
    os.remove(request.session['tmp_test'].grayscale_path)

    # record rating
    request.session['active_account'].completedtests = (1 +
        int(request.session['active_account'].completedtests))
    request.session['active_account'].save()
    return redirect('/submissionreview/')


def show_find_pt(URL2):
    marker_red = URL2.find('markers=color:red')
    marker_yellow = URL2.find('markers=color:yellow')
    end = URL2.find('maptype')
    return (URL2[:marker_red] + URL2[marker_yellow:end] +
            URL2[marker_red:marker_yellow] + URL2[end:])

def case_to_dict(case):
    input_dict = {}
    for attr in dir(case):
        try:
            input_dict[attr] = getattr(case, attr)
        except AttributeError:
            print >> sys.stderr, 'Attribute "%s" not found.' % attr

    input_dict['URLfind'] = show_find_pt(case.URLfind)
    input_dict['LKP'] = COORDS.format(case.lastlat, case.lastlon)
    input_dict['find_pt'] = COORDS.format(case.findlat, case.findlon)
    input_dict['find_grid'] = COORDS.format(case.findx, case.findy)
    input_dict['horcells'] = input_dict['vercells'] = case.sidecellnumber
    input_dict['totalcellnumber'] = int(float(case.totalcellnumber))
    input_dict['cellwidth'] = 5.0
    input_dict['regionwidth'] = (input_dict['cellwidth'] *
            case.sidecellnumber / 1000)
    return input_dict


def submissionreview(request):
    authenticate_user(request)

    active_model = request.session['active_model']
    active_model.completed_cases += 1
    active_model.save()

    active_test = request.session['tmp_test']
    active_case = active_test.test_case
    input_dict = case_to_dict(active_case)
    input_dict['account_name'] = request.session['active_account'].institution_name
    input_dict['model_name'] = active_model.name_id
    input_dict['rating'] = active_test.test_rating

    active_test.save()
    return render_to_response('Submissionreview.html', input_dict)


def nonactive_test(request):
    authenticate(request)

    active_model = request.session['active_model']
    intest_raw = request.GET['Nonactive_Testin']
    intest = intest_raw.strip()
    completed_list = [test.test_name for test in
        active_model.tests.all() if not test.Active]

    #debugx
    print >> sys.stderr, 'DEBUG:\n'
    print >> sys.stderr, intest

    if intest not in completed_list:
        request.session['failure'] = True
        return redirect('/model_menu/')

    active_test = active_model.tests.get(test_name=intest)
    active_case = active_test.test_case
    input_dict = case_to_dict(active_case)
    input_dict['rating'] = str(active_test.test_rating)

    return render_to_response('nonactive_test.html', input_dict)


def get_sorted_models(allmodels):
    """Return list of rated models, highest-rated first.
    Uses avgrating attribute and operator.attrgetter method.

    """
    rated_models = [x for x in allmodels if x.avgrating != 'unrated']
    return sorted(rated_models, key=attrgetter('avgrating'),
                  reverse=True)


def confidence_interval(scores):
    """Return the 95% CI of the mean as (lowerbound, upperbound).

    :type  scores: iterable of float
    :param scores: Relevant scores.

    Because we are trying to infer bounds on the actual
    (population) performance of the model, from limited samples,
    we use +- 1.96 * SEM, the standard error of the mean::

        SEM = stdev / sqrt(N)

    """
    N, avg, stdev = 0, 0.0, 0.0
    try:
        N, avg, stdev = len(scores), np.mean(scores), np.std(scores)
        halfwidth = 1.96*stdev / math.sqrt(N)
        lowerbound = round(np.clip(avg-halfwidth, -1, 1), 4)
        upperbound = round(np.clip(avg+halfwidth, -1, 1), 4)
        return (lowerbound, upperbound)
    except:
        print >> sys.stderr, 'No 95%% CI. N=%d, avg=%6.2f, std=%6.2f' % (N, avg, stdev)
        return (0, 0)


def Leader_model(request):
    """Create the leaderboard."""
    authenticate(request)

    # Build Leaderboard
    score_list = []
    sorted_models = get_sorted_models(Model.objects.all())
    for model in sorted_models:
        # Read info
        account = model.account_set.all()[0]
        institution = account.institution_name
        username = account.username
        name = model.name_id
        rating = float(model.avgrating)
        tests = model.tests.all()
        finished_tests = [test for test in tests if not test.Active]
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
        score_list.append(case)

    # Prepare variables to send to HTML template
    inputdict = {'score_list': score_list}
    if request.session['active_account'] =='superuser':
        inputdict['superuser'] = True

    inputdict['notes'] = NOTES
    inputdict['header_list'] = HEADERS
    inputdict['table'] = 'model_avg'

    request.session['nav'] = '1'
    request.session['inputdic'] = inputdict
    return render_to_response('leaderboard.html', inputdict)


def fetch_model_scores():
    score_list = []
    sorted_models = get_sorted_models(Model.objects.all())
    for model in sorted_models:
        account = model.account_set.all()[0]
        rating = float(model.avgrating)
        tests = model.tests.all()
        finished_tests = [test for test in tests if not test.Active]
        N = len(finished_tests)
        scores = [float(x.test_rating) for x in finished_tests]

        # Build case, depending on sample size
        case = [account.institution_name, model.name_id,
                '%5.3f' % rating, N, account.username]

        if N <= 1:
            case.extend([-1, 1, True])  # std=False, sm.sample=True
        else:
            lowerbound, upperbound = confidence_interval(scores)
            if N < 10:  # small sample=True
                case.extend([lowerbound, upperbound, True])
            else: # small sample = False
                case.extend([lowerbound, upperbound, False])

        score_list.append(case)

    return score_list


def switchboard(request):
    """
    Switchboard table values::

        0: model average table
        1: test case table
        2: scenario table

    """
    authenticate(request)
    sortby = int(request.GET.get('table', 0))
    inputdict = request.session.get('inputdic', {})

    if sortby == 1:
        return redirect('/leaderboard_test_case')
    elif sortby == 2:
        scenario_list = [c.scenario for c in Case.objects.distinct('scenario')]
        inputdict['scenario_list'] = scenario_list
        inputdict['table'] = 'scenario'
        inputdict['score_list'] = fetch_model_scores()
        inputdict['header_list'] = HEADERS
        return render_to_response('leaderboard.html', inputdict)
    else:
        return redirect('/leaderboard_model')


def leaderboard_model(request):
    """Create the leaderboard."""
    authenticate(request)

    # Prepare variables to send to HTML template
    inputdict = {
        'score_list': fetch_model_scores(),
        'table': 'model_avg',
        'header_list': HEADERS,
        'notes': NOTES
    }
    if request.session['active_account'] =='superuser':
        inputdict['superuser'] = True

    request.session['inputdic'] = inputdict
    return render_to_response('leaderboard.html', inputdict)


def leaderboard_test_case(request):
    authenticate(request)

    # check if the given casename is in the database
    raw_casename = request.GET.get('case_name', None)
    if raw_casename is not None:
        casename = raw_casename.replace(' ', '')
        active_cases = Case.objects.filter(case_name=casename)

        if not active_cases:  # entry is invalid
            inputdict = request.session.get('inputdic', {})
            return render_to_response('Leaderboard_Testfail.html', inputdict)

        matched_tests = Test.objects.filter(test_name=casename, Active=False)
    else:
        matched_tests = Test.objects.filter(Active=False)

    # copy values for leaderboard table
    score_list = []
    sorted_tests = matched_tests.order_by('test_rating').reverse()
    for test in sorted_tests[:40]:
        first_model = test.model_set.all()[0]
        first_account = first_model.account_set.all()[0]
        score_list.append([
            first_account.institution_name,
            first_model.name_id,
            test.test_name,
            test.test_rating,
            first_account.username
        ])

    headers = ['Institution Name', 'Model Name', 'Test Name',
               'Avg Test Rating', 'Test Owner']
    inputdict = {
        'score_list': score_list,
        'case_name': raw_casename,
        'table': 'test_case',
        'header_list': headers,
        'notes': NOTES
    }
    if request.session['active_account'] == 'superuser':
        inputdict['superuser'] = True

    request.session['inputdic'] = inputdict
    return render_to_response('leaderboard.html', inputdict)


def leaderboard_scenario(request):
    """Return models with best avg ratings on scenarios of a particular type.

    """
    authenticate(request)

    scenario = request.GET.get('scenario_sort', None)
    if scenario is None:
        return redirect('/switchboard/?table=2')

    input_list = []
    for model in Model.objects.all():
        tests = model.tests.filter(Active=False)
        relevant_tests = [t for t in tests if t.test_case.scenario == scenario]
        is_relevant = any(relevant_tests)
        if is_relevant:
            scores = [float(test.test_rating) for test in tests]
            avg_rating = np.mean(scores)
            account = model.account_set.all()[0]
            N = len(relevant_tests)
            entry = [account.institution_name, model.name_id,
                     '%5.3f' % avg_rating, N, account.username]

            if N < 2:
                entry.extend([-1, 1, True])  # std=False, sm.sample=True
            else:
                lowerbound, upperbound = confidence_interval(scores)
                if N < 10:  # small sample = True
                    entry.extend([lowerbound, upperbound, True])
                else: # small sample = False
                    entry.extend([lowerbound, upperbound, False])

            input_list.append(entry)

    scenario_list = [c.scenario for c in Case.objects.distinct('scenario')]
    scenario_list.remove(scenario)
    inputdict = {
        'scenario': scenario,
        'score_list': input_list,
        'table': 'scenario',
        'header_list': HEADERS,
        'notes': NOTES,
        'scenario_list': scenario_list
    }

    if request.session['active_account'] =='superuser':
        inputdict['superuser'] = True

    request.session['inputdic'] = inputdict
    return render_to_response('leaderboard.html', inputdict)


def testcaseshow(request):
    authenticate(request)

    if request.session['active_account'] == 'superuser':
        all_cases = [case.case_name for case in Case.objects.all()]
        inputdict = {'all_lst': all_cases}
        return render_to_response('case_info_admin.html', inputdict)

    Account = request.session['active_account']

    # construct a list of completed test cases
    completed_list = []
    for i in list(Account.account_models.all()):
        name = 'Model Name: ' + str(i.name_id)
        lst = []
        lst.append(name)
        for j in list(i.tests.all()):
            if not j.Active:
                lst.append(str( j.test_name))

        completed_list.append(lst)

    all_cases = [case.case_name for case in Case.objects.all()]
    inputdict = {'completed_list': completed_list, 'all_lst': all_cases}
    return render_to_response('case_info.html', inputdict)


def return_leader(request):
    authenticate(request)

    inputdict = request.session['inputdic']
    nav_selection = request.session['nav']

    if nav_selection == '1':
        return render_to_response('Leader_Model.html', inputdict)
    elif nav_selection == '2':
        return render_to_response('Leaderboard_testname.html', inputdict)
    elif nav_selection == '3':
        return render_to_response('Leaderboard_test.html', inputdict)
    elif nav_selection == '4':
        return render_to_response('Leaderboard_scenario.html', inputdict)
    elif nav_selection == '5':
        return render_to_response('test_to_scenario.html', inputdict)
    elif nav_selection == '6':
        return render_to_response('leaderboard.html', inputdict)
    elif nav_selection == '7':
        return render_to_response('scenario_to_test.html', inputdict)


def completedtest_info(request):
    authenticate(request)

    completed_list = []
    for case in list(request.session['active_model'].tests.all()):
        if not case.Active:
            thumb = MEDIA_DIR + "thumb_" + str(case.ID2).replace(':','_') + ".png"
            completed_list.append({
                'test_name': case.test_name,
                'test_rating': case.test_rating,
                'thumb': thumb,
                'thumbexists': os.path.isfile(thumb)
            })

    return render_to_response(
        'completedtest_info.html',
        {'completed_list': completed_list})

def case_ref(request):
    authenticate(request)

    Input = request.GET['CaseName2']
    active_case = Case.objects.get(case_name = Input)
    return render_to_response('case_ref.html', case_to_dict(active_case))


def caseref_return(request):
    authenticate(request)

    inputdict = request.session['inputdic']

    nav_choice = request.session['nav']
    if nav_choice == '3':
        return render_to_response('Leaderboard_test.html', inputdict)
    elif nav_choice == '2':
        return render_to_response('Leaderboard_testname.html', inputdict)
    elif nav_choice == '1':
        return render_to_response('Leader_Model.html', inputdict)
    elif nav_choice == '4':
        return render_to_response('Leaderboard_scenario.html', inputdict)
    elif nav_choice == '5':
        return render_to_response('test_to_scenario.html', inputdict)
    elif nav_choice == '6':
        return render_to_response('leaderboard.html', inputdict)
    elif nav_choice == '7':
        return render_to_response('scenario_to_test.html', inputdict)


def Account_Profile(request):
    authenticate(request)

    Account_in = request.GET['Account']
    active_account = Account.objects.get(username=Account_in)

    inputdict = {
        'Name': active_account.institution_name,
        'Email': active_account.Email,
        'RegisteredUser': active_account.fullname,
        'website': active_account.Website,
        'profpic': active_account.photourl,
        'xsize': active_account.photosizex,
        'ysize': active_account.photosizey
    }

    if active_account.Website != 'none':
        inputdict['websitexists'] = True

    # get model descriptions
    model_list = []
    for model in active_account.account_models.all():
        model_list.append([model.name_id, model.description, Account_in])

    inputdict['model_list'] = model_list
    return render_to_response('Account_Profile.html', inputdict)


def returnfrom_profile(request):
    authenticate(request)

    inputdict = request.session['inputdic']

    nav_choice = request.session['nav']
    if nav_choice == '3':
        return render_to_response('Leaderboard_test.html', inputdict)
    elif nav_choice == '2':
        return render_to_response('Leaderboard_testname.html', inputdict)
    elif nav_choice == '1':
        return render_to_response('Leader_Model.html', inputdict)
    elif nav_choice == '4':
        return render_to_response('Leaderboard_scenario.html', inputdict)
    elif nav_choice == '5':
        return render_to_response('test_to_scenario.html', inputdict)
    elif nav_choice == '6':
        return render_to_response('leaderboard.html', inputdict)
    elif nav_choice == '7':
        return render_to_response('scenario_to_test.html', inputdict)


def case_hyperin(request):
    authenticate(request)

    inputdict = request.session['inputdic']
    inputdict['caseselection'] = str(request.GET['casein'])

    nav_choice = request.session['nav']
    if nav_choice == '2':
        return render_to_response('Leaderboard_testname.html', inputdict)
    if nav_choice == '3':
        return render_to_response('Leaderboard_test.html', inputdict)
    if nav_choice == '7':
        return render_to_response('scenario_to_test.html', inputdict)


def upload_casefile(request):
    """Bulk add new cases to the database.
    Should use a CSV file (with quotes for text delimiter), since this is easily
    generated in Excel. The reader is tolerant about use of carriage returns
    (win vs mac vs linux).

    """
    authenticate_admin(request)

    # TODO: Use csv.DictReader here instead
    # use python csv reader, tell it to expect excel style
    # CSV with delimiter: , and quote char as quotes ""
    file = request.FILES['casecsv']
    csv_reader = csv.reader(file.read().splitlines(), dialect=csv.excel_tab,
        delimiter=', ', quotechar='"')
    data = [row for row in csv_reader]

    # If the first line looks like the header, ignore it
    if data[0][0] == 'Name':
        data.pop(0)
    case_report = []

    for row in data:
        new_case = Case(
            case_name=row[0],
            key=row[1],
            country=row[2],
            state=row[3],
            county=row[4],
            populationdensity=row[5],
            weather=row[6],
            subject_category=row[7],
            subject_subcategory=row[8],
            scenario =row[9],
            subject_activity=row[10],
            Age=row[11],
            Sex=row[12],
            number_lost=row[13],
            group_type=row[14],
            ecoregion_domain=row[15],
            ecoregion_division=row[16],
            terrain=row[17],
            lastlat=row[18],
            lastlon=row[19],
            findlat=row[20],
            findlon=row[21],
            total_hours=row[22],
            notify_hours=row[23],
            search_hours=row[24],
            comments=row[25]
        )

        # look and see if this case already exists, ignore it if it does
        # we may need a mechanism for updating an existing case somehow in the
        # future...
        try:
            find_case = Case.objects.get(case_name = new_case.case_name)
            new_case.initialize()
            new_case.save()
            row.append("Success")
        except Case.DoesNotExist:
            row.append("Ignored, name exists")

    return render_to_response('bulkcasereg_complete.html', {'result': data})


def export_case_library(request):
    authenticate_admin(request)

    export_cols = [
        'Name', 'Key#', 'Subject Category', 'Subject Sub-Category', 'Scenario',
        'Subject Activity', 'Age', 'Sex', 'Number Lost', 'Group Type',
        'EcoRegion Domain', 'EcoRegion Division', 'Terrain', 'LKP Coord. (N/S)',
        'LKP Coord. (E/W)', 'Find Coord. (N/S)', 'Fid Coord. (E/W)', 'Total',
        'Hours', 'Notify Hours', 'Search Hours', 'Comments'
    ]

    with open('case_in/exported_case_Library.csv', 'wb') as export_file:
        writer = csv.writer(export_file, delimiter = '|')
        writer.writerow(export_cols)

        for case in Case.objects.all():
            case_export_fields = [
                str(case.case_name), str(case.key), str(case.subject_category),
                str(case.subject_subcategory), str(case.scenario),
                str(case.subject_activity), str(case.Age), str(case.Sex),
                str(case.number_lost), str(case.group_type),
                str(case.ecoregion_domain), str(case.ecoregion_division),
                str(case.terrain), str(case.lastlat), str(case.lastlon),
                str(case.findlat), str(case.findlon), str(case.total_hours),
                str(case.notify_hours), str(case.search_hours),
                str(case.comments)
            ]
            writer.writerow(case_export_fields)

    return render_to_response('casexport_complete.html', {'data': data})


def Manage_Account(request):
    authenticate_user(request)
    request.session['active_model'] = 'none'
    return render_to_response('Account_manage.html')


def edit_user(request):
    authenticate_user(request)

    Account = request.session['active_account']
    Firstname_in = str(Account.firstname_user)
    Lastname_in = str(Account.lastname_user)
    Email_in = str(Account.Email)

    inputdict = {
        'Firstname_in': Account.firstname_user,
        'Lastname_in': Account.lastname_user,
        'Email_in': Account.Email
    }
    return render_to_response('account_useredit.html', inputdict)


def edit_user_run(request):
    authenticate_user(request)

    # read in information
    Account = request.session['active_account']
    Firstname = str(request.GET['FirstName'])
    Lastname = str(request.GET['LastName'])
    Email_in = str(request.GET['Email'])
    Password = str(request.GET['Password'])

    # identify regular expressions
    Firstname_r = r'^.+$'
    Lastname_r  = r'^.+$'
    Email_in_r  = r'^[a-zA-z0-9\.\-]+@[a-zA-z0-9\-]+\.[a-zA-z0-9\-]+$'

    # Verify input
    count = 0
    count2 = 0
    inputdict = {'Firstname': Firstname, 'Lastname': Lastname, 'Email_in': Email_in}
    if re.match(Firstname_r, Firstname) is None:
        count += 1
        inputdict['firstfail'] = True

    if re.match(Lastname_r, Lastname) is None:
        count += 1
        inputdict['lastfail'] = True

    if re.match(Email_in_r, Email_in) is None:
        count += 1
        inputdict['emailfail'] = True

    if Password != str(Account.password):
        count2 = 1
        inputdict['passfail'] = True

    if count > 0:
        inputdict['fail'] = True
        return render_to_response('account_useredit.html', inputdict)

    if count2 == 1:
        inputdict['fail2'] = True
        return render_to_response('account_useredit.html', inputdict)

    # Update Account
    Account.firstname_user = Firstname
    Account.lastname_user = Lastname
    Account.Email = Email_in
    Account.save()
    return render_to_response('account_update_complete.html')


def edit_inst(request):
    authenticate_user(request)

    Account = request.session['active_account']
    Institution_in = str(Account.institution_name)
    Websitein_in = str(Account.Website)

    inputdict = {'Institution_in': Institution_in, 'Websitein_in': Websitein_in}
    return render_to_response('account_editinstitution.html', inputdict)


def edit_inst_run(request):
    authenticate_user(request)

    # read in information
    Account = request.session['active_account']
    Institution = str(request.GET['Institution'])
    Website = str(request.GET['Website'])
    Password = str(request.GET['Password'])

    # identify regular expressions
    Institution_r = r"^[a-zA-z\s:0-9']+$"
    Websitein_r =r'.*$'

    # Verify input
    count = 0
    count2 = 0
    inputdict = {'Institution': Institution, 'Websitein': Website}

    # Match regular expressions --- Perform verification
    if re.match(Institution_r, Institution) is None:
        count += 1
        inputdict['Institutionfail'] = True

    if re.match(Websitein_r, Website) is None:
        count += 1
        webfail = True
        inputdict['Websitein_r'] = Websitein_r

    if Password != str(Account.password):
        count2 = 1
        inputdict['passfail'] = True

    if count > 0:
        inputdict['fail'] = True
        return render_to_response('account_editinstitution.html', inputdict)

    if count2 == 1:
        inputdict['fail2'] = True
        return render_to_response('account_editinstitution.html', inputdict)

    # Update Account
    if Website == '':
        Website = 'none'

    Account.institution_name = Institution
    Account.Website = Website
    Account.save()
    return render_to_response('account_update_complete.html')


def edit_pw(request):
    authenticate_user(request)
    return render_to_response('account_editpw.html')


def edit_pw_run(request):
    authenticate_user(request)

    # read in information
    Account = request.session['active_account']
    Password1 = str(request.GET['Password1'])
    Password2 = str(request.GET['Password2'])
    Password = str(request.GET['Password'])

    # identify regular expressions
    Password1_r ='^.+$'
    Password2_r ='^.+$'

    # Verify input
    count = 0
    count2 = 0
    inputdict = {'Password1': Password1, 'Password2': Password2}

    # Match regular expressions --- Perform verification
    if re.match(Password1_r, Password1) is None:
        count += 1
        inputdict['Pass1fail'] = True

    if re.match(Password2_r, Password2) is None:
        count += 1
        inputdict['Pass2fail'] = True

    if Password != str(Account.password):
        count2 = 1
        inputdict['passfail'] = True

    if Password2 != Password1:
        count2 = 1
        inputdict['passmatchfail'] = True

    if count > 0:
        inputdict['fail'] = True
        return render_to_response('account_editpw.html', inputdict)

    if count2 == 1:
        inputdict['fail2'] = True
        return render_to_response('account_editpw.html', inputdict)

    # Update Account
    Account.password = Password1
    Account.save()

    User_in = User.objects.get(username = str(Account.username))
    User_in.set_password(Password1)
    User_in.save()

    return render_to_response('account_update_complete.html')


def uploadprofpic(request):
    inputdict = {}
    inputdict.update(csrf(request))
    return render_to_response('uploadaccountpic.html', inputdict)


def accountregcomplete(request):
    return render_to_response('RegistrationComplete.html', {})


def confirm_prof_pic(request):
    account = request.session['active_account']
    os.remove(account.photolocation)

    with open(account.photolocation, 'wb+') as destination:
        for chunk in request.FILES['profilephoto'].chunks():
            destination.write(chunk)

    # resize image
    im = Image.open(account.photolocation)
    xsize, ysize = im.size

    if xsize > ysize:
        diffx = xsize - 350
        if diffx > 0:
            totaldiff = diffx
            xpixels = xsize - totaldiff
            percentdiff = float(xpixels)/float(xsize)
            ypixels = int(ysize * percentdiff)
            im = im.resize((xpixels, ypixels) )

    elif xsize < ysize:
        diffy = ysize - 350
        if diffy > 0:
            totaldiff = diffy
            ypixels = ysize - totaldiff
            percentdiff = float(ypixels) / float(ysize)
            xpixels = int(xsize * percentdiff)
            im = im.resize((xpixels, ypixels))

    elif xsize == ysize:
        im = im.resize((350, 350))

    # Remove old picture and increment profile pic refresh counter
    os.remove(account.photolocation)
    account.profpicrefresh = int(account.profpicrefresh) + 1
    account.save()

    # Set up profile pic locations
    account.photourl = PHOTO_URL_TEMPLATE.format(
        account.ID2, account.profpicrefresh)
    account.photolocation = account.photourl[1:]
    account.save()
    im.save(account.photolocation)  # save new profile pic

    # Save image size parameters
    im = Image.open(account.photolocation)
    account.photosizex, account.photosizey = im.size
    account.save()

    inputdict = {
        'account_photo': account.photourl,
        'xsize': account.photosizex,
        'ysize': account.photosizey
    }
    return render_to_response('profpic_confirm.html', inputdict)


def denyprofpic_confirm(request):
    account = request.session['active_account']

    # Remove old picture and increment profile pic refresh counter
    os.remove(account.photolocation)  # remove old picture
    account.profpicrefresh = int(account.profpicrefresh) + 1
    account.save()

    # Set up profile pic locations
    account.photourl = PHOTO_URL_TEMPLATE.format(
        account.ID2, account.profpicrefresh)
    account.photolocation = account.photourl[1:]
    account.save()
    shutil.copyfile('in_images/Defaultprofpic.png', account.photolocation)

    # Save image size parameters
    im = Image.open(account.photolocation)
    account.photosizex, account.photosizey = im.size
    account.save()
    return redirect('/uploadprofpic/')


def confirmprofpic_confirm(request):
    return redirect('/accountregcomplete/')


def edit_picture(request):
    authenticate_user(request)

    account = request.session['active_account']
    inputdict = {
        'account_photo': account.photourl,
        'xsize': account.photosizex,
        'ysize': account.photosizey
    }
    return render_to_response('edit_profpic.html', inputdict)


def remove_profpic(request):
    authenticate_user(request)

    account = request.session['active_account']

    # Remove old picture and increment profile pic refresh counter
    os.remove(account.photolocation)  # remove old picture
    account.profpicrefresh = int(account.profpicrefresh) + 1
    account.save()

    # Set up profile pic locations
    account.photourl = PHOTO_URL_TEMPLATE.format(
        account.ID2, account.profpicrefresh)
    account.photolocation = account.photourl[1:]
    account.save()

    # replace old pic with default
    shutil.copyfile('in_images/Defaultprofpic.png', account.photolocation)

    # Save image size parameters
    im = Image.open(account.photolocation)
    account.photosizex, account.photosizey = im.size
    account.save()
    account.save()
    account.save()
    return redirect('/edit_picture/')


def alterprofpic(request):
    authenticate_user(request)
    inputdict = {}
    inputdict.update(csrf(request))
    return render_to_response('change_accountpic.html', inputdict)


def change_accountpic(request):
    authenticate_user(request)

    account = request.session['active_account']
    os.remove(account.photolocation)

    with open(account.photolocation, 'wb+') as destination:
        for chunk in request.FILES['profilephoto'].chunks():
            destination.write(chunk)

    # resize image
    im = Image.open(account.photolocation)
    xsize, ysize = im.size

    if xsize > ysize:
        diffx = xsize - 350
        if diffx > 0:
            totaldiff = diffx
            xpixels = xsize - totaldiff
            percentdiff = float(xpixels)/float(xsize)
            ypixels = int(ysize * percentdiff)
            im = im.resize((xpixels, ypixels) )

    elif xsize < ysize:
        diffy = ysize - 350
        if diffy > 0:
            totaldiff = diffy
            ypixels = ysize - totaldiff
            percentdiff = float(ypixels)/float(ysize)
            xpixels = int(xsize * percentdiff)
            im = im.resize((xpixels, ypixels))

    elif xsize == ysize:
        im = im.resize((350, 350))

    # remove raw image and increment profile pic request
    os.remove(account.photolocation)
    account.profpicrefresh = int(account.profpicrefresh) + 1
    account.save()

    # Set up profile pic locations
    account.photourl = PHOTO_URL_TEMPLATE.format(
        account.ID2, account.profpicrefresh)
    account.photolocation = account.photourl[1:]
    account.save()
    im.save(account.photolocation)  # save new profile pic

    # Save image size params
    img = Image.open(account.photolocation)
    account.photosizex, account.photosizey = img.size
    account.save()
    return redirect('/edit_picture/')


def traffic(request):
    authenticate_admin(request)

    mainhits = Mainhits.objects.all()[0].hits

    input_list = []
    for i in Account.objects.all():
        tmplst = []
        tmplst.append(str(i.username))
        tmplst.append(str(i.institution_name))
        tmplst.append(str(i.sessionticker))
        tmplst.append(str(len(i.account_models.all())))
        tmplst.append(str(i.deleted_models))
        tmplst.append(str(i.completedtests))
        input_list.append(tmplst)

    deleted_list = []
    for i in TerminatedAccounts.objects.all():
        tmplst = []
        tmplst.append(str(i.username))
        tmplst.append(str(i.institution_name))
        tmplst.append(str(i.sessionticker))
        tmplst.append(str(i.modelsi))
        tmplst.append(str(i.deleted_models))
        tmplst.append(str(i.completedtests))

        deleted_list.append(tmplst)

    inputdict = {
        'mainhits': mainhits,
        'input_list': input_list,
        'deleted_list': deleted_list
    }
    return render_to_response('traffic.html', inputdict)


def delete_account(request):
    authenticate_user(request)
    return render_to_response('Deleteaccount.html')


def deleteaccount_confirm(request):
    authenticate_user(request)

    password = str(request.GET['Password'])
    account = request.session['active_account']

    if password != str(account.password):  # password invalid
        inputdict = {'passfail': True}
        return render_to_response('Deleteaccount.html', inputdict)
    else:  # account to be deleted

        # create new deleted object
        t = TerminatedAccounts()
        t.username = str(account.username)
        t.sessionticker = str(account.sessionticker)
        t.completedtests = str(account.completedtests)
        t.institution_name = str(account.institution_name)
        t.modelsi = str(len(account.account_models.all()))
        t.deleted_models = str(account.deleted_models)
        t.save()

        # Delete Tests / models
        for i in account.account_models.all():
            for j in i.tests.all():
                j.delete()

            # delete all model test links
            for k in TestModelLink.objects.all():
                if str(k.model.ID2) == str(i.ID2):
                    k.delete()

            i.delete()

        # Delete Picture
        os.remove(account.photolocation)

        # Delete model account links
        for i in ModelAccountLink.objects.all():
            if str(i.account.ID2) == str(account.ID2):
                i.delete()

        account.delete()
        return render_to_response('Accountdeleted.html')


def terminate_accounts(request):
    authenticate_admin(request)

    inputdict = {}
    if str(request.session['userdel']) != '':
        username = str(request.session['userdel'])
        inputdict['accountin'] = username
        request.session['userdel'] = ''

    return render_to_response('adminaccountermination.html', inputdict)


def view_username_admin(request):
    authenticate_admin(request)

    score_list = []
    for account in Account.objects.all():
        score_list.append((account.username, account.institution_name))

    inputdict = {'score_list': score_list}
    return render_to_response('account_admin_terminfo.html', inputdict)


def delaccountlink(request):
    authenticate_admin(request)
    user = request.GET['username']
    request.session['userdel'] = user
    return redirect('/terminate_accounts/')


def adminterminate_account(request):
    authenticate_admin(request)

    username = request.GET['account']
    password_in = request.GET['Password']

    failcount = 0
    inputdict = {'accountin': username}
    if auth.authenticate(username=request.session['admin_name'], password=password_in) is None:
        failcount += 1
        inputdict['invalidpw'] = True

    truecount = 0
    for account in Account.objects.all():
        if username == account.username:
            truecount += 1

    if truecount == 0:
        failcount += 1
        inputdict['invalidaccount'] = True

    if  failcount > 0:
        inputdict['Fail'] = True
        return render_to_response('adminaccountermination.html', inputdict)


    # If pass -- proceed with delete
    account = Account.objects.get(username=username)

    # create new deleted object
    t = TerminatedAccounts()
    t.username = str(account.username)
    t.sessionticker = str(account.sessionticker)
    t.completedtests = str(account.completedtests)
    t.institution_name = str(account.institution_name)
    t.modelsi = str(len(account.account_models.all()))
    t.deleted_models = str(account.deleted_models)
    t.save()

    # Delete Tests / models
    for i in account.account_models.all():
        for j in i.tests.all():
            j.delete()

        # delete all model test links
        for k in TestModelLink.objects.all():
            if str(k.model.ID2) == str(i.ID2):
                k.delete()

        i.delete()

    os.remove(account.photolocation)  # delete picture

    # Delete model account links
    for i in ModelAccountLink.objects.all():
        if str(i.account.ID2) == str(account.ID2):
            i.delete()

    account.delete()
    return render_to_response('accountdeleted_admin.html')


def delete_model(request):
    authenticate_user(request)

    model_list = []
    account = request.session['active_account']

    for i in request.session['active_account'].account_models.all():
        model_list.append(i.name_id)

    inputdict = {'modelname_list': model_list}
    return render_to_response('delete_model.html', inputdict)


def deletemodel_confirm(request):
    authenticate_user(request)

    selection = request.GET['model_in']
    if selection == '0':
        return redirect('/delete_model/')

    pw = request.GET['Password']
    if pw != str(request.session['active_account'].password):
        model_list = []
        account = request.session['active_account']

        for i in request.session['active_account'].account_models.all():
            model_list.append(i.name_id)

        inputdict = {'modelname_list': model_list, 'passfail': True}
        return render_to_response('delete_model.html', inputdict)

    # Retrieve active model
    request.session['active_model'] = Model.objects.get(ID2 = str(request.session['active_account'].ID2) + ':' + str(selection))
    model = request.session['active_model']

    # Delete all tests
    for test in model.tests.all():
        test.delete()

    # delete Test Model Links
    for test_model in TestModelLink.objects.all():
        if str(test_model.model.ID2) == str(model.ID2):
            test_model.delete()

    # delete Account Model Links
    for link in ModelAccountLink.objects.all():
        if str(link.model.ID2) == str(model.ID2):
            link.delete()

    model.delete()

    # move along deleted models
    account = request.session['active_account']
    account.deleted_models = int(account.deleted_models) + 1
    account.save()
    return render_to_response('Modeldeleted.html')


def help(request):
    authenticate_user(request)
    return render_to_response('help.html')


def help_how_alter_account(request):
    authenticate_user(request)
    return render_to_response('help_how_edit_account.html')


def password_reset(request):
   return render_to_response('password_reset.html')


def password_email(request):
    User_in = request.GET['Username']
    try:
        Active_account = Account.objects.get(username = User_in)
    except exceptions.ObjectDoesNotExist:
        return render_to_response('password_reset.html')

    # Active_account.Email
    print Active_account.password
    length = 7
    chars = string.ascii_letters + string.digits
    random.seed = (os.urandom(1024))
    Active_account.password = ''.join(random.choice(chars) for i in range(length))
    Active_account.save()
    print Active_account.Email

    try:
       s = 'Your new password is:' + Active_account.password
       send_mail("Temporary MapScore Password", s,
            'mapscore@c4i.gmu.edu', ["Active_account.Email"],
            fail_silently=False)
    except:
       print 'Tried to send this email:', s
       print 'To this account         :', Active_account.Email

    return render_to_response('Password_email.html')


def collecting_data(request):
    return render_to_response('collecting_data.html')


def model_inst_sort(request):
    authenticate(request)

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    avgrating = str(request.GET['avgrating'])
    tstcomplete = str(request.GET['tstcomplete'])
    page = str(request.GET['page'])

    modelname = '0'
    avgrating = '0'
    tstcomplete = '0'

    inputdict = request.session['inputdic']
    scorelist = inputdict['Scorelist']
    caseselection = inputdict.get('caseselection', None)

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
                    count += 1

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
                    count += 1

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
                    count += 1

    sortinfo = [instname, modelname, avgrating, tstcomplete]
    inputdict = {'Scorelist': scorelist, 'sortlst': sortinfo}
    if caseselection is not None:
        inputdict['caseselection'] = caseselection

    request.session['inputdic'] = inputdict

    if page == 'model_leader':
        return render_to_response('Leader_Model.html', inputdict)
    elif page == 'model_to_scenario_move':
        scenario_list = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_list:
                scenario_list.append(str(i.scenario))

        inputdict['scenario_list'] = scenario_list
        request.session['inputdic'] = inputdict
        return render_to_response('leaderboard.html', inputdict)
    elif page == 'model_to_test':
        return render_to_response('Leaderboard_testname.html', inputdict)
    elif page == 'model_to_test_fail':
        return render_to_response('Leaderboard_testname_fail.html', inputdict)


def model_name_sort(request):
    authenticate(request)

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    avgrating = str(request.GET['avgrating'])
    tstcomplete = str(request.GET['tstcomplete'])
    page = str(request.GET['page'])

    instname = '0'
    avgrating = '0'
    tstcomplete = '0'

    inputdict = request.session['inputdic']
    scorelist = inputdict['Scorelist']
    caseselection = inputdict.get('caseselection', None)

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
                    count += 1
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
                    count += 1
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
                    count += 1

    sortinfo = [instname, modelname, avgrating, tstcomplete]
    inputdict = {'Scorelist': scorelist, 'sortlst': sortinfo}
    if caseselection is not None:
        inputdict['caseselection'] = caseselection

    request.session['inputdic'] = inputdict

    if page == 'model_leader':
        return render_to_response('Leader_Model.html', inputdict)
    elif page == 'model_to_scenario_move':
        scenario_list = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_list:
                scenario_list.append(str(i.scenario))

        inputdict['scenario_list'] = scenario_list
        request.session['inputdic'] = inputdict
        return render_to_response('leaderboard.html', inputdict)
    elif page == 'model_to_test':
        return render_to_response('Leaderboard_testname.html', inputdict)
    elif page == 'model_to_test_fail':
        return render_to_response('Leaderboard_testname_fail.html', inputdict)


def model_rtg_sort(request):
    authenticate(request)

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    avgrating = str(request.GET['avgrating'])
    tstcomplete = str(request.GET['tstcomplete'])
    page = str(request.GET['page'])

    modelname = '0'
    instname = '0'
    tstcomplete = '0'

    inputdict = request.session['inputdic']
    scorelist = inputdict['Scorelist']
    caseselection = inputdict.get('caseselection', None)

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
                    count += 1
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
                    count += 1
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
                    count += 1

    sortinfo = [instname, modelname, avgrating, tstcomplete]
    inputdict = {'Scorelist': scorelist, 'sortlst': sortinfo}
    if caseselection is not None:
        inputdict['caseselection'] = caseselection

    request.session['inputdic'] = inputdict

    if page == 'model_leader':
        return render_to_response('Leader_Model.html', inputdict)
    elif page == 'model_to_scenario_move':
        scenario_list = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_list:
                scenario_list.append(str(i.scenario))

        inputdict['scenario_list'] = scenario_list
        request.session['inputdic'] = inputdict
        return render_to_response('leaderboard.html', inputdict)
    elif page == 'model_to_test':
        return render_to_response('Leaderboard_testname.html', inputdict)
    elif page == 'model_to_test_fail':
        return render_to_response('Leaderboard_testname_fail.html', inputdict)


def model_tstscomp_sort(request):
    authenticate(request)

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    avgrating = str(request.GET['avgrating'])
    tstcomplete = str(request.GET['tstcomplete'])
    page = str(request.GET['page'])

    modelname = '0'
    instname = '0'
    avgrating = '0'

    inputdict = request.session['inputdic']
    scorelist = inputdict['Scorelist']
    caseselection = inputdict.get('caseselection', None)

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
                    count += 1
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
                    count += 1
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
                    count += 1

    sortinfo = [instname, modelname, avgrating, tstcomplete]
    inputdict = {'Scorelist': scorelist, 'sortlst': sortinfo}
    if caseselection is not None:
        inputdict['caseselection'] = caseselection

    request.session['inputdic'] = inputdict

    if page == 'model_leader':
        return render_to_response('Leader_Model.html', inputdict)
    elif page == 'model_to_scenario_move':
        scenario_list = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_list:
                scenario_list.append(str(i.scenario))

        inputdict['scenario_list'] = scenario_list
        request.session['inputdic'] = inputdict
        return render_to_response('leaderboard.html', inputdict)
    elif page == 'model_to_test':
        return render_to_response('Leaderboard_testname.html', inputdict)
    elif page == 'model_to_test_fail':
        return render_to_response('Leaderboard_testname_fail.html', inputdict)


def test_inst_sort(request):
    authenticate(request)

    # extract data
    instname = int(request.GET['instname'])
    modelname = int(request.GET['modelname'])
    testname = int(request.GET['testname'])
    tstrating = int(request.GET['tstrating'])
    page = str(request.GET['page'])

    inputdict = request.session['inputdic']
    scorelist = inputdict['Scorelist']
    casename = inputdict['casename']
    caseselection = inputdict.get('caseselection', None)

    table_values = []
    for row in scorelist:
        table_values.append({
            'institution': row[0],
            'model_name': row[1],
            'test_name': row[2],
            'test_rating': row[3],
            'user': row[4]
        })

    if instname:
        sortby= 'institution'
    elif modelname:
        sortby = 'model_name'
    elif testname:
        sortby = 'test_name'
    else:
        sortby = 'test_rating'

    score_list = sorted(table_values, key=lambda row: row[sortby])
    sortinfo = [instname, modelname, testname, tstrating]
    inputdict = {'Scorelist': scorelist, 'sortlst': sortinfo}
    inputdict['casename'] = casename
    if caseselection is not None:
        inputdict['caseselection'] = caseselection

    request.session['inputdic'] = inputdict

    if page == 'test_leader':
        return render_to_response('Leaderboard_test.html', inputdict)
    elif page =='test_leader_fail':
        return render_to_response('Leaderboard_Testfail.html', inputdict)
    elif page =='TEST_TOSCENARIO_MOVE':
        scenario_list = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_list:
                scenario_list.append(str(i.scenario))

        inputdict['scenario_list'] = scenario_list
        request.session['inputdic'] = inputdict
        return render_to_response('test_to_scenario.html', inputdict)


def sort_table(request):
    """Sort the leaderboard table by a chosen column."""

    # extract sorting flags
    instname = int(request.GET['instname'])
    modelname = int(request.GET['modelname'])
    testname = int(request.GET['testname'])
    tstrating = int(request.GET['tstrating'])

    # preserve input values for return and grab table data
    inputdict = request.session['inputdic']
    casename = inputdict['casename']
    caseselection = inputdict.get('caseselection', None)
    scorelist = inputdict['Scorelist']

    # # put table data into a dictionary for ease of sorting
    # table_values = []
    # for row in scorelist:
    #     table_values.append({
    #         'institution': row[0],
    #         'model_name': row[1],
    #         'test_name': row[2],
    #         'test_rating': row[3],
    #         'user': row[4]
    #     })
    # score_list = sorted(table_values, key=lambda row: row[sortby])

    if instname:
        sortby = 0
    elif modelname:
        sortby = 1
    elif testname:
        sortby = 2
    else:
        sortby = 3

    scorelist = sorted(scorelist, key=lambda row: row[sortby])
    sortinfo = [instname, modelname, testname, tstrating]
    inputdict = {'Scorelist': scorelist, 'sortlst': sortinfo}
    inputdict['casename'] = casename
    if caseselection is not None:
        inputdict['caseselection'] = caseselection

    request.session['inputdic'] = inputdict
    return inputdict


def test_modelname_sort(request):
    authenticate(request)

    inputdict = sort_table(request)

    page = request.GET['page']
    if page == 'test_leader':
        return render_to_response('Leaderboard_test.html', inputdict)
    elif page =='test_leader_fail':
        return render_to_response('Leaderboard_Testfail.html', inputdict)
    elif page =='TEST_TOSCENARIO_MOVE':
        scenario_list = []
        for case in Case.objects.all():
            if case.scenario not in scenario_list:
                scenario_list.append(case.scenario)

        inputdict['scenario_list'] = scenario_list
        request.session['inputdic'] = inputdict
        return render_to_response('test_to_scenario.html', inputdict)


def test_name_sort(request):
    authenticate(request)

    inputdict = sort_table(request)

    if page == 'test_leader':
        return render_to_response('Leaderboard_test.html', inputdict)
    elif page =='test_leader_fail':
        return render_to_response('Leaderboard_Testfail.html', inputdict)
    elif page =='TEST_TOSCENARIO_MOVE':
        scenario_list = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_list:
                scenario_list.append(str(i.scenario))

        inputdict['scenario_list'] = scenario_list
        request.session['inputdic'] = inputdict
        return render_to_response('test_to_scenario.html', inputdict)


def test_rating_sort(request):
    authenticate(request)

    inputdict = sort_table(request)

    if page == 'test_leader':
        return render_to_response('Leaderboard_test.html', inputdict)
    elif page =='test_leader_fail':
        return render_to_response('Leaderboard_Testfail.html', inputdict)
    elif page =='TEST_TOSCENARIO_MOVE':
        scenario_list = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_list:
                scenario_list.append(str(i.scenario))

        inputdict['scenario_list'] = scenario_list
        request.session['inputdic'] = inputdict
        return render_to_response('test_to_scenario.html', inputdict)


def cat_inst_sort(request):
    authenticate(request)

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    catrating = str(request.GET['catrating'])
    catcompleted = str(request.GET['catcompleted'])
    page = str(request.GET['page'])

    modelname = '0'
    catrating = '0'
    catcompleted = '0'

    inputdict = request.session['inputdic']
    scorelist = inputdict['input_list']
    name = inputdict['scenario']
    caseselection = inputdict.get('caseselection', None)

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
                    count += 1
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
                    count += 1
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
                    count += 1

    sortinfo = [instname, modelname, catrating, catcompleted]
    inputdict = {'input_list': scorelist, 'sortlst': sortinfo}
    if caseselection is not None:
        inputdict['caseselection'] = caseselection

    request.session['inputdic'] = inputdict

    if page == 'category_leader':
        scenario_list = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_list:
                scenario_list.append(str(i.scenario))

        inputdict['scenario_list'] = scenario_list
        inputdict['scenario'] = name
        request.session['inputdic'] = inputdict
        return render_to_response('Leaderboard_scenario.html', inputdict)

    elif page == 'scenario_to_test':
        inputdict['scenario'] = name
        request.session['inputdic'] = inputdict
        return render_to_response('scenario_to_test.html', inputdict)

    elif page =='scenario_to_test_fail':
        inputdict['scenario'] = name
        request.session['inputdic'] = inputdict
        return render_to_response('scenario_to_testfail.html', inputdict)


def cat_modelname_sort(request):
    authenticate(request)

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    catrating = str(request.GET['catrating'])
    catcompleted = str(request.GET['catcompleted'])
    page = str(request.GET['page'])

    instname = '0'
    catrating = '0'
    catcompleted = '0'

    inputdict = request.session['inputdic']
    scorelist = inputdict['input_list']
    name = inputdict['scenario']
    caseselection = inputdict.get('caseselection', None)

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
                    count += 1
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
                    count += 1
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
                    count += 1

    sortinfo = [instname, modelname, catrating, catcompleted]
    inputdict = {'input_list': scorelist, 'sortlst': sortinfo}
    if caseselection is not None:
        inputdict['caseselection'] = caseselection

    request.session['inputdic'] = inputdict

    if page == 'category_leader':
        scenario_list = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_list:
                scenario_list.append(str(i.scenario))

        inputdict['scenario_list'] = scenario_list
        inputdict['scenario'] = name
        request.session['inputdic'] = inputdict
        return render_to_response('Leaderboard_scenario.html', inputdict)

    elif page == 'scenario_to_test':
        inputdict['scenario'] = name
        request.session['inputdic'] = inputdict
        return render_to_response('scenario_to_test.html', inputdict)

    elif page =='scenario_to_test_fail':
        inputdict['scenario'] = name
        request.session['inputdic'] = inputdict
        return render_to_response('scenario_to_testfail.html', inputdict)


def catrating_sort(request):
    authenticate(request)

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    catrating = str(request.GET['catrating'])
    catcompleted = str(request.GET['catcompleted'])
    page = str(request.GET['page'])

    instname = '0'
    modelname = '0'
    catcompleted = '0'

    inputdict = request.session['inputdic']
    scorelist = inputdict['input_list']
    name = inputdict['scenario']
    caseselection = inputdict.get('caseselection', None)

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
                    count += 1
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
                    count += 1
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
                    count += 1

    sortinfo = [instname, modelname, catrating, catcompleted]
    inputdict = {'input_list': scorelist, 'sortlst': sortinfo}
    if caseselection is not None:
        inputdict['caseselection'] = caseselection

    request.session['inputdic'] = inputdict

    if page == 'category_leader':
        scenario_list = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_list:
                scenario_list.append(str(i.scenario))

        inputdict['scenario_list'] = scenario_list
        inputdict['scenario'] = name
        request.session['inputdic'] = inputdict
        return render_to_response('Leaderboard_scenario.html', inputdict)

    elif page == 'scenario_to_test':
        inputdict['scenario'] = name
        request.session['inputdic'] = inputdict
        return render_to_response('scenario_to_test.html', inputdict)

    elif page =='scenario_to_test_fail':
        inputdict['scenario'] = name
        request.session['inputdic'] = inputdict
        return render_to_response('scenario_to_testfail.html', inputdict)


def catcompleted_sort(request):
    authenticate(request)

    # extract data
    instname = str(request.GET['instname'])
    modelname = str(request.GET['modelname'])
    catrating = str(request.GET['catrating'])
    catcompleted = str(request.GET['catcompleted'])
    page = str(request.GET['page'])

    instname = catrating = modelname = '0'
    inputdict = request.session['inputdic']
    scorelist = inputdict['input_list']
    name = inputdict['scenario']
    caseselection = inputdict.get('caseselection', None)

    # sort depending on various circumstances
    if catcompleted == '0':
        catcompleted = '1'
        count = 1
        temp = ''

        while count > 0:
            count = 0
            for i in range(len(scorelist)-1):
                temp = ''
                if float(scorelist[i][3]) < float(scorelist[i+1][3]):
                    temp = scorelist[i]
                    scorelist[i] = scorelist[i+1]
                    scorelist[i+1] = temp
                    count += 1
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
                    count += 1
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
                    count += 1

    sortinfo = [instname, modelname, catrating, catcompleted]
    inputdict = {'input_list': scorelist, 'sortlst': sortinfo}
    if caseselection is not None:
        inputdict['caseselection'] = caseselection

    request.session['inputdic'] = inputdict

    if page == 'category_leader':
        scenario_list = []
        for i in Case.objects.all():
            if str(i.scenario) not in  scenario_list:
                scenario_list.append(str(i.scenario))

        inputdict['scenario_list'] = scenario_list
        inputdict['scenario'] = name
        request.session['inputdic'] = inputdict
        return render_to_response('Leaderboard_scenario.html', inputdict)

    elif page == 'scenario_to_test':
        inputdict['scenario'] = name
        request.session['inputdic'] = inputdict
        return render_to_response('scenario_to_test.html', inputdict)

    elif page =='scenario_to_test_fail':
        inputdict['scenario'] = name
        request.session['inputdic'] = inputdict
        return render_to_response('scenario_to_testfail.html', inputdict)


def model_edit_info(request):
    authenticate_user(request)

    inputdict = {
        'description': str(request.session['active_model'].description),
        'model_name': request.session['active_model'].name_id
    }
    return render_to_response('edit_model_info.html', inputdict)


def model_change_info(request):
    authenticate_user(request)

    pw = str(request.GET['Password'])
    des = str(request.GET['description'])
    name = request.session['active_model'].name_id
    account = request.session['active_account']
    model = request.session['active_model']
    password = str(account.password)

    inputdict = {
        'description': des,
        'model_name': name
    }

    count = 0
    if pw != password:
        count += 1
        inputdict['passfail'] = True

    baddescription = r'^\s*$'

    if re.match(baddescription, des) is not None:
        count += 1
        inputdict['Fail1'] = True

    if count > 0:
        return render_to_response('edit_model_info.html', inputdict)

    # If everything works out
    model.description = des
    model.save()
    return render_to_response('model_info_updated.html')


def model_Profile(request):
    authenticate(request)

    try:
        active_account = Account.objects.get(
            username=request.GET['Account'])
    except Account.DoesNotExist:
        # TODO: redirect somewhere better
        return redirect('/main/')

    try:
        active_model = active_account.account_models.get(
            name_id=request.GET['Model'])
    except Model.DoesNotExist:
        # TODO: redirect somewhere better
        return redirect('/main/')

    model_dict = {
        'Name': active_model.name_id,
        'Accountname': active_account.institution_name,
        'Description': active_model.description,
        'username': active_account.username
    }
    return render_to_response('model_Profile.html', model_dict)


def metric_description(request):
    authenticate_user(request)
    return render_to_response('metric_description.html')


def metric_description_nonactive(request):
    authenticate_user(request)
    return render_to_response('metric_description_nonactive.html')


def metric_description_submissionreview(request):
    authenticate_user(request)
    return render_to_response('metric_description_submissionreview.html')


def reg_conditions(request):
    return render_to_response('regconditions.html')


def download_param(request):
    authenticate_user(request)

    active_case = request.session['active_case']

    instring = "Case_Name: " + active_case.case_name + '\r\n'
    instring = instring + "Coordinate_System: WGS_84" + '\r\n'
    instring = instring + "Subject_Age: " +  active_case.Age + '\r\n'
    instring = instring + "Subject_Gender: " + active_case.Sex + '\r\n'
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
    instring = instring + "Last_Known_Position: " + '('+active_case.lastlat + ', ' +active_case.lastlon + ')'  + '\r\n'
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
    #image.save(resp, 'png')
    resp.write(instring)
    return resp


def upload_layers(request):
    authenticate_admin(request)

    request.session['ActiveAdminCase'] = int(request.GET['id'])
    admincase = Case.objects.get(id = request.session['ActiveAdminCase'])

    inputdict = {}
    inputdict['id'] = request.session['ActiveAdminCase']
    inputdict['Name'] =  admincase.case_name
    inputdict.update(csrf(request))
    inputdict['layersexist'] = True if admincase.UploadedLayers else False
    return render_to_response('UploadLayersMenu.html', inputdict)


def upload_Layerfile(request):
    authenticate_admin(request)

    # Take in file - save to server
    admincase = Case.objects.get(id = request.session['ActiveAdminCase'])
    string = str(admincase.LayerField)

    if admincase.UploadedLayers == True:
        stream = "Layers/" + str(admincase.id) +'_' + str(admincase.case_name)
        os.remove(string)
        shutil.rmtree(stream)
        admincase.UploadedLayers = False
        admincase.save()

    with open(string, 'wb+') as destination:
        for chunk in request.FILES['caselayer'].chunks():
            destination.write(chunk)

    admincase.UploadedLayers = True
    admincase.save()

    zippin = zipfile.ZipFile(string, 'r')
    stream = "Layers/" + str(admincase.id) +'_' + str(admincase.case_name)
    zippin.extractall(stream)

    return render_to_response('CaseLayersComplete.html')


def DownloadLayers(request):
    authenticate_user(request)

    active_test = request.session['tmp_test']
    active_case = active_test.test_case
    string = str(active_case.LayerField)
    zippin = zipfile.ZipFile(string, 'r')
    zippinlst = zippin.namelist()
    zippin.close()
    buff = cStringIO.StringIO()
    zippin2 = zipfile.ZipFile(buff, 'w', zipfile.ZIP_DEFLATED)

    for name in zippinlst:
        stream = "Layers/" + str(active_case.id) +'_' + str(active_case.case_name) + "/" + name
        for i in range(len(name)-1):
            if name[i] == '/':
                term = i
                break

        name2 = name[term+1: len(name)]
        if not stream[len(stream)-1] == '/':
            filein = open(stream, 'rb')
            zippin2.writestr(name2, filein.read())

    zippin2.close()
    buff.flush()
    writeinfo = buff.getvalue()
    buff.close()

    resp = HttpResponse( content_type = 'application/zip')
    resp['Content-Disposition'] = 'attachment; filename= Layers.zip'
    resp.write(writeinfo)
    return resp


def delete_Layers(request):
    authenticate_admin(request)

    # Take in file - save to server
    admincase = Case.objects.get(id = request.session['ActiveAdminCase'])
    string = str(admincase.LayerField)
    stream = "Layers/" + str(admincase.id) +'_' + str(admincase.case_name)
    os.remove(string)
    shutil.rmtree(stream)

    admincase.UploadedLayers = False
    admincase.save()
    return redirect("/admin_cases/")


def DownloadLayersadmin(request):
    authenticate_admin(request)

    active_case = Case.objects.get(id=request.session['ActiveAdminCase'])

    string = str(active_case.LayerField)
    zippin = zipfile.ZipFile(string, 'r')
    zippinlst = zippin.namelist()
    zippin.close()
    buff = cStringIO.StringIO()
    zippin2 = zipfile.ZipFile(buff, 'w', zipfile.ZIP_DEFLATED)

    for name in zippinlst:
        stream = ("Layers/" + str(active_case.id) +'_' +
                  str(active_case.case_name) + "/" + name)
        for i in range(len(name)-1):
            if name[i] == '/':
                term = i
                break

        name2 = name[term+1: len(name)]

        if not stream[len(stream)-1] == '/':
            filein = open(stream, 'rb')
            zippin2.writestr(name2, filein.read())

    zippin2.close()
    buff.flush()
    writeinfo = buff.getvalue()
    buff.close()

    resp = HttpResponse(content_type='application/zip')
    resp['Content-Disposition'] = 'attachment; filename= Layers.zip'
    resp.write(writeinfo)
    return resp


def casetypeselect(request):
    authenticate_user(request)
    name_lst = sorted(set([str(x.case_name) for x in Case.objects.all()]))
    type_lst = sorted(set([str(x.subject_category) for x in Case.objects.all()]))
    return render_to_response('Testselect.html', {'names': name_lst, 'types': type_lst})


def TesttypeSwitch(request):
    authenticate_user(request)

    selection = request.GET['typein2']
    if selection == '0':
        return redirect("/casetypeselect/")

    for case in Case.objects.all():
        if (case.subject_category == selection
            and case not in request.session['active_model'].tests.all()):
            request.session['active_case'] = case
            return redirect('/test/')
    return render_to_response('nomorecases.html', {'selection' : selection})


def TestNameSwitch(request):
    authenticate_user(request)

    selection = request.GET['casename']
    if selection == '0':
        return redirect('/casetypeselect/')

    try:
        request.session['active_case'] = Case.objects.get(case_name=selection)
        return redirect('/test/')
    except Case.DoesNotExist:
        return render_to_response('nomorecasestype.html', {'selection': selection})
    else:  # multiple cases found; pick the first
        cases = Case.objects.filter(case_name = selection)
        request.session['active_case'] = cases[0]
        return redirect("/test/")


def next_sequential_test_switch(request):
    authenticate_user(request)

    tests = request.session['active_model'].tests.all()
    tested_cases = [test.test_case for test in tests]
    for case in Case.objects.all():
        if case not in tested_cases:
            request.session['active_case'] = case
            return redirect('/test/')
    return render_to_response('nomorecases.html')


def test(request):
    authenticate(request)

    active_case = request.session['active_case']
    if isinstance(active_case, basestring):
        print >> sys.stderr, 'An active case has not been selected yet.'
        return redirect('/main/')

    input_dict = case_to_dict(active_case)
    input_dict.update(csrf(request))
    return render_to_response('file_up.html', input_dict)
