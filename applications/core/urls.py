from django.urls import path
from . import views

app_name = 'coreApp'

urlpatterns = [
    path('inicio/', views.HomeView.as_view(), name='Home'),
    path('admin-dashboard/', views.CustomAdminDashBoardView.as_view(), name='custom-admin-dashboard'),
]