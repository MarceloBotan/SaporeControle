from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.BranchList.as_view(), name='branch_list'),
    path('add/', views.BranchAdd.as_view(), name='branch_add'),
]