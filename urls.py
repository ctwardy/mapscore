from django.conf.urls.defaults import patterns, include, url
from Views import main_page 
from Views import account_reg
from Views import create_account
from Views import account_access
from Views import model_regform
from Views import model_created
from Views import base_redirect
from Views import model_access
from Views import admin_login
from Views import admin_account
from Views import testcase_admin
from Views import newtest
from Views import Casereg
from Views import create_test
from django.contrib import admin
from Views import tst_instructions
from Views import setactive_test
from Views import active_test
from Views import grid_test_result
from Views import regen_test
from Views import load_image
from Views import passtest
from Views import Bulkin
from Views import Activate_instructions
from django.conf import settings
from Views import Rate
from Views import confirm_grayscale
admin.autodiscover()
from django.conf.urls.static import static
from Views import denygrayscale_confirm
from Views import acceptgrayscale_confirm
from Views import submissionreview
from Views import setcompletedtest
from Views import nonactivetest
from Views import Leader_model
from Views import switchboard
from Views import model_to_test_switch
from Views import switchboard_totest
from Views import testcaseshow
from Views import return_leader
from Views import completedtest_info
from Views import case_ref
from Views import caseref_return
from Views import Account_Profile
from Views import returnfrom_profile
from Views import completedtest_modellink
from Views import case_hyperin
from Views import upload_casefile
from Views import exportcaselibrary
from Views import Manage_Account
from Views import edit_user
from Views import edit_user_run
from Views import edit_inst
from Views import edit_inst_run
from Views import edit_pw
from Views import edit_pw_run
from Views import uploadprofpic
from Views import accountregcomplete
from Views import confirm_prof_pic
from Views import denyprofpic_confirm
from Views import confirmprofpic_confirm
from Views import edit_picture
from Views import remove_profpic
from Views import alterprofpic
from Views import change_accountpic
from Views import traffic
from Views import delete_account
from Views import deleteaccount_confirm
from Views import terminate_accounts
from Views import view_username_admin
from Views import delaccountlink
from Views import adminterminate_account

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('', 
			  ('^$', base_redirect),
			  ('^main/$',main_page),
			  ('^account_reg/$',account_reg),
			  ('^create_account/$',create_account),
			  ('^account/$',account_access),
			  ('^new_model/$',model_regform),
			  ('^model_created/$',model_created),
			  ('^model_menu/$',model_access),
			  (r'^admin/$',include(admin.site.urls)),
			  ('^admin_login/$',admin_login),
			  ('^admin_account/$',admin_account),
			  ('^admin_cases/$',testcase_admin),
			  ('^new_testcase/$',Casereg),
			  ('^new_test/$',newtest),
			  ('^create_test/$',create_test),
			  ('^test_instructions/$',tst_instructions),
			  ('^setactive_test/$',setactive_test),
			  ('^test_active/$' , active_test),
			  ('^grid_testresult/$',grid_test_result),
			  ('^regen_test/$',regen_test),
			  ('^upload_file/$',load_image),
			  ('^pass_test/$', passtest),
			  ('^bulkin/$',Bulkin),
			  ('^activate_inst/$',Activate_instructions),
			  ('^Rate_Test/$' , Rate),
			  ('^confirm_grayscale/$',confirm_grayscale),
			  ('^denygrayscale_confirm/$', denygrayscale_confirm),
			  ('^acceptgrayscale_confirm/$',acceptgrayscale_confirm),
			  ('^submissionreview/$',submissionreview),
			  ('^nonactive_test/$',setcompletedtest),
			  ('^Nonactive_test/$',nonactivetest),
			  ('^Leader_model/$',Leader_model),
			  ('^switchboard/$',switchboard),
			  ('^model_to_test_switch/$',model_to_test_switch),
			  ('^switchboard_totest/$',switchboard_totest),
			  ('^case_info/$',testcaseshow),
			  ('^return_leader/$',return_leader),
			  ('^completedtest_info/$',completedtest_info),
			  ('^case_ref/$',case_ref),
			  ('^caseref_return/$',caseref_return),
			  ('^Account_Profile/$',Account_Profile),
			  ('^returnfrom_profile/$',returnfrom_profile),
			  ('^completedtest_modellink/$',completedtest_modellink),
			  ('^case_hyperin/$',case_hyperin),
			  ('^upload_casefile/$',upload_casefile),
			  ('^exportcaselibrary/$',exportcaselibrary),
			  ('^Manage_Account/$',Manage_Account),
			  ('^edit_user/$',edit_user),
			  ('^edit_user_run/$',edit_user_run),
			  ('^edit_inst/$',edit_inst),
			  ('^edit_inst_run/$',edit_inst_run),
			  ('^edit_pw/$',edit_pw),
			  ('^edit_pw_run/$',edit_pw_run),
			  ('^uploadprofpic/$',uploadprofpic),
			  ('^accountregcomplete/$',accountregcomplete),
			  ('^confirm_prof_pic/$',confirm_prof_pic),
			  ('^denyprofpic_confirm/$',denyprofpic_confirm),
			  ('^confirmprofpic_confirm/$',confirmprofpic_confirm),
			  ('^edit_picture/$',edit_picture),
			  ('^remove_profpic/$',remove_profpic),
			  ('^alterprofpic/$',alterprofpic),
			  ('^change_accountpic/$',change_accountpic),
			  ('^traffic/$',traffic),
			  ('^delete_account/$',delete_account),
			  ('^deleteaccount_confirm/$',deleteaccount_confirm),
			  ('^terminate_accounts/$',terminate_accounts),
			  ('^view_username_admin/$',view_username_admin),
			  ('^delaccountlink/$',delaccountlink),
			  ('^adminterminate_account/$',adminterminate_account),
			  
    # Examples:
    # url(r'^$', 'MapRateWeb.views.home', name='home'),
    # url(r'^MapRateWeb/', include('MapRateWeb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
