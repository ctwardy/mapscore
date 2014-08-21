from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static import static
from django.http import HttpResponse
from django.conf import settings

from django.contrib import admin
admin.autodiscover()
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from Views import *

urlpatterns = patterns('',
              ('^$', base_redirect),
              ('^main/$', main_page),
              ('^log_out/$',log_out),
              ('^log_in/$', log_in),
              #('^account_reg/$',account_reg),
              #('^create_account/$',create_account),
              ('^account/$',account_access),
              ('^batch_test_upload/$',batch_test_upload),
              url('^batch_test_upload/$', batch_test_upload, name='batch_test_upload'),
              url('^batch_test_upload_final/$', batch_test_upload_final, name='batch_test_upload_final'), 
              
              ('^create_account/$', create_account), 
              ('^create_account_submit/$', create_account_submit), 
              ('^edit_account/$', edit_account), 
              ('^edit_account_submit/$', edit_account_submit), 
              ('^edit_model/$', edit_model), 
              ('^edit_model_submit/$', edit_model_submit), 
              
              #('^create_model/$', create_model), 
              
              ('^model_menu/$', model_access), 
              (r'^admin/$',include(admin.site.urls)),
              ('^admin_login_page/$',admin_login_page),
              (r'^admin_log_in/$', admin_log_in), 
              ('^admin_account/$',admin_account),
              ('^admin_cases/$',testcase_admin),
              ('^new_testcase/$',Casereg),
              ('^test_instructions/$',test_instructions),
              #('^regen_test/$',regen_test),
              ('^evaluate/$', evaluate),
              ('^completed_test/$', completed_test),
              
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
              ('^case_hyperin/$',case_hyperin),
              ('^upload_casefile/$',upload_casefile),
              ('^exportcaselibrary/$',exportcaselibrary),
              
              ('^traffic/$',traffic),
              ('^delete_account/$',delete_account),
              ('^deleteaccount_confirm/$',deleteaccount_confirm),
              ('^terminate_accounts/$',terminate_accounts),
              ('^view_username_admin/$',view_username_admin),
              ('^delaccountlink/$',delaccountlink),
              ('^adminterminate_account/$',adminterminate_account),
              ('^delete_model/$',delete_model),
              ('^deletemodel_confirm/$',deletemodel_confirm),
              ('^help/$',help),
              ('^help_how_alter_account/$',help_how_alter_account),
              
              ('^model_to_Scenario_switch/$',model_to_Scenario_switch),
              ('^switchboard_toscenario/$',switchboard_toscenario),
              ('^test_to_Scenario_switch/$',test_to_Scenario_switch),
              ('^test_to_test_switch/$',test_to_test_switch),
              ('^scenario_to_test_switch/$',scenario_to_test_switch),
              ('^scenario_to_scenario_switch/$',scenario_to_scenario_switch),
              ('^hyper_leaderboard/$',hyper_leaderboard),
              
              ('^password_reset/$', password_reset),
              ('^password_reset_submit/$', password_reset_submit),
              
              # To be deleted
              ('^model_inst_sort/$',model_inst_sort),
              ('^model_name_sort/$',model_name_sort),
              ('^model_rtg_sort/$',model_rtg_sort),
              ('^model_tstscomp_sort/$',model_tstscomp_sort),
              ('^test_inst_sort/$',test_inst_sort),
              ('^test_modelname_sort/$',test_modelname_sort),
              ('^test_name_sort/$',test_name_sort),
              ('^test_rating_sort/$',test_rating_sort),
              ('^cat_inst_sort/$',cat_inst_sort),
              ('^cat_modelname_sort/$',cat_modelname_sort),
              ('^catrating_sort/$',catrating_sort),
              ('^catcompleted_sort/$',catcompleted_sort),
              ('^model_Profile/$',model_Profile),
              
              ('^leaderboard/$', leaderboard), 
              ('^metric_description/$', metric_description), 
              ('^reg_conditions/$', reg_conditions),
              ('^DownloadParam/$', DownloadParam),
              ('^UploadLayers/$', UploadLayers),
              ('^upload_Layerfile/$', upload_Layerfile),
              ('^DownloadLayers/$', DownloadLayers),
              ('^delete_Layers/$', delete_Layers),
              ('^DownloadLayersadmin/$', DownloadLayersadmin),
              ('^casetypeselect/$', casetypeselect),
              ('^NextSequentialTestSwitch/$', NextSequentialTestSwitch),
              ('^TesttypeSwitch/$', TesttypeSwitch),
              ('^TestNameSwitch/$', TestNameSwitch),
              ('^test/$', test),
              ('^permission_denied/$', permission_denied), 
              (r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain")),
             
             
    # Examples:
    # url(r'^$', 'MapRateWeb.views.home', name='home'),
    # url(r'^MapRateWeb/', include('MapRateWeb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
