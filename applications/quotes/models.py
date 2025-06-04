from django.db import models
from decimal import Decimal


from .managers import OrderManager
from applications.products.models import CakeFlavor, CakeSize, Product

# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'), # creo que debo quitar ese status
        ('canceled', 'Cancelado'),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Manager
    objects = OrderManager()

    @property
    def get_total_items(self):
        return sum(detail.quantity for detail in self.orderdetail_set.all())

    @property
    def get_subtotal(self):
        return sum(detail.item_total for detail in self.orderdetail_set.all())

    @property
    def subtotal(self):
        """Calcula el subtotal de la orden sumando todos los detalles"""
        total = Decimal('0.00')
        for detail in self.details.all():
            # Precio base del producto + precio por sabor + precio de decoración
            item_price = (detail.product.price +
                          detail.cake_flavor.price_per_slice +
                          detail.decoration_price)
            total += item_price * detail.quantity
        return total

    @property
    def total_items(self):
        """Retorna la cantidad total de items en la orden"""
        return sum(detail.quantity for detail in self.details.all())

    @property
    def shipping_cost(self):
        """Retorna el costo de envío multiplicado por la cantidad de pasteles"""
        if hasattr(self, 'delivery'):
            return self.delivery.cost * self.total_items
        return Decimal('0.00')

    @property
    def total(self):
        """Calcula el total de la orden incluyendo el envío"""
        return self.subtotal + self.shipping_cost

    def save(self, *args, **kwargs):
        # Si el objeto es nuevo y no tiene clave primaria
        if not self.pk:
            super().save(*args, **kwargs)  # Guarda para generar `created_at` y obtener `id`

            # Generar el número de pedido
            last_order = Order.objects.order_by('-id').first()
            next_id = last_order.id + 1 if last_order else 1
            self.order_number = f"ORD-{self.created_at.strftime('%Y%m%d')}-{next_id:03d}"

        # Hacer el guardado final, independientemente si es nuevo o no
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at']


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cake_flavor = models.ForeignKey(CakeFlavor, on_delete=models.CASCADE)
    cake_size = models.ForeignKey(CakeSize, on_delete=models.CASCADE)
    decoration_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def item_unit_price(self):
        """Calcula el precio por unidad (base + sabor + decoración)"""
        return (self.product.price +
                self.cake_flavor.price_per_slice +
                self.decoration_price)

    @property
    def item_total(self):
        """Calcula el precio total por item (precio unitario × cantidad)"""
        return self.item_unit_price * self.quantity


    def __str__(self):
        return f"Pedido {self.order.order_number}: {self.product.name} - {self.cake_flavor.name} ({self.cake_size.name})"

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('canceled', 'Cancelado'),
        ('delivered', 'Enviado'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    neighborhood = models.CharField(max_length=100, blank=True, null=True)
    ext_number = models.CharField(max_length=10, blank=True, null=True)
    int_number = models.CharField(max_length=10, blank=True, null=True)
    cost = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Entrega para {self.order.order_number}"

    class Meta:
        ordering = ['-created_at']



