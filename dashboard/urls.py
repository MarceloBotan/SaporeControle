from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/telecom', views.DashboardTelecom.as_view(), name='dashboard_telecom'),

    path('dashboard/delete_chart/<int:id>', views.delete_chart, name='delete_chart'),

    path('dashboard/chart_list', views.ChartList.as_view(), name='chart_list'),
    path('dashboard/chart_add', views.ChartAdd.as_view(), name='chart_add'),
    path('dashboard/chart_edit/<int:pk>', views.ChartEdit.as_view(), name='chart_edit'),
]