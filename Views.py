# Main Views File 

# Import statements
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import redirect
import random
import shutil

# Import Models

from framework.models import Account
from framework.models import Test
from framework.models import Case
from framework.models import Model
from framework.models import Model_Account_Link
from framework.models import Test_Model_Link
from framework.models import Mainhits
from framework.models import terminated_accounts

import time
import re
import os
#from PIL import Image
import Image

from django.core.context_processors import csrf

#--------------------------------------------------------------
def base_redirect(response):
	return redirect('/main/')



#-------------------------------------------------------------
def main_page(request):

	# record a hit on the main page
	#----------------------------------------------------
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

	sorted_models = []
	allmodels = Model.objects.all()

	# Sorting Algorithm largest -- smallest

	for i in allmodels:
		if i.model_avgrating != 'unrated':
			sorted_models.append(i)

	#Bubblesort
	alterations = 1
	while alterations > 0:

		tmplist =['']
		alterations = 0
		for i in range(len(sorted_models)-1):
			if float(sorted_models[i].model_avgrating) < float(sorted_models[i+1].model_avgrating):
				tmplist[0] = sorted_models[i]
				sorted_models[i] = sorted_models[i+1]
				sorted_models[i+1] =  tmplist[0]
				alterations = alterations + 1


	# copy values for leaderboard table
	inputlist = []
	sublist = []
	for i in range(len(sorted_models)):
		sublist = []
		institution = str(sorted_models[i].account_set.all()[0].institution_name)
		model = str(sorted_models[i].model_nameID)
		rating = str(sorted_models[i].model_avgrating)

		tests = sorted_models[i].model_tests.all()

		count = 0
		for n in tests:
			if n.Active == False:
				count = count + 1

		numbertests = count

		sublist.append(institution)
		sublist.append(model)
		sublist.append(rating)
		sublist.append(numbertests)

		inputlist.append(sublist)


		if len(inputlist) >5:
			inputlist = inputlist[0:4]

	inputdic ={'Scorelist':inputlist}	


	return render_to_response('Main.html',inputdic)
#-------------------------------------------------------------	



#-------------------------------------------------------------
def account_reg(request):

	return render_to_response('NewAccount.html',{})
#-------------------------------------------------------------	



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
	betakey = str(request.GET['Betakey'])
	
	#Verify Input
	
	# Beta Key ************
	actualbetakey = 'sarbayes334$$beta%Test'
	
	Firstname_r = '^.+$'
	Lastname_r  = '^.+$'
	Email_in_r  = '^[a-zA-z0-9\.]+@[a-zA-z0-9]+\.[a-zA-z0-9]+$'
	Institution_r = "^[a-zA-z\s:0-9']+$"
	Username_r = '^[a-zA-z0-9_]+$'
	Password1_r ='^.+$'
	Password2_r ='^.+$'
	Websitein_r ='.*$'   


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
	
	if betakey != actualbetakey:
		count = count + 1
		betafail = True
		inputdic['betafail'] = betafail
	
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
		return 	render_to_response('NewAccount.html',inputdic)




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
			completedtests = 0

				)
	account.save()





	# Set up profile pic locations

	ID2 = account.ID2
	stringurl = '/media/profpic_'
	stringurl = stringurl + str(ID2) + '.png'
	account.photourl = stringurl


	stringlocation = 'media/profpic_' + str(ID2) + '.png'
	#'C:\Users\Nathan Jones\Django Website\MapRateWeb\media\profpic_' + str(ID2) + '.png'
	account.photolocation = stringlocation


	account.save()

	# set default profpic
	#shutil.copyfile('C:\Users\Nathan Jones\Django Website\MapRateWeb\in_images\Defaultprofpic.png',stringlocation)
	shutil.copyfile('in_images/Defaultprofpic.png',stringlocation)

	request.session['active_account'] =  account	
	return redirect('/uploadprofpic/')
#-------------------------------------------------------------

def account_access(request):


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
			#--------------------------------------------------------------------------------------
			request.session['active_account'].sessionticker = int(request.session['active_account'].sessionticker) + 1
			request.session['active_account'].save()
			#--------------------------------------------------------------------------------------


			for i in request.session['active_account'].account_models.all():
				model_list.append(i.model_nameID)

			profpic = request.session['active_account'].photourl


			return render_to_response('AccountScreen.html',{'Name':request.session['active_account'].institution_name,'modelname_list':model_list ,'profpic':profpic})

		# User does not exist
		else:

			return render_to_response('IncorrectLogin.html',{})
	else:
		#------------------------------------------------------------------
		# Token Verification
		try:
			if request.session['usertoken'] == False:
				return render_to_response('noaccess.html',{})
		except: 
			return render_to_response('noaccess.html',{})

		#---------------------------------------------------------------------
		model_list = []
		for i in request.session['active_account'].account_models.all():
			model_list.append(i.model_nameID)

		profpic = request.session['active_account'].photourl

		return render_to_response('AccountScreen.html',{'Name':request.session['active_account'].institution_name,'modelname_list':model_list,'profpic':profpic })

#-----------------------------------------------------------------
def model_regform(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------


	return render_to_response('NewModel.html',{})

#-------------------------------------------------------------------

def model_created(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	# Verify Model Name

	Model_name = str(request.GET['Name'])
	ModelName_r = '^[a-zA-z0-9_]+$'

	count = 0
	if re.match(ModelName_r,Model_name) == None:
		count = count + 1
		inputdic01 ={'namein': Model_name,'Fail':True}

	else:
		for k in request.session['active_account'].account_models.all():
			counter = 0
			if Model_name == str(k.model_nameID):
				counter = counter + 1

			if counter > 0:
				count = count + 1
				inputdic01 = {'namein': Model_name,'modelnamerepeat': True}



	if count > 0:	


		return render_to_response('NewModel.html',inputdic01)






	#Create new model

	new_model = Model(model_nameID = Model_name,
		ID2 = str(request.session['active_account'].ID2) + ':'+ str(Model_name))
	new_model.setup()
	new_model.save()

	#Link Model to account

	Link = Model_Account_Link(	model = new_model,
					account = request.session['active_account'])

	Link.save()

	return render_to_response('ModelRegComplete.html',{})

#-------------------------------------------------------------------	

def model_access(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	request.session['active_case_temp'] = 'none'
	request.session['active_test'] = 'none'


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

#---------------------------------------------------------------------
def admin_login(request):

	request.session['Superlogin'] = False
	return render_to_response('AdminLogin.html')
#--------------------------------------------------------------------

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

		#------------------------------------------------------------------
		# Token Verification
		try:
			if request.session['admintoken'] == False:
				return render_to_response('noaccess.html',{})
		except: 
			return render_to_response('noaccess.html',{})

		#---------------------------------------------------------------------

		request.session['active_account'] ='superuser'
		return render_to_response('AdminScreen.html',{})

#--------------------------------------------------------------------------
def testcase_admin(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------


	request.session['inputdic'] = 'none'
	caselist = []

	for i in Case.objects.all():
		inputlist = []
		inputlist.append(i.case_name)
		inputlist.append(i.id)
		inputlist.append(i.Age)
		inputlist.append(i.Sex)
		inputlist.append('(' + str(i.lastlat) + ',' + str(i.lastlon ) + ')')
		inputlist.append('(' + str(i.findlat ) + ',' + str(i.findlon ) + ')')
		inputlist.append('(' + str(i.upright_lat  ) + ',' + str(i.upright_lon ) + ');'+'(' + str(i.downright_lat) + ',' + str(i.downright_lon ) + ');'+'(' + str(i.upleft_lat) + ',' + str(i.upleft_lon ) + ');'+'(' + str(i.downleft_lat ) + ',' + str(i.downleft_lon) + ')')
		inputlist.append('(' + str(i.findx) + ',' + str(i.findy ) + ')')
		caselist.append(inputlist)




	return render_to_response('TestCaseMenu.html',{'case_list':caselist})

#----------------------------------------------------------------------------
def Casereg(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	inputdic = {}
	inputdic.update(csrf(request))
	return render_to_response('Casereg.html',inputdic)


#-----------------------------------------------------------------------------

def newtest(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	# If all tests completed
	count2 = 0
	for i in request.session['active_model'].model_tests.all():
		if i.Active == False:
			count2 = count2 +1

	if int(count2) == int(len(Case.objects.all())):

		return render_to_response('nomorecases.html')

	# only one active test at a time
	count001 = 0
	for i in request.session['active_model'].model_tests.all():
		if i.Active == True:
			count001 = count001 +1
	if count001 >0:
		return render_to_response('TestWelcome_alreadyactive.html')




	id_in = int(request.session['active_model'].Completed_cases) +1
	request.session['active_case_temp'] = Case.objects.get(id = id_in)

	age = request.session['active_case_temp'].Age
	name = request.session['active_case_temp'].case_name
	sex = request.session['active_case_temp'].Sex
	LKP = '('+request.session['active_case_temp'].lastlat + ',' +request.session['active_case_temp'].lastlon + ')' 
	totalcells = request.session['active_case_temp'].totalcellnumber
	sidecells = request.session['active_case_temp'].sidecellnumber
	upright = '('+request.session['active_case_temp'].upright_lat  + ',' +request.session['active_case_temp'].upright_lon + ')'
	downleft = '('+request.session['active_case_temp'].downleft_lat  + ',' +request.session['active_case_temp'].downleft_lon + ')'
	downright = '('+request.session['active_case_temp'].downright_lat  + ',' +request.session['active_case_temp'].downright_lon + ')'
	upleft = '('+request.session['active_case_temp'].upleft_lat  + ',' +request.session['active_case_temp'].upleft_lon + ')'

	account_name = request.session['active_account'].institution_name
	model_name = request.session['active_model'].model_nameID
	URL = request.session['active_case_temp'].URL

	subject_category = request.session['active_case_temp'].subject_category 
	subject_subcategory = request.session['active_case_temp'].subject_subcategory
	scenario   =  request.session['active_case_temp'].scenario
	subject_activity  = request.session['active_case_temp'].subject_activity
	number_lost  = request.session['active_case_temp'].number_lost
	group_type = request.session['active_case_temp'].group_type 
	ecoregion_domain  = request.session['active_case_temp'].ecoregion_domain 
	ecoregion_division = request.session['active_case_temp'].ecoregion_division 
	terrain  = request.session['active_case_temp'].terrain
	total_hours = request.session['active_case_temp'].total_hours 





	# Create Input dictionary

	inputdic = {'Name_act':account_name, 'Name_m':model_name, 'name' :name, 'age':age, 'sex':sex,'LKP':LKP,'horcells':sidecells,'vercells':sidecells,'totcells' : totalcells, 'cellwidth' : 5, 'regionwidth' : 25,'upleft':upleft,'upright':upright,'downleft':downleft,'downright':downright,'MAP':URL}
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





	return render_to_response('TestWelcome.html',inputdic)

#-----------------------------------------------------------------------------------------------
def create_test(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	tempcase = request.session['active_case_temp'] 
	newtest = Test( test_case = tempcase,
			test_name = tempcase.case_name,
			ID2 = str(request.session['active_model'].ID2) + ':' +str(tempcase.case_name) )
	newtest.setup()

	newtest.save()

	Link = Test_Model_Link( test = newtest,
				model = request.session['active_model'])

	Link.save()

	return render_to_response('TestCreated.html')

#-------------------------------------------------------------------------------------------------
def setactive_test(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	intest = request.GET['test_in_active']
	print intest
	if intest == '0':
		return redirect('/model_menu/')

	else:
		request.session['active_test'] = Test.objects.get(ID2 = str(request.session['active_model'].ID2) + ':' + str(intest))
		return redirect('/test_instructions/')



#------------------------------------------------------------------------------------------------
def Activate_instructions(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	request.session['active_test'].show_instructions = True
	request.session['active_test'].save()
	return redirect('/test_instructions/')



#-------------------------------------------------------------------------------------------------
def tst_instructions(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	if request.session['active_test'].show_instructions == True:
		request.session['active_test'].show_instructions = False
		request.session['active_test'].save()
		return render_to_response('tst_instructions.html')
	else:
		return redirect('/test_active/')

#------------------------------------------------------------------------------------------------

def active_test(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------


	#request.session['active_test'] = Test.objects.get(ID2 = request.session['active_test'].ID2)
	active_test = request.session['active_test']
	print str(active_test.nav) + '-----nav'

	# If you have not passed  or conducted current test
	if int(active_test.nav) == 0:

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

		inputdic = {'pt1':pt1,'pt2':pt2,'pt3':pt3,'pt4':pt4,'pt5':pt5,'pt6':pt6,'pt7':pt7,'pt8':pt8,'pt9':pt9,'pic':url}

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
		upright = '('+active_case.upright_lat  + ',' +active_case.upright_lon + ')'
		downleft = '('+active_case.downleft_lat  + ',' +active_case.downleft_lon + ')'
		downright = '('+active_case.downright_lat  + ',' +active_case.downright_lon + ')'
		upleft = '('+active_case.upleft_lat  + ',' +active_case.upleft_lon + ')'

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
		terrain  = active_case.terrain
		total_hours = active_case.total_hours 





	# Create Input dictionary

		inputdic = {'Name_act':account_name, 'Name_m':model_name, 'name' :name, 'age':age, 'sex':sex,'LKP':LKP,'horcells':sidecells,'vercells':sidecells,'totcells' : totalcells, 'cellwidth' : 5, 'regionwidth' : 25,'upleft':upleft,'upright':upright,'downleft':downleft,'downright':downright,'MAP':URL}
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


		inputdic.update(csrf(request))
		return render_to_response('file_up.html',inputdic)

#--------------------------------------------------------------------------------------------------

def grid_test_result(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	active_test = request.session['active_test']


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


		inputdic01 ={'pt1x_i':pt1x,'pt1y_i':pt1y,'pt2x_i':pt2x,'pt2y_i':pt2y,'pt3x_i':pt3x,'pt3y_i':pt3y,'pt4x_i':pt4x,'pt4y_i':pt4y,'pt5x_i':pt5x,'pt6x_i':pt6x,'pt6y_i':pt6y,'pt7x_i':pt7x,'pt7y_i':pt7y,'pt8x_i':pt8x,'pt8y_i':pt8y,'pt9x_i':pt9x,'pt9y_i':pt9y}
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
	inputdic = {'pic':url, 'pt_agrid':pt_agrid,'status':status,'pt_latlon':pt_latlon,'pt_sgrid':pt_sgrid}

	# If you passed, mark on test
	if False not in result:

		request.session['active_test'].nav = 1
		request.session['active_test'].save()
		time.sleep(1)
		return render_to_response('grid_affirmation_Pass.html',inputdic)

	# If you fail, progress
	else:

		request.session['active_test'].nav = 1
		request.session['active_test'].save()
		time.sleep(1)
		return render_to_response('grid_affirmation_Fail.html',inputdic)

#---------------------------------------------------------------------------------------------------------
def regen_test(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	request.session['active_test'].nav = 0
	request.session['active_test'].generate_testpoints()
	request.session['active_test'].save()
	return redirect('/test_active/')

#------------------------------------------------------------------------------------------------------------

def passtest(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	active_test = request.session['active_test']
	request.session['active_test'].Validated = True
	request.session['active_test'].nav = 2
	request.session['active_test'].save()
	os.remove(request.session['active_test'].test_url2)

	return redirect('/test_active/')

#-----------------------------------------------------------------------------------------------------------
def Bulkin(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	active_test = request.session['active_test']
	inall = request.GET['Bulkin']
	stringlst = request.GET['Bulkin'].split()


	# Verify input
	pattern ='^[0-9]+$'


	inputdic01 ={'inall':inall}

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

#------------------------------------------------------------------------------------------------------------	
# Load Image 

def load_image(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	#******************** Alter for server
	#string = 'C:/Users/Nathan Jones/Django Website/MapRateWeb/media/'
	string = 'media/'

	 # reformat ID2
	#..................................................
	st = str(request.session['active_test'].ID2)
	temp = ''
	for i in st:
		if i == ':':
			temp = temp +'_'
		else:
			temp = temp + str(i)
	#...............................................	

	string = string + temp
	string = string + '.png'



	# Save the greyscale file path to the test object
	request.session['active_test'].greyscale_path = string
	request.session['active_test'].save()


	destination = open(string,'wb+')

	for chunk in request.FILES['grayscale'].chunks():
		destination.write(chunk)
	destination.close()

	return redirect('/confirm_grayscale/')

#-------------------------------------------------------------------------------------------------------------	
def confirm_grayscale(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	# Verify Image
	image_in = Image.open(request.session['active_test'].greyscale_path)

	# Check for demensions

	if image_in.size[0] != 5001 or image_in.size[1] != 5001:

		#----------------------------------------------------------------------------------------		
		# reformat ID2
		#..................................................
		st = str(request.session['active_test'].ID2)
		temp = ''
		for i in st:
			if i == ':':
				temp = temp +'_'
			else:
			 	temp = temp + str(i)
		#...............................................



		served_Location = '/media/' + temp + '.png'
		inputdic = {'grayscale':served_Location}
		return render_to_response('uploadfail_demensions.html',inputdic)


	data = image_in.getdata()

	bands = image_in.getbands()

	if bands[0] == 'R' and bands[1] == 'G' and bands[2] == 'B':
		count = 0
		for i in range(len(data)):
			if data[i][0] != data[i][1] or data[i][0] != data[i][2] or data[i][1] != data[i][2]:
				count = count + 1

		# image not grayscale
		if count > 0:

	#----------------------------------------------------------------------------------------		
			# reformat ID2
			#..................................................
			st = str(request.session['active_test'].ID2)
			temp = ''
			for i in st:
				if i == ':':
					temp = temp +'_'
				else:
					temp = temp + str(i)


			served_Location = '/media/' + temp + '.png'

			inputdic = {'grayscale':served_Location}

			return render_to_response('imageupload_fail.html',inputdic)

	#----------------------------------------------------------------------------------------		



	# REview		
	elif bands[0] == 'L'  or bands[0] == 'P':
		print 'actual grayscale'

	# Image not grayscale
	else:

	#----------------------------------------------------------------------------------------		
		# reformat ID2
		#..................................................
		st = str(request.session['active_test'].ID2)
		temp = ''
		for i in st:
			if i == ':':
				temp = temp +'_'
			else:
			 	temp = temp + str(i)
	#...............................................

		served_Location = '/media/' + temp + '.png'

		inputdic = {'grayscale':served_Location}

		return render_to_response('imageupload_fail.html',inputdic)

	#----------------------------------------------------------------------------------------	




	 # reformat ID2
	#..................................................
	st = str(request.session['active_test'].ID2)
	temp = ''
	for i in st:
		if i == ':':
			temp = temp +'_'
		else:
			temp = temp + str(i)
	#...............................................

	served_Location = '/media/' + temp + '.png'

	inputdic = {'grayscale':served_Location}

	return render_to_response('imageupload_confirm.html',inputdic)









#----------------------------------------------------------------------------------------------------------------
# deny grayscale confirmation
def denygrayscale_confirm(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	# Remove served Grayscale image
	os.remove(request.session['active_test'].greyscale_path)

	# Wipe the path
	request.session['active_test'].greyscale_path = 'none'
	request.session['active_test'].save()

	return redirect('/test_active/')


#----------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------
# accept grayscale confirmation
def acceptgrayscale_confirm(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	#string = 'C:/Users/Nathan Jones/Django Website/MapRateWeb/user_grayscale/'
	string = 'user_grayscale/'

	 # reformat ID2
	#..................................................
	st = str(request.session['active_test'].ID2)
	temp = ''
	for i in st:
		if i == ':':
			temp = temp +'_'
		else:
			temp = temp + str(i)
	#...............................................	

	string = string + temp
	string = string + '.jpg'


	# Remove served Grayscale image
	shutil.move(request.session['active_test'].greyscale_path, string)

	# set the path
	request.session['active_test'].greyscale_path = string
	request.session['active_test'].save()

	return redirect('/Rate_Test/')


#----------------------------------------------------------------------------------------------------------------




def Rate(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	response = request.session['active_test'].rate()

	# Resync Model
	request.session['active_model'] = Model.objects.get(ID2 = request.session['active_model'].ID2)

	os.remove(request.session['active_test'].greyscale_path)


	# record rating
	#--------------------------------------------------------------------
	request.session['active_account'].completedtests = int(request.session['active_account'].completedtests) + 1
	request.session['active_account'].save()
	#--------------------------------------------------------------------


	return redirect('/submissionreview/')	

#----------------------------------------------------------------------------------------------------------------
def submissionreview(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

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
	upright = '('+active_case.upright_lat  + ',' +active_case.upright_lon + ')'
	downleft = '('+active_case.downleft_lat  + ',' +active_case.downleft_lon + ')'
	downright = '('+active_case.downright_lat  + ',' +active_case.downright_lon + ')'
	upleft = '('+active_case.upleft_lat  + ',' +active_case.upleft_lon + ')'

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
	terrain  = active_case.terrain
	total_hours = active_case.total_hours 

	findpoint = '(' + active_case.findlat  + ',' +active_case.findlon + ')'
	findgrid =  '(' + active_case.findx  + ',' +active_case.findy + ')'



	URL2 = active_case.URLfind	
	rating = str(request.session['active_test'].test_rating)



	# Create Input dictionary

	inputdic = {'Name_act':account_name, 'Name_m':model_name, 'name' :name, 'age':age, 'sex':sex,'LKP':LKP,'horcells':sidecells,'vercells':sidecells,'totcells' : totalcells, 'cellwidth' : 5, 'regionwidth' : 25,'upleft':upleft,'upright':upright,'downleft':downleft,'downright':downright,'MAP':URL}
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


#-----------------------------------------------------------------------------------------------------------------------------------
def setcompletedtest(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	intest_raw = str(request.GET['Nonactive_Testin'])

	intest = ''
	for i in intest_raw:
		if i != ' ':
			intest = intest + str(i)


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

#-------------------------------------------------------------------------------------------------------------------------------------
def nonactivetest(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------


	active_test = request.session['active_test']
	active_case = active_test.test_case


	age = active_case.Age
	name = active_case.case_name
	sex = active_case.Sex
	LKP = '('+active_case.lastlat + ',' +active_case.lastlon + ')' 
	totalcells = active_case.totalcellnumber
	sidecells = active_case.sidecellnumber
	upright = '('+active_case.upright_lat  + ',' +active_case.upright_lon + ')'
	downleft = '('+active_case.downleft_lat  + ',' +active_case.downleft_lon + ')'
	downright = '('+active_case.downright_lat  + ',' +active_case.downright_lon + ')'
	upleft = '('+active_case.upleft_lat  + ',' +active_case.upleft_lon + ')'

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
	terrain  = active_case.terrain
	total_hours = active_case.total_hours 

	findpoint = '(' + active_case.findlat  + ',' +active_case.findlon + ')'
	findgrid =  '(' + active_case.findx  + ',' +active_case.findy + ')'



	URL2 = active_case.URLfind	
	rating = str(request.session['active_test'].test_rating)



	# Create Input dictionary

	inputdic = {'Name_act':account_name, 'Name_m':model_name, 'name' :name, 'age':age, 'sex':sex,'LKP':LKP,'horcells':sidecells,'vercells':sidecells,'totcells' : totalcells, 'cellwidth' : 5, 'regionwidth' : 25,'upleft':upleft,'upright':upright,'downleft':downleft,'downright':downright,'MAP':URL}
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

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def Leader_model(request):

	#-------------------------------------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False and request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#-------------------------------------------------------------------------------------------------

	sorted_models = []
	allmodels = Model.objects.all()

	# Sorting Algorithm largest -- smallest

	for i in allmodels:
		if i.model_avgrating != 'unrated':
			sorted_models.append(i)

	#Bubblesort
	alterations = 1
	while alterations > 0:

		tmplist =['']
		alterations = 0
		for i in range(len(sorted_models)-1):
			if float(sorted_models[i].model_avgrating) < float(sorted_models[i+1].model_avgrating):
				tmplist[0] = sorted_models[i]
				sorted_models[i] = sorted_models[i+1]
				sorted_models[i+1] =  tmplist[0]
				alterations = alterations + 1


	# copy values for leaderboard table
	inputlist = []
	sublist = []
	for i in range(len(sorted_models)):
		sublist = []
		institution = str(sorted_models[i].account_set.all()[0].institution_name)
		model = str(sorted_models[i].model_nameID)
		rating = str(sorted_models[i].model_avgrating)

		tests = sorted_models[i].model_tests.all()

		count = 0
		for n in tests:
			if n.Active == False:
				count = count + 1

		numbertests = count

		sublist.append(institution)
		sublist.append(model)
		sublist.append(rating)
		sublist.append(numbertests)

		inputlist.append(sublist)



	inputdic ={'Scorelist':inputlist}

	if request.session['active_account'] =='superuser':
		inputdic['superuser'] = True

	request.session['inputdic'] = inputdic	
	request.session['nav']	= '1'
	return render_to_response('Leader_Model.html',inputdic)

#---------------------------------------------------------------------------------------------------
def switchboard(request):

	#-------------------------------------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False and request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#-------------------------------------------------------------------------------------------------

	if request.GET['Sort_by'] == '0':
		return redirect('/Leader_model/')

	elif request.GET['Sort_by'] == '1':
		return redirect('/model_to_test_switch/')

#----------------------------------------------------------------------------------------------------
def model_to_test_switch(request):

	#-------------------------------------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False and request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#-------------------------------------------------------------------------------------------------

	request.session['nav']	= '2'
	inputdic = request.session['inputdic'] 	

	return render_to_response('Leaderboard_testname.html',inputdic)

#-------------------------------------------------------------------------------------------------------------
def switchboard_totest(request):	

	#-------------------------------------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False and request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#-------------------------------------------------------------------------------------------------

	casename_raw = str(request.GET['casename'])

	casename = ''
	for i in casename_raw:
		if i != ' ':
			casename = casename + str(i)



	cases = Case.objects.all()

	# check if the given casename is in the database
	ticker = 0
	for i in cases:
		if i.case_name == casename:
			Active_case = i
			ticker = ticker+1

	# If entry is invalid
	if ticker ==0:
		inputdic = request.session['inputdic'] 	
		return render_to_response('Leaderboard_Testfail.html',inputdic)

	# If entry is valid
	else:

		sorted_tests = []
		allTests = Test.objects.all()

		# Sorting Algorithm largest -- smallest

		for i in allTests:
			if i.Active == False and i.test_name == casename:
				sorted_tests.append(i)

		#Bubblesort
		alterations = 1
		while alterations > 0:

			tmplist =['']
			alterations = 0
			for i in range(len(sorted_tests)-1):
				if float(sorted_tests[i].test_rating) < float(sorted_tests[i+1].test_rating):
					tmplist[0] = sorted_tests[i]
					sorted_tests[i] = sorted_tests[i+1]
					sorted_tests[i+1] =  tmplist[0]
					alterations = alterations + 1


		# copy values for leaderboard table
		inputlist = []
		sublist = []
		for i in range(len(sorted_tests)):
			sublist = []
			institution = str(sorted_tests[i].model_set.all()[0].account_set.all()[0].institution_name)
			model = str(sorted_tests[i].model_set.all()[0].model_nameID)
			rating = str(sorted_tests[i].test_rating)

			test = str(sorted_tests[i].test_name)


			sublist.append(institution)
			sublist.append(model)
			sublist.append(test)
			sublist.append(rating)

			inputlist.append(sublist)


		inputdic ={'Scorelist':inputlist}

		if request.session['active_account'] =='superuser':
			inputdic['superuser'] = True

		request.session['inputdic'] = inputdic	
		request.session['nav']	= '3'
		return render_to_response('Leaderboard_test.html',inputdic)

#---------------------------------------------------------------------------------------------------------------
def testcaseshow(request):

	#-------------------------------------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False and request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#-------------------------------------------------------------------------------------------------

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
		name =  'Model Name: ' + str(i.model_nameID)
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

#-----------------------------------------------------------------------------------------------------------------
def return_leader(request):

	#-------------------------------------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False and request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#-------------------------------------------------------------------------------------------------

	inputdic = request.session['inputdic'] 	

	if request.session['nav'] == '3':
		return render_to_response('Leaderboard_test.html',inputdic)

	elif request.session['nav'] == '2':

		return render_to_response('Leaderboard_testname.html',inputdic)
#-----------------------------------------------------------------------------------------------------------------
def completedtest_info(request):

	#-------------------------------------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False and request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#-------------------------------------------------------------------------------------------------

	completed_lst = []

	for i in list(request.session['active_model'].model_tests.all()):
		if i.Active == False:
			completed_lst.append(str(i.test_name))

	inputdic ={'completed_lst': completed_lst}

	return render_to_response('completedtest_info.html',inputdic)

#----------------------------------------------------------------------------------------------------------------
def case_ref(request):

	#-------------------------------------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False and request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#-------------------------------------------------------------------------------------------------

	Input = request.GET['CaseName2']

	active_case = Case.objects.get(case_name = Input)

	age = active_case.Age
	name = active_case.case_name
	sex = active_case.Sex
	LKP = '('+active_case.lastlat + ',' +active_case.lastlon + ')' 
	totalcells = active_case.totalcellnumber
	sidecells = active_case.sidecellnumber
	upright = '('+active_case.upright_lat  + ',' +active_case.upright_lon + ')'
	downleft = '('+active_case.downleft_lat  + ',' +active_case.downleft_lon + ')'
	downright = '('+active_case.downright_lat  + ',' +active_case.downright_lon + ')'
	upleft = '('+active_case.upleft_lat  + ',' +active_case.upleft_lon + ')'

	URL = active_case.URL

	subject_category = active_case.subject_category 
	subject_subcategory = active_case.subject_subcategory
	scenario   =  active_case.scenario
	subject_activity  = active_case.subject_activity
	number_lost  = active_case.number_lost
	group_type = active_case.group_type 
	ecoregion_domain  = active_case.ecoregion_domain 
	ecoregion_division = active_case.ecoregion_division 
	terrain  = active_case.terrain
	total_hours = active_case.total_hours 



	# Create Input dictionary

	inputdic = { 'name' :name, 'age':age, 'sex':sex,'LKP':LKP,'horcells':sidecells,'vercells':sidecells,'totcells' : totalcells, 'cellwidth' : 5, 'regionwidth' : 25,'upleft':upleft,'upright':upright,'downleft':downleft,'downright':downright,'MAP':URL}
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

#-----------------------------------------------------------------------------------------------------------------------
def caseref_return(request):

	#-------------------------------------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False and request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#-------------------------------------------------------------------------------------------------

	inputdic = request.session['inputdic'] 

	return render_to_response('Leaderboard_test.html',inputdic)

#---------------------------------------------------------------------------------------------------------------------

def Account_Profile(request):

	#-------------------------------------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False and request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#-------------------------------------------------------------------------------------------------

	Account_in = request.GET['Account']

	Active_account = Account.objects.get(institution_name = Account_in)

	Name = str(Active_account.institution_name)
	Email = str(Active_account.Email)
	RegisteredUser = str(Active_account.firstname_user) + ' ' + str(Active_account.lastname_user)
	website = str(Active_account.Website)
	profpic = str(Active_account.photourl)

	inputdic = {'Name':Name, 'Email':Email, 'RegisteredUser':RegisteredUser, 'website':website,'profpic':profpic}

	if website !='none':
		inputdic['websitexists'] = True


	return render_to_response('Account_Profile.html',inputdic)
#--------------------------------------------------------------------------------------------------------------------
def returnfrom_profile(request):

	#-------------------------------------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False and request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#-------------------------------------------------------------------------------------------------

	inputdic = request.session['inputdic'] 

	if request.session['nav'] == '3':
		return render_to_response('Leaderboard_test.html',inputdic)

	elif request.session['nav'] == '2':

		return render_to_response('Leaderboard_testname.html',inputdic)

	elif request.session['nav'] == '1':

		return render_to_response('Leader_Model.html',inputdic)

#------------------------------------------------------------------------------------------------------------------------
def completedtest_modellink(request):

	#-------------------------------------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False and request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#-------------------------------------------------------------------------------------------------

	completedtest = str(request.GET['completedtest'])
	request.session['completedtest'] = completedtest
	request.session['completedtest_lookup'] = True
	return redirect('/model_menu/')


#---------------------------------------------------------------------------------------------------------------------
def case_hyperin(request):

	#-------------------------------------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False and request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#-------------------------------------------------------------------------------------------------

	inputdic = request.session['inputdic'] 


	caseselection = str(request.GET['casein'])



	if request.session['nav'] == '2':
		inputdic['caseselection'] = caseselection
		return render_to_response('Leaderboard_testname.html',inputdic)

	if request.session['nav'] == '3':
		inputdic['caseselection'] = caseselection
		return render_to_response('Leaderboard_test.html',inputdic)
#-----------------------------------------------------------------------------------------------------------------------

def upload_casefile(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	# Take in file - save to server
	#string = 'C:\Users\Nathan Jones\Django Website\MapRateWeb\case_in\input_unsorted.txt'
	string = 'case_in/input_unsorted.txt'
	destination = open(string,'wb+')

	for chunk in request.FILES['casetxt'].chunks():
		destination.write(chunk)
	destination.close()

	# Filter input file 
	file1 = open(string,'r')

	input1 = file1.readlines()

	file1.close()

	input1 = str(input1)



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
	pattern = '^\s*(.*)\s*$'


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
		subject_category = str(re.match(pattern,items[2]).group(1))
		subject_subcategory = str(re.match(pattern,items[3]).group(1))
		scenario = str(re.match(pattern,items[4]).group(1))
		subject_activity = str(re.match(pattern,items[5]).group(1))
		age = str(re.match(pattern,items[6]).group(1))
		sex = str(re.match(pattern,items[7]).group(1))
		number_lost = str(re.match(pattern,items[8]).group(1))
		group_type = str(re.match(pattern,items[9]).group(1))
		ecoregion_Domain = str(re.match(pattern,items[10]).group(1))
		ecoregion_Division = str(re.match(pattern,items[11]).group(1))
		terrain = str(re.match(pattern,items[12]).group(1))
		LKP_lat = str(re.match(pattern,items[13]).group(1))
		LKP_lon = str(re.match(pattern,items[14]).group(1))
		find_lat = str(re.match(pattern,items[15]).group(1))
		find_lon = str(re.match(pattern,items[16]).group(1))
		total_hours = str(re.match(pattern,items[17]).group(1))
		notify_hours = str(re.match(pattern,items[18]).group(1))
		search_hours = str(re.match(pattern,items[19]).group(1))
		comments = str(re.match(pattern,items[20]).group(1))


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

			)

		New_Case.initialize()

		# Only save if find location in bounds
		if New_Case.findx != "Out of Bounds" and New_Case.findy != "Out of Bounds":

			New_Case.save()

		line = filein.readline()

	filein.close()
	os.remove(string)
	os.remove(sortedaddress)

	return render_to_response('bulkcasereg_complete.html')


#------------------------------------------------------------------------------------------------------------------
def exportcaselibrary(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------


	#string = 'C:\Users\Nathan Jones\Django Website\MapRateWeb\case_in\exported_case_Library.txt'
	string = 'case_in/exported_case_Library.txt'
	file = open(string,'w')

	outputstr = ''
	for i in Case.objects.all():
		tempstr = ''
		tempstr = str(i.case_name) + '|' + str(i.key) + '|' + str(i.subject_category) + '|' + str(i.subject_subcategory) + '|' + str(i.scenario) + '|'
		tempstr = tempstr + str(i.subject_activity) + '|' + str(i.Age) + '|' + str(i.Sex) + '|' + str(i.number_lost) + '|' + str(i.group_type) + '|'
		tempstr = tempstr + str(i.ecoregion_domain) +'|' + str(i.ecoregion_division) + '|' + str(i.terrain) + '|' + str(i.lastlat) + '|' + str(i.lastlon) + '|'
		tempstr = tempstr + str(i.findlat) + '|' + str(i.findlon) + '|' + str(i.total_hours) + '|' + str(i.notify_hours) + '|' + str(i.search_hours) + '|' 
		tempstr = tempstr + str(i.comments) + '$'

		outputstr = outputstr + tempstr

	file.write(outputstr)
	file.close()

	return render_to_response('casexport_complete.html')

#-------------------------------------------------------------------------------------------------------------------------
def Manage_Account(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	return render_to_response('Account_manage.html')

#----------------------------------------------------------------------------------------------------------------------------
def edit_user(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	Account = request.session['active_account']

	Firstname_in = str(Account.firstname_user)
	Lastname_in = str(Account.lastname_user)
	Email_in = str(Account.Email)

	inputdic ={'Firstname_in':Firstname_in,'Lastname_in':Lastname_in,'Email_in':Email_in}

	return render_to_response('account_useredit.html',inputdic)

#------------------------------------------------------------------------------------------------------------------------------
def edit_user_run(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	Account = request.session['active_account']

	# read in information
	Firstname = str(request.GET['FirstName'])
	Lastname = str(request.GET['LastName'])
	Email_in = str(request.GET['Email'])
	Password = str(request.GET['Password'])
	#identify regular expressions

	Firstname_r = '^.+$'
	Lastname_r  = '^.+$'
	Email_in_r  = '^[a-zA-z0-9\.]+@[a-zA-z0-9]+\.[a-zA-z0-9]+$'


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
		return 	render_to_response('account_useredit.html',inputdic)


	if count2 == 1:

		inputdic['fail2'] = True
		return 	render_to_response('account_useredit.html',inputdic)


	# Update Account

	Account.firstname_user = Firstname
	Account.lastname_user = Lastname
	Account.Email = Email_in
	Account.save()

	return 	render_to_response('account_update_complete.html')


#---------------------------------------------------------------------------------------------
def edit_inst(request):	

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	Account = request.session['active_account']

	Institution_in = str(Account.institution_name)
	Websitein_in = str(Account.Website)


	inputdic ={'Institution_in':Institution_in,'Websitein_in':Websitein_in}

	return render_to_response('account_editinstitution.html',inputdic)
#---------------------------------------------------------------------------------------------
def edit_inst_run(request):			

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	Account = request.session['active_account']

	# read in information
	Institution = str(request.GET['Institution'])
	Website = str(request.GET['Website'])
	Password = str(request.GET['Password'])

	#identify regular expressions

	Institution_r = "^[a-zA-z\s:0-9']+$"
	Websitein_r ='.*$' 

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
		return 	render_to_response('account_editinstitution.html',inputdic)


	if count2 == 1:

		inputdic['fail2'] = True
		return 	render_to_response('account_editinstitution.html',inputdic)


	# Update Account

	if Website == '':
		Website = 'none'

	Account.institution_name = Institution
	Account.Website = Website

	Account.save()

	return 	render_to_response('account_update_complete.html')	


#-------------------------------------------------------------------------------------------------

def edit_pw(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	return render_to_response('account_editpw.html')

#-------------------------------------------------------------------------------------------------

def edit_pw_run(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

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
		return 	render_to_response('account_editpw.html',inputdic)


	if count2 == 1:

		inputdic['fail2'] = True
		return 	render_to_response('account_editpw.html',inputdic)


	# Update Account

	Account.password = Password1
	Account.save()

	User_in = User.objects.get(username = str(Account.username))
	User_in.set_password(Password1)
	User_in.save()

	return 	render_to_response('account_update_complete.html')	

#--------------------------------------------------------------------------
def uploadprofpic(request):

	inputdic = {}
	inputdic.update(csrf(request))
	return 	render_to_response('uploadaccountpic.html',inputdic)

#----------------------------------------------------------------------------
def accountregcomplete(request):

	return 	render_to_response('RegistrationComplete.html',{})

#----------------------------------------------------------------------------
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

		im.resize((350,350))

	im.save(str(account.photolocation))


	#----------------------------------------------------------------------------------
	inputdic = {'account_photo':account.photourl}

	return 	render_to_response('profpic_confirm.html',inputdic)

#------------------------------------------------------------------------------
def denyprofpic_confirm(request):
	account = request.session['active_account']

	#shutil.copyfile('C:\Users\Nathan Jones\Django Website\MapRateWeb\in_images\Defaultprofpic.png',account.photolocation)
	shutil.copyfile('in_images/Defaultprofpic.png',account.photolocation)

	return redirect('/uploadprofpic/')

#------------------------------------------------------------------------------
def confirmprofpic_confirm(request):


	return redirect('/accountregcomplete/')

#---------------------------------------------------------------------------------
def edit_picture(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	account = request.session['active_account']
	inputdic = {'account_photo':account.photourl}

	return 	render_to_response('edit_profpic.html',inputdic)

#---------------------------------------------------------------------------------
def remove_profpic(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	account = request.session['active_account']

	#shutil.copyfile('C:\Users\Nathan Jones\Django Website\MapRateWeb\in_images\Defaultprofpic.png',account.photolocation)
	shutil.copyfile('in_images/Defaultprofpic.png',account.photolocation)
	time.sleep(2)

	return redirect('/edit_picture/')


#--------------------------------------------------------------------------
def alterprofpic(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	inputdic = {}
	inputdic.update(csrf(request))
	return 	render_to_response('change_accountpic.html',inputdic)

#----------------------------------------------------------------------------

def change_accountpic(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------


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

		im.resize((350,350))

	im.save(str(account.photolocation))

	time.sleep(4)

	return redirect('/edit_picture/')
#----------------------------------------------------------------------------------
def traffic(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	mainhits = int(Mainhits.objects.all()[0].hits)

	inputlst = []
	for i in Account.objects.all():
		tmplst = []
		tmplst.append(str(i.username))
		tmplst.append(str(i.institution_name))
		tmplst.append(str(i.sessionticker))
		tmplst.append(str(len(i.account_models.all())))
		tmplst.append(str(i.completedtests))

		inputlst.append(tmplst)

	deletedlst = []
	for i in terminated_accounts.objects.all():
		tmplst = []
		tmplst.append(str(i.username))
		tmplst.append(str(i.institution_name))
		tmplst.append(str(i.sessionticker))
		tmplst.append(str(i.models))
		tmplst.append(str(i.completedtests))

		deletedlst.append(tmplst)



	inputdic = {'mainhits':mainhits,'inputlst':inputlst,'deletedlst':deletedlst}

	return 	render_to_response('traffic.html',inputdic)


#-----------------------------------------------------------------------------------
def delete_account(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	return 	render_to_response('Deleteaccount.html')

#------------------------------------------------------------------------------------
def deleteaccount_confirm(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['usertoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	password = str(request.GET['Password'])
	account =  request.session['active_account']

	# If invalid password
	if password != str(account.password):

		inputdic ={'passfail':True}
	 	return 	render_to_response('Deleteaccount.html',inputdic)


	# If account is to be deleted
	else:
		# create new deleted object

		t = terminated_accounts()
		t.username = str(account.username)
		t.sessionticker = str(account.sessionticker)
		t.completedtests = str(account.completedtests)
		t.institution_name = str(account.institution_name)
		t.models = str(len(account.account_models.all()))
		t.save()


	 	#Delete Tests / models

	 	for i in account.account_models.all():

	 		for j in i.model_tests.all():
	 			j.delete()

	 		i.delete()

	 	 # Delete Picture
	 	os.remove(account.photolocation)

	 	# delete account

	 	account.delete()

	 	return 	render_to_response('Accountdeleted.html')

#-------------------------------------------------------------------------------------
def terminate_accounts(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------


	inputdic = {}

	if str(request.session['userdel']) != '':
		username = str(request.session['userdel'])
		inputdic['accountin'] = username
		request.session['userdel'] = ''

	return 	render_to_response('adminaccountermination.html',inputdic)

#-------------------------------------------------------------------------------------
def view_username_admin(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	inputlist = []
	for i in Account.objects.all():
		tmplst = []
		tmplst.append(i.username)
		tmplst.append(i.institution_name)
		inputlist.append(tmplst)

	inputdic = {'inputlist':inputlist}

	return 	render_to_response('account_admin_terminfo.html',inputdic)

#-----------------------------------------------------------------------------------
def delaccountlink(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

	user = str(request.GET['username'])
	request.session['userdel'] = user	

	return redirect('/terminate_accounts/')	

#------------------------------------------------------------------------------------
def adminterminate_account(request):

	#------------------------------------------------------------------
	# Token Verification
	try:
		if request.session['admintoken'] == False:
			return render_to_response('noaccess.html',{})
	except: 
		return render_to_response('noaccess.html',{})

	#---------------------------------------------------------------------

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
		return 	render_to_response('adminaccountermination.html',inputdic)


	# If pass -- proceed with delete

	account = Account.objects.get(username = username)

	# create new deleted object

	t = terminated_accounts()
	t.username = str(account.username)
	t.sessionticker = str(account.sessionticker)
	t.completedtests = str(account.completedtests)
	t.institution_name = str(account.institution_name)
	t.models = str(len(account.account_models.all()))
	t.save()


	 #Delete Tests / models

	for i in account.account_models.all():

		for j in i.model_tests.all():
			j.delete()

	 	i.delete()

	 # Delete Picture
	os.remove(account.photolocation)


	 # delete account

	account.delete()


	return 	render_to_response('accountdeleted_admin.html')

