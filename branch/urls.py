from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.BranchList.as_view(), name='branch_list'),
    path('edit/', views.BranchEdit.as_view(), name='branch_edit'),
]