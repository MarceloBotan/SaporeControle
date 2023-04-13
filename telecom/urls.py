from django.urls import path
from . import views

urlpatterns = [
    path('', views.Dashboard.as_view(), name='index'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    
    path('generate_csv/<str:telecom_type>/<int:csv_simple>', views.generate_csv, name='generate_csv'),

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