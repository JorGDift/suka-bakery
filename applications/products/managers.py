# models.py
from django.db import models


class CategoryManager(models.Manager):
    """Manager personalizado para Categorías."""


class ProductManager(models.Manager):
    """Manager personalizado para Productos."""
    def filter_products(self, product_name='', product_category=''):
        """Filtrar productos por nombre y/o categoría"""
        queryset = self.get_queryset()

        if product_name:
            queryset = queryset.filter(name__icontains=product_name)
        if product_category:
            queryset = queryset.filter(category=product_category)

        return queryset