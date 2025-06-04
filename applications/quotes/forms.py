from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils import timezone
from decimal import Decimal


from applications.products.models import Product, CakeFlavor, CakeSize
from .models import Order, OrderDetail, Delivery


class QuotationCreateForm(forms.Form):
    # Campos de OrderDetail
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=True,
        label="Producto",
        widget=forms.Select(attrs={
            'class': 'form-select mb-3',
            'placeholder': 'Seleccione un producto'
        })
    )

    cake_flavor = forms.ModelChoiceField(
        queryset=CakeFlavor.objects.all(),
        required=True,
        label="Sabor del Pastel",
        widget=forms.Select(attrs={
            'class': 'form-select mb-3',
            'placeholder': 'Seleccione un sabor'
        })
    )

    cake_size = forms.ModelChoiceField(
        queryset=CakeSize.objects.all(),
        required=True,
        label="Tamaño del Pastel",
        widget=forms.Select(attrs={
            'class': 'form-select mb-3',
            'placeholder': 'Seleccione un tamaño'
        })
    )

    decoration_price = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        initial=0.00,
        required=False,
        label="Precio de Decoración",
        widget=forms.NumberInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Ingrese el precio de decoración',
            'step': '0.01',
            'min': '0'
        })
    )

    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Cantidad",
        widget=forms.NumberInput(attrs={
            'class': 'form-control mb-3',
        })
    )

    # Campos de Delivery
    street = forms.CharField(
        max_length=255,
        required=False,
        label="Calle",
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Ingrese la calle'
        })
    )

    neighborhood = forms.CharField(
        max_length=100,
        required=False,
        label="Colonia o Barrio",
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Ingrese la colonia o barrio'
        })
    )

    ext_number = forms.CharField(
        max_length=10,
        required=False,
        label="Número Exterior",
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Número exterior'
        })
    )

    int_number = forms.CharField(
        max_length=10,
        required=False,
        label="Número Interior (opcional)",
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Número interior (opcional)'
        })
    )

    cost = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        label="Costo de Envío",
        widget=forms.NumberInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Ingrese el costo de envío',
            'step': '0.01',
            'min': '0'
        })

    )

    delivery_date = forms.DateTimeField(
        required=False,
        label="Fecha de Entrega",
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control mb-3'
        })
    )

    def clean_quantity(self):
        """Validación personalizada para `quantity`."""
        quantity = self.cleaned_data.get("quantity")
        if quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")
        return quantity

    def clean(self):
        """Validación general del formulario."""
        cleaned_data = super().clean()
        decoration_price = cleaned_data.get("decoration_price")
        cost = cleaned_data.get("cost")

        if decoration_price is not None and decoration_price < 0:
            raise ValidationError("El precio de decoración no puede ser negativo.")

        if cost is not None and cost < 0:
            raise ValidationError("El costo de envío no puede ser negativo.")

        return cleaned_data


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']

        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }

OrderDetailFormSet = inlineformset_factory(
    Order,
    OrderDetail,
    fields=['product', 'cake_flavor', 'cake_size', 'decoration_price', 'quantity'],
    extra=0,
    can_delete=True,
    widgets={
        'product': forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Selecciona un producto'
        }),
        'cake_flavor': forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Selecciona sabor'
        }),
        'cake_size': forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Selecciona tamaño'
        }),
        'decoration_price': forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0'
        }),
        'quantity': forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1',
            'min': '1',
            'step': '1'
        }),
    },
    labels={
        'product': 'Producto',
        'cake_flavor': 'Sabor del Pastel',
        'cake_size': 'Tamaño del Pastel',
        'decoration_price': 'Precio de Decoración',
        'quantity': 'Cantidad',
    }
)

class QuotationFilterForm(forms.Form):
    order_number = forms.CharField(
        required=False,
        label='Número de Orden',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: ORD-20250519-023'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Order.STATUS_CHOICES,
        required=False,
        label='Estado',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class DeliveryCreateForm(forms.ModelForm):
    order = forms.ModelChoiceField(
        queryset=Order.objects.filter(delivery__isnull=True),
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'name': 'order'
        }),
        required=True,
        label='Número de Orden'
    )


    class Meta:
        model = Delivery
        fields = [
            'street',
            'neighborhood',
            'ext_number',
            'int_number',
            'cost',
            'delivery_date'
        ]
        widgets = {
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la calle'
            }),
            'neighborhood': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la colonia'
            }),
            'ext_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número exterior'
            }),
            'int_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número interior (opcional)'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': '0.00',
                'min': '0',
                'step': '0.01'
            }),
            'delivery_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': True
            })
        }
        labels = {
            'street': 'Calle',
            'neighborhood': 'Colonia',
            'ext_number': 'Número Exterior',
            'int_number': 'Número Interior',
            'cost': 'Costo de envío',
            'delivery_date': 'Fecha y hora de entrega'
        }

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data['delivery_date']

        if delivery_date < timezone.now():
            raise forms.ValidationError('La fecha de entrega no puede ser en el pasado')

        if delivery_date > timezone.now() + timezone.timedelta(days=30):
            raise forms.ValidationError('La fecha de entrega no puede ser más de 30 días en el futuro')

        return delivery_date

    def clean_cost(self):
        cost = self.cleaned_data['cost']

        if cost < Decimal('0.00'):
            raise forms.ValidationError('El costo no puede ser negativo')

        return cost

    def clean(self):
        cleaned_data = super().clean()

        # Validar orden
        order = cleaned_data.get('order')
        if not order:
            raise forms.ValidationError({
                'order': 'Debe seleccionar una orden'
            })

        # Validar dirección
        street = cleaned_data.get('street')
        neighborhood = cleaned_data.get('neighborhood')
        ext_number = cleaned_data.get('ext_number')

        if not street:
            raise forms.ValidationError({
                'street': 'La calle es requerida'
            })

        if not neighborhood:
            raise forms.ValidationError({
                'neighborhood': 'La colonia es requerida'
            })

        if not ext_number:
            raise forms.ValidationError({
                'ext_number': 'El número exterior es requerido'
            })

        return cleaned_data


class DeliveryUpdateForm(forms.ModelForm):
    order = forms.ModelChoiceField(
        queryset=Order.objects.filter(delivery__isnull=True),
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'name': 'order'
        }),
        required=False,
        label='Número de Orden'
    )


    class Meta:
        model = Delivery
        fields = [
            'street',
            'neighborhood',
            'ext_number',
            'int_number',
            'cost',
            'status',
            'delivery_date'
        ]
        widgets = {
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la calle'
            }),
            'neighborhood': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la colonia'
            }),
            'ext_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número exterior'
            }),
            'int_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número interior (opcional)'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': '0.00',
                'min': '0',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'delivery_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': True
            })
        }
        labels = {
            'street': 'Calle',
            'neighborhood': 'Colonia',
            'ext_number': 'Número Exterior',
            'int_number': 'Número Interior',
            'cost': 'Costo de envío',
            'delivery_date': 'Fecha y hora de entrega'
        }

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data['delivery_date']

        # Si estás creando un nuevo registro
        if not self.instance.pk and delivery_date < timezone.now():
            raise forms.ValidationError('La fecha de entrega no puede ser en el pasado')

        # Siempre valida que no sea más de 30 días en el futuro
        if delivery_date > timezone.now() + timezone.timedelta(days=30):
            raise forms.ValidationError('La fecha de entrega no puede ser más de 30 días en el futuro')

        return delivery_date

    def clean_cost(self):
        cost = self.cleaned_data['cost']

        if cost < Decimal('0.00'):
            raise forms.ValidationError('El costo no puede ser negativo')

        return cost

    def clean(self):
        cleaned_data = super().clean()

        # Validar dirección
        street = cleaned_data.get('street')
        neighborhood = cleaned_data.get('neighborhood')
        ext_number = cleaned_data.get('ext_number')

        if not street:
            raise forms.ValidationError({
                'street': 'La calle es requerida'
            })

        if not neighborhood:
            raise forms.ValidationError({
                'neighborhood': 'La colonia es requerida'
            })

        if not ext_number:
            raise forms.ValidationError({
                'ext_number': 'El número exterior es requerido'
            })

        return cleaned_data


class DeliveryFilterForm(forms.Form):
    order_number = forms.CharField(
        required=False,
        label='Número de Orden',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: ORD-20250519-023'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'Selecciona un status')] + Delivery.STATUS_CHOICES,
        required=False,
        label='Estado',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )



