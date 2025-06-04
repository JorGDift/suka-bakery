from django.db import models
from django.db.models import F, Sum, Case, When, Value, DecimalField, OuterRef, Subquery

class OrderManager(models.Manager):
    def with_order_totals(self):
        """
        Retorna las órdenes con sus totales precalculados incluyendo envío
        """
        detail_total = (
            F('details__product__price') +
            F('details__cake_size__price') +
            F('details__decoration_price')
        ) * F('details__quantity')

        return self.annotate(
            subtotal=Sum(detail_total),
            delivery_cost=Case(
                When(delivery__isnull=False, then=F('delivery__cost')),
                default=Value(0),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).annotate(
            order_total=F('subtotal') + F('delivery_cost')
        ).prefetch_related(
            'details',
            'details__product',
            'details__cake_size',
            'delivery'
        )


    def get_orders_by_status(self, status):
        """
        Obtiene órdenes por estado con sus totales
        """
        return self.with_order_totals().filter(status=status)

    def get_orders_with_delivery(self):
        """
        Obtiene solo órdenes que tienen envío
        """
        return self.with_order_totals().filter(delivery__isnull=False)

    def get_orders_by_delivery_status(self, delivery_status):
        """
        Obtiene órdenes por estado de envío
        """
        return self.with_order_totals().filter(delivery__status=delivery_status)

    def search_orders(self, query):
        """
        Búsqueda de órdenes incluyendo dirección de envío
        """
        from django.db.models import Q
        return self.with_order_totals().filter(
            Q(order_number__icontains=query) |
            Q(details__product__name__icontains=query) |
            Q(delivery__street__icontains=query) |
            Q(delivery__neighborhood__icontains=query)
        ).distinct()