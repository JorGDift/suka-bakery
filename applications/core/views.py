from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from django.http import HttpResponseRedirect

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction

from django.urls import reverse_lazy
from django.core.exceptions import ValidationError


from django.views.generic import ListView, View, TemplateView, CreateView

from applications.products.models import Product, Category, ProductImage
from applications.quotes.models import Order, Delivery


# Create your views here.
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser  # o cualquier otra condición

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('usersApp:custom-admin-login')  # Redirige al login si no está autenticado
        return redirect('usersApp:custom-admin-login')  # Redirige a otra página si no tiene permisos

class HomeView(ListView):
    template_name = 'suka_client/base.html'
    model = Product
    context_object_name = 'product_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        # Obtenemos el contexto base
        context = super().get_context_data(**kwargs)

        # Creamos un diccionario para agrupar los productos por categoría
        products_by_category = {}

        # Obtenemos únicamente las categorías que tienen productos asociados
        categories = Category.objects.filter(products__isnull=False).distinct()

        # Para cada categoría, obtenemos sus productos relacionados
        for category in categories:
            products = category.products.all()  # Usamos el related_name='products'
            if products.exists():  # Validamos que hayan productos antes de incluir
                products_by_category[category.name] = products

        # Agregamos los productos agrupados por categoría al contexto
        context['products_by_category'] = products_by_category

        return context


class CustomAdminDashBoardView(AdminRequiredMixin, TemplateView):
    template_name = 'suka_admin/dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Conteo total de productos, entregas, etc
        context['total_products'] = Product.objects.count()
        context['total_delivery_pending'] = Delivery.objects.filter(status='pending').count()
        context['total_delivery_delivered'] = Delivery.objects.filter(status='delivered').count()


        # Envios entregados por mes (como antes)
        envios_por_mes = [0]*12
        entregas = (
            Delivery.objects
            .filter(status='delivered', delivery_date__isnull=False)
            .annotate(mes=ExtractMonth('delivery_date'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        )
        for entrega in entregas:
            mes = entrega['mes']
            total = entrega['total']
            envios_por_mes[mes - 1] = total
        context['envios_por_mes'] = envios_por_mes

        # Conteo órdenes por estado (sin delivered)
        ordenes_por_estado = Order.objects.values('status').annotate(total=Count('id'))
        # Crear un dict para pasar al template con claves como 'pending', 'confirmed', etc
        ordenes_dict = {status: 0 for status, _ in Order.STATUS_CHOICES}
        for item in ordenes_por_estado:
            ordenes_dict[item['status']] = item['total']
        context['ordenes_por_estado'] = ordenes_dict

        return context






