from django.urls import path
from . import views

app_name = 'quoteApp'

urlpatterns = [
    path('delivery-create/', views.DeliveryCreateView.as_view(), name='suka_admin_delivery_create'),
    path('delivery-list/', views.DeliveryListView.as_view(), name='suka_admin_delivery_list'),
    path('delivery-update/<int:pk>', views.DeliveryUpdateView.as_view(), name='suka_admin_delivery_update'),
    path('delivery-delete/<int:pk>', views.DeliveryDeleteView.as_view(), name='suka_admin_delivery_delete'),


    ######################
    #### COTIZACIONES ####
    ######################
    path('quotation-create/', views.QuotationCreateView.as_view(), name='suka_admin_quotation_create'),
    path('quotation-update/<int:pk>', views.OrderUpdateView.as_view(), name='suka_admin_quotation_update'),
    path('quotation-list/', views.QuotationListView.as_view(), name='suka_admin_quotation_list'),
    path('api/orders/<int:order_id>/', views.get_order_details, name='api-order-details'),
    path('quotation-detail/<int:pk>/', views.QuotationDetailView.as_view(), name='suka_admin_quotation_detail'),
    path('quotation-delete/<int:pk>', views.QuotationDeletedView.as_view(), name='suka_admin_quotation_delete'),
]