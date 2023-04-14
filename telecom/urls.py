from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    
    path('generate_csv/<str:telecom_type>/<int:csv_simple>', views.generate_csv, name='generate_csv'),

    path('delete_model/<str:telecom_type>/<int:model_id>', views.delete_model, name='delete_model'),

    path('s_model_list/', views.SmartModelList.as_view(), name='s_model_list'),
    path('s_model_edit/<int:pk>', views.SmartModelEdit.as_view(), name='s_model_edit'),
    path('s_model_add/', views.SmartModelAdd.as_view(), name='s_model_add'),

    path('v_model_list/', views.BoxModelList.as_view(), name='v_model_list'),
    path('v_model_edit/<int:pk>', views.BoxModelEdit.as_view(), name='v_model_edit'),
    path('v_model_add/', views.BoxModelAdd.as_view(), name='v_model_add'),

    path('line_plan_list/', views.LinePlanList.as_view(), name='line_plan_list'),
    path('line_plan_edit/<int:pk>', views.LinePlanEdit.as_view(), name='line_plan_edit'),
    path('line_plan_add/', views.LinePlanAdd.as_view(), name='line_plan_add'),

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