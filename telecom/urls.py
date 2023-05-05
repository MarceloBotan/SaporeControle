from django.urls import path
from . import views

urlpatterns = [
    path('generate_csv/<str:telecom_type>/<int:csv_simple>', views.generate_csv, name='generate_csv'),

    #Modelo/Plano#
    path('smartphone_model_list/', views.SmartphoneModelList.as_view(), name='smartphone_model_list'),
    path('smartphone_model_edit/<int:pk>', views.SmartphoneModelEdit.as_view(), name='smartphone_model_edit'),
    path('smartphone_model_add/', views.SmartphoneModelAdd.as_view(), name='smartphone_model_add'),

    path('vivobox_model_list/', views.VivoboxModelList.as_view(), name='vivobox_model_list'),
    path('vivobox_model_edit/<int:pk>', views.VivoboxModelEdit.as_view(), name='vivobox_model_edit'),
    path('vivobox_model_add/', views.VivoboxModelAdd.as_view(), name='vivobox_model_add'),

    path('line_plan_list/', views.LinePlanList.as_view(), name='line_plan_list'),
    path('line_plan_edit/<int:pk>', views.LinePlanEdit.as_view(), name='line_plan_edit'),
    path('line_plan_add/', views.LinePlanAdd.as_view(), name='line_plan_add'),

    #Status#
    path('smartphone_status_list/', views.SmartphoneStatusList.as_view(), name='smartphone_status_list'),
    path('smartphone_status_edit/<int:pk>', views.SmartphoneStatusEdit.as_view(), name='smartphone_status_edit'),
    path('smartphone_status_add/', views.SmartphoneStatusAdd.as_view(), name='smartphone_status_add'),

    path('vivobox_status_list/', views.VivoboxStatusList.as_view(), name='vivobox_status_list'),
    path('vivobox_status_edit/<int:pk>', views.VivoboxStatusEdit.as_view(), name='vivobox_status_edit'),
    path('vivobox_status_add/', views.VivoboxStatusAdd.as_view(), name='vivobox_status_add'),

    path('line_status_list/', views.LineStatusList.as_view(), name='line_status_list'),
    path('line_status_edit/<int:pk>', views.LineStatusEdit.as_view(), name='line_status_edit'),
    path('line_status_add/', views.LineStatusAdd.as_view(), name='line_status_add'),

    path('line_status_rfp_list/', views.LineStatusRFPList.as_view(), name='line_status_rfp_list'),
    path('line_status_rfp_edit/<int:pk>', views.LineStatusRFPEdit.as_view(), name='line_status_rfp_edit'),
    path('line_status_rfp_add/', views.LineStatusRFPAdd.as_view(), name='line_status_rfp_add'),

    #Itens#
    path('line_list/', views.LineList.as_view(), name='line_list'),
    path('line_search/', views.LineSearch.as_view(), name='line_search'),
    path('line_details/<int:pk>', views.LineDetails.as_view(), name='line_details'),
    path('line_edit/<int:pk>', views.LineEdit.as_view(), name='line_edit'),
    path('line_add/', views.LineAdd.as_view(), name='line_add'),

    path('smartphone_list/', views.SmartphoneList.as_view(), name='smartphone_list'),
    path('smartphone_search/', views.SmartphoneSearch.as_view(), name='smartphone_search'),
    path('smartphone_details/<int:pk>', views.SmartphoneDetails.as_view(), name='smartphone_details'),
    path('smartphone_edit/<int:pk>', views.SmartphoneEdit.as_view(), name='smartphone_edit'),
    path('smartphone_add/', views.SmartphoneAdd.as_view(), name='smartphone_add'),

    path('vivobox_list/', views.VivoBoxList.as_view(), name='vivobox_list'),
    path('vivobox_search/', views.VivoBoxSearch.as_view(), name='vivobox_search'),
    path('vivobox_details/<int:pk>', views.VivoBoxDetails.as_view(), name='vivobox_details'),
    path('vivobox_edit/<int:pk>', views.VivoBoxEdit.as_view(), name='vivobox_edit'),
    path('vivobox_add/', views.VivoBoxAdd.as_view(), name='vivobox_add'),
]