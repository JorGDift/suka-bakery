from django.urls import path
from . import views

app_name = 'usersApp'

urlpatterns = [
    path('user-login/', views.UserLoginView.as_view(), name='custom-admin-login'),
    path('user-logout/', views.UserLogoutView.as_view(), name='custom-admin-logout'),
    path('crear-usuario/', views.CustomAdminUserCreateView.as_view(), name='custom-admin-user-create'),
    path('listar-usuarios/', views.CustomAdminUserListView.as_view(), name='custom-admin-user-list'),
    path('actualizar-usuarios/<int:pk>', views.CustomAdminUserUpdateView.as_view(), name='custom-admin-user-update'),
    path('actualizar-contraseña-usuario/<int:pk>', views.AdminPasswordChangeView.as_view(), name='custom-admin-password-user-update'),
    path('eliminar-usuario/<int:pk>', views.CustomAdminUserDeleteView.as_view(), name='custom-admin-user-delete'),
]