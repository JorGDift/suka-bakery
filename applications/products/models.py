from django.db import models

from .managers import ProductManager, CategoryManager
# Create your models here.
class CakeFlavor(models.Model):
    name = models.CharField(max_length=30, unique=True)
    price_per_slice = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Sabor de Pastel"
        verbose_name_plural = "Sabores de Pastel"
        ordering = ['-created_at']


class CakeSize(models.Model):
    name = models.CharField(max_length=30, unique=True)
    num_people = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.num_people} personas)"

    class Meta:
        verbose_name = "Tamaño de Pastel"
        verbose_name_plural = "Tamaños de Pastel"
        ordering = ['-created_at']

class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Asociamos el manager personalizado
    objects = CategoryManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['-created_at']


class Product(models.Model):
    name = models.CharField(unique=True, max_length=64)
    description = models.TextField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    price = models.DecimalField(max_digits=5, decimal_places=2)
    flavor = models.ForeignKey(CakeFlavor, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    size = models.ForeignKey(CakeSize, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # Asociamos el manager personalizado
    objects = ProductManager()

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"
