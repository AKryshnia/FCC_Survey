from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_profile, name='user_profile'),
    path('survey/<int:enterprise_id>/', views.survey, name='survey'),
    path('survey/thanks/', views.survey_thanks, name='survey_thanks'),
    path('survey/results/<int:enterprise_id>/', views.survey_statistics, name='result_page'),
    path('survey/statistics/<int:enterprise_id>/', views.survey_statistics, {'mode': 'statistics'}, name='statistics'),
    path('enterprise/<int:enterprise_id>/', views.enterprise_detail, name='enterprise_detail'),
    path('enterprises/', views.enterprise_list, name='enterprise_list'),
    path('enterprises/add/', views.add_enterprise, name='add_enterprise'),
    path('enterprises/added/', views.enterprise_added, name='add_enterprise_success'),
    path('enterprises/edit/<int:enterprise_id>/', views.edit_enterprise, name='edit_enterprise'),
    path('enterprises/edited/<int:enterprise_id>/', views.enterprise_edited, name='edit_enterprise_success'),
    path('generate-pdf/<int:enterprise_id>/', views.generate_pdf, name='generate_pdf'),
    ]
