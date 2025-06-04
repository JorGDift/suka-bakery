from django.contrib import admin
from .models import Product, ProductImage, Category, CakeFlavor, CakeSize

# Register your models here.
@admin.register(CakeFlavor)
class FlavorAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_slice', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(CakeSize)
class CakeSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_people')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Muestra un espacio adicional para agregar imágenes en el mismo formulario

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_at')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    inlines = [ProductImageInline]  # Permite agregar imágenes desde la página de productos