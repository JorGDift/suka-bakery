from django.contrib import admin
from .models import Order, OrderDetail, Delivery

class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 1  # Número de formularios vacíos que se mostrarán
    fields = ['product', 'cake_flavor', 'cake_size', 'decoration_price', 'quantity']
    readonly_fields = ['created_at', 'updated_at']

class DeliveryInline(admin.StackedInline):
    model = Delivery
    can_delete = False
    max_num = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'status', 'created_at', 'total_items', 'total']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'subtotal', 'total']
    inlines = [OrderDetailInline, DeliveryInline]

    fieldsets = (
        ('Información de la Orden', {
            'fields': ('order_number', 'status')
        }),
        ('Información Temporal', {
            'fields': ('created_at', 'updated_at')
        }),
        ('Información Financiera', {
            'fields': ('subtotal', 'total')
        }),
    )

    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = 'Subtotal'

    def total(self, obj):
        return obj.total
    total.short_description = 'Total'

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'delivery_date', 'cost']
    list_filter = ['status', 'delivery_date']
    search_fields = ['order__order_number']
    readonly_fields = ['created_at', 'updated_at']