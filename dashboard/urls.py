from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('delete_object/<str:_type>/<int:_id>', views.delete_object, name='delete_object'),
    path('edit_object/<str:_type>/<int:_id>', views.edit_object, name='edit_object'),
    path('add_object/<str:_type>', views.add_object, name='add_object'),
    
    path('dashboard/chart_visibility', views.chart_visibility, name='chart_visibility'),
    path('dashboard/chart_visibility/<int:_id>/<int:show>', views.chart_visibility, name='chart_visibility'),

    path('dashboard/telecom', views.DashboardTelecom.as_view(), name='dashboard_telecom'),

    path('dashboard/chart_list', views.ChartList.as_view(), name='chart_list'),
    path('dashboard/chart_add', views.ChartAdd.as_view(), name='chart_add'),
    path('dashboard/chart_edit/<int:pk>', views.ChartEdit.as_view(), name='chart_edit'),
]