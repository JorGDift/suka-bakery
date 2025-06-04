from django.urls import path
from . import views

app_name = 'productApp'

urlpatterns = [
    path('lista-productos/', views.CustomAdminProductListView.as_view(), name='product-list'),
    path('crear-producto/', views.CustomAdminCreateProductView.as_view(), name='product-create'),
    path('actualizar-producto/<int:pk>', views.CustomAdminProductUpdateView.as_view(), name='admin-product-update'),
    path('eliminar-producto/<int:pk>/', views.CustomAdminProductDeletView.as_view(), name='product-deleted'),
    path('crear-categoria/', views.CustomAdminCreateCategoryView.as_view(), name='admin-category-create'),
    path('listar-categorias/', views.CustomAdminCategoryListView.as_view(), name='admin-category-list'),
    path('actualizar-categoria/<int:pk>', views.CustomAdminCategoryUpdateView.as_view(), name='admin-category-update'),
    path('eliminar-categorias/<int:pk>', views.CustomAdminCategoryDeletedView.as_view(), name='admin-category-deleted'),
    path('listado-sabores/', views.CustomAdminFlavorsCreateView.as_view(), name='admin-flavor-create'),
    path('crear-sabor/', views.CustomAdminFlavorsListView.as_view(), name='admin-flavor-list'),
    path('actualizar-sabor/<int:pk>', views.CustomAdminFlavorsUpdateView.as_view(), name='admin-flavor-update'),
    path('eliminar-sabor/<int:pk>', views.CustomAdminFlavorsDeletedView.as_view(), name='admin-flavor-deleted'),
    path('listado-tamaños/', views.CustomAdminSizesListView.as_view(), name='admin-size-list'),
    path('crear-tamaño/', views.CustomAdminSizesCreateView.as_view(), name='admin-size-create'),
    path('actualizar-tamaño/<int:pk>', views.CustomAdminSizeUpdateView.as_view(), name='admin-size-update'),
    path('eliminar-tamaño/<int:pk>', views.CustomAdminSizeDeletedView.as_view(), name='admin-size-deleted'),
]

