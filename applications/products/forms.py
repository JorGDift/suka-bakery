# forms.py
from django import forms

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from PIL import Image

from applications.products.models import Category, Product, CakeFlavor


class CreateProductForm(forms.ModelForm):
    """
    Formulario para la creación y edición de productos.
    Incluye campos para pasteles con sabores y tamaños específicos.
    """

    images = forms.FileField(
        label="Imágenes del producto",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'multiple': True,
            'accept': 'image/*',
            'aria-describedby': 'imageHelp',
            'hidden': True  # Para que funcione con tu drop-zone
        }),
        required=False,
        help_text="Selecciona hasta 4 imágenes (JPG, PNG o WebP)"
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'flavor', 'size', 'price']
        labels = {
            'name': 'Nombre del producto',
            'description': 'Descripción',
            'category': 'Categoría',
            'flavor': 'Sabor del pastel',
            'size': 'Tamaño del pastel',
            'price': 'Precio (MXN)'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Pastel de Chocolate Grande',
                'aria-describedby': 'nameHelp'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el producto...',
                'aria-describedby': 'descriptionHelp'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'aria-describedby': 'categoryHelp'
            }),
            'flavor': forms.Select(attrs={
                'class': 'form-select',
                'aria-describedby': 'flavorHelp'
            }),
            'size': forms.Select(attrs={
                'class': 'form-select',
                'aria-describedby': 'sizeHelp'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'aria-describedby': 'priceHelp'
            })
        }
        help_texts = {
            'name': 'Ingresa un nombre único para el producto',
            'description': 'Describe el producto',
            'category': 'Selecciona la categoría del producto',
            'flavor': 'Selecciona el sabor',
            'size': 'Selecciona el tamaño',
            'price': 'Ingresa el precio en pesos mexicanos'
        }
        error_messages = {
            'name': {
                'required': 'El nombre del producto es obligatorio',
                'unique': 'Ya existe un producto con este nombre',
                'max_length': 'El nombre no puede exceder los 64 caracteres'
            },
            'category': {
                'required': 'Debes seleccionar una categoría'
            },
            'price': {
                'required': 'El precio es obligatorio',
                'invalid': 'Ingresa un precio válido',
                'max_digits': 'El precio no puede exceder los 5 dígitos',
                'decimal_places': 'El precio debe tener 2 decimales'
            }
        }

    def clean_price(self):
        """
        Valida el campo precio:
        - Verifica que el precio sea coherente con el sabor y tamaño seleccionados
        - Aplica reglas de negocio para el cálculo de precios
        """
        price = self.cleaned_data.get('price')

        if price is not None:
            if price <= 0:
                raise forms.ValidationError("El precio debe ser mayor a 0")
            if price > 99999.99:
                raise forms.ValidationError("El precio no puede ser mayor a 99,999.99")

        return price

    def clean_category(self):
        category = self.cleaned_data.get('category')

        if not category:
            raise forms.ValidationError(
                "Debes seleccionar una categoría para el producto"
            )

        return category

    def clean_size(self):
        size = self.cleaned_data.get('size')
        if not size:
            raise forms.ValidationError(
                "Debes seleccionar un tamaño para el producto"
            )
        return size

    def clean_flavor(self):
        flavor = self.cleaned_data.get('flavor')
        if not flavor:
            raise forms.ValidationError(
                "Debes seleccionar un sabor para el producto"
            )
        return flavor


    def clean_description(self):
        """
        Valida la descripción del producto:
        - Verifica contenido apropiado
        - Asegura información completa
        """
        description = self.cleaned_data.get('description')
        category = self.cleaned_data.get('category')

        if description:
            # Verificar longitud máxima
            if len(description) > 255:
                raise forms.ValidationError("La descripción no puede exceder los 255 caracteres")
        return description

    def clean_images(self):
        """
        Validaciones exhaustivas para las imágenes:
        - Verifica el tamaño de cada archivo
        - Valida dimensiones mínimas y máximas
        - Comprueba la relación de aspecto
        - Verifica que sea una imagen válida
        - Limita el número máximo de imágenes
        - Valida el formato y calidad de la imagen
        """
        images = self.files.getlist('images')

        # Configuración de límites
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        MIN_WIDTH = 400
        MIN_HEIGHT = 400
        MAX_WIDTH = 4096
        MAX_HEIGHT = 4096
        MAX_IMAGES = 4
        ASPECT_RATIO_TOLERANCE = 0.1  # 10% de tolerancia

        if len(images) > MAX_IMAGES:
            raise forms.ValidationError(
                f"No puedes subir más de {MAX_IMAGES} imágenes por producto"
            )

        valid_images = []
        for image in images:
            # Validar tamaño del archivo
            if image.size > MAX_FILE_SIZE:
                raise forms.ValidationError(
                    f"La imagen '{image.name}' excede el tamaño máximo permitido de 5MB"
                )

            try:
                # Abrir la imagen para validaciones
                img = Image.open(image)

                # Verificar que la imagen no esté corrupta
                img.verify()
                img = Image.open(image)  # Reabrir después de verify()

                # Validar dimensiones
                width, height = img.size
                if width < MIN_WIDTH or height < MIN_HEIGHT:
                    raise forms.ValidationError(
                        f"La imagen '{image.name}' es demasiado pequeña. "
                        f"Dimensiones mínimas: {MIN_WIDTH}x{MIN_HEIGHT}px"
                    )

                if width > MAX_WIDTH or height > MAX_HEIGHT:
                    raise forms.ValidationError(
                        f"La imagen '{image.name}' es demasiado grande. "
                        f"Dimensiones máximas: {MAX_WIDTH}x{MAX_HEIGHT}px"
                    )

                # Validar relación de aspecto (cercana a 1:1)
                aspect_ratio = width / height
                if abs(1 - aspect_ratio) > ASPECT_RATIO_TOLERANCE:
                    raise forms.ValidationError(
                        f"La imagen '{image.name}' debe ser aproximadamente cuadrada. "
                        "La relación de aspecto debe estar entre 0.9 y 1.1"
                    )

                # Validar formato real del archivo
                format = img.format.lower()
                if format not in ['jpeg', 'jpg', 'png', 'webp']:
                    raise forms.ValidationError(
                        f"El formato de '{image.name}' no está permitido. "
                        "Use JPEG, PNG o WebP"
                    )

                # Verificar si la imagen está vacía o corrupta
                try:
                    img.transpose(Image.FLIP_LEFT_RIGHT)
                except Exception as e:
                    raise forms.ValidationError(
                        f"La imagen '{image.name}' parece estar corrupta o dañada"
                    )

                valid_images.append(image)

            except Exception as e:
                raise forms.ValidationError(
                    f"Error al procesar la imagen '{image.name}': {str(e)}"
                )

        return valid_images


class SearchProductForm(forms.Form):
    """Formulario para buscar productos."""
    productName = forms.CharField(
        label="Nombre del producto",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Pastel de Vainilla'
        })
    )

    productCategory = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Categoria del producto",
        empty_label="Selecciona una categoría",  # Opción default vacía
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-select'
        })
    )

#################################################
########## CATEGORÍAS ##########################
#################################################
class CategoryCreateForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

        labels = {
            'name': 'Nombre de la Categoría'
        }

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Pasteles, Galletas etc.'
            })
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError('Este campo es obligatorio.')

        # Validar longitud mínima
        if len(name.strip()) < 3:
            raise ValidationError('El nombre de la categoría debe tener al menos 3 caracteres.')

        # Validar longitud máxima
        if len(name) > 30:
            raise ValidationError('El nombre de la categoría no puede exceder los 30 caracteres.')

        # Validar que solo contenga letras, números y espacios
        if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ0-9\s]+$', name):
            raise ValidationError('El nombre solo puede contener letras, números y espacios.')

        # Validar que no exista una categoría con el mismo nombre
        existing_category = Category.objects.filter(name__iexact=name)
        if self.instance and self.instance.pk:
            existing_category = existing_category.exclude(pk=self.instance.pk)

        if existing_category.exists():
            raise ValidationError('Ya existe una categoría con este nombre.')

        # Validar espacios al inicio y final
        if name != name.strip():
            raise ValidationError('El nombre no puede comenzar ni terminar con espacios.')

        # Validar espacios múltiples
        if '  ' in name:
            raise ValidationError('El nombre no puede contener espacios múltiples.')

        # Convertir primera letra de cada palabra a mayúscula
        name = ' '.join(word.capitalize() for word in name.split())

        return name

    def clean(self):
        cleaned_data = super().clean()
        if self._errors:  # Si ya hay errores, no continuar con más validaciones
            return cleaned_data
        return cleaned_data


#################################################
########## SABORES ##########################
#################################################
class CakeFlavorCreateForm(forms.ModelForm):
    class Meta:
        model = CakeFlavor
        fields = ['name', 'price_per_slice']
        labels = {
            'name': 'Nombre del sabor',
            'price_per_slice': 'Precio por porción'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del sabor'
            }),
            'price_per_slice': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el precio por porción'
            })
        }

    def clean_name(self):
        name = self.cleaned_data['name']

        # Validar longitud mínima y máxima
        if len(name.strip()) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres')
        if len(name.strip()) > 30:
            raise forms.ValidationError('El nombre no puede exceder los 30 caracteres')

        # Validar caracteres especiales
        if not re.match("^[a-zA-ZÀ-ÿ\u00f1\u00d1\s]*$", name):
            raise forms.ValidationError('El nombre solo debe contener letras y espacios')

        # Validar espacios múltiples
        if '  ' in name:
            raise forms.ValidationError('El nombre no puede contener espacios múltiples')

        # Validar que no exista otro sabor con el mismo nombre (ignorando mayúsculas/minúsculas)
        if CakeFlavor.objects.filter(name__iexact=name).exists():
            if self.instance.pk:
                if CakeFlavor.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Ya existe un sabor con este nombre')
            else:
                raise forms.ValidationError('Ya existe un sabor con este nombre')

        return name.strip().title()  # Capitaliza cada palabra

    def clean_price_per_slice(self):
        price = self.cleaned_data['price_per_slice']

        # Validar que el precio sea mayor que 0
        if price <= 0:
            raise forms.ValidationError('El precio debe ser mayor que 0')

        # Validar precio máximo (considerando que es precio por porción)
        if price > 1000:
            raise forms.ValidationError('El precio por porción parece ser demasiado alto')

        # Validar que tenga máximo 2 decimales
        if price.as_tuple().exponent < -2:
            raise forms.ValidationError('El precio no puede tener más de 2 decimales')

        # Validar que el precio tenga un mínimo razonable
        if price < 1:
            raise forms.ValidationError('El precio por porción debe ser al menos 1')

        return price

    def clean(self):
        cleaned_data = super().clean()
        # validaciones que involucren múltiples campos
        return cleaned_data


#################################################
########## TAMAÑOS ##########################
#################################################
from django import forms
from .models import CakeSize
import re

class CakeSizeForm(forms.ModelForm):
    class Meta:
        model = CakeSize
        fields = ['name', 'num_people']
        labels = {
            'name': 'Nombre del tamaño',
            'num_people': 'Número de personas'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Mediano, Grande, etc.'
            }),
            'num_people': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de personas que sirve'
            })
        }

        error_messages = {
            'num_people': {
                'min_value': 'El número de personas debe ser mayor a 0',
                'required': 'Este campo es requerido'
            }
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        # Validar longitud mínima y máxima
        if len(name) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres')
        if len(name) > 30:
            raise forms.ValidationError('El nombre no puede exceder los 30 caracteres')

        # Validar caracteres especiales
        if not re.match("^[a-zA-ZñÑáéíóúÁÉÍÓÚ0-9\s]+$", name):
            raise forms.ValidationError('El nombre solo debe contener letras, números y espacios')

        # Validar que no exista otro tamaño con el mismo nombre
        if CakeSize.objects.filter(name__iexact=name).exclude(id=self.instance.id if self.instance else None).exists():
            raise forms.ValidationError('Ya existe un tamaño con este nombre')

        return name.title()

    def clean_num_people(self):
        num_people = self.cleaned_data['num_people']

        # Validar rango razonable de personas
        if num_people < 1:
            raise forms.ValidationError('El número de personas debe ser mayor a 0')
        if num_people > 500:
            raise forms.ValidationError('El número de personas parece demasiado alto (máximo 500)')

        # Validar números redondos
        if num_people % 1 != 0:
            raise forms.ValidationError('El número de personas debe ser un número entero')

        return num_people

    def clean(self):
        """Validaciones que requieren múltiples campos"""
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        num_people = cleaned_data.get('num_people')

        # Ejemplo de validación cruzada
        #if name and num_people:
            # Verificar coherencia entre nombre y número de personas
            #if 'individual' in name.lower() and num_people > 1:
                #raise forms.ValidationError(
                    #'Un pastel individual no puede ser para más de una persona'
                #)