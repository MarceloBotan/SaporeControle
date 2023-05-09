from django.urls import path
from . import views

#app_name = 'printer'


urlpatterns = [
    path('printer_list/', views.PrinterList.as_view(), name='printer_list'),
    path('printer_edit/<int:pk>', views.PrinterEdit.as_view(), name='printer_edit'),
    path('printer_add/', views.PrinterAdd.as_view(), name='printer_add'),
]