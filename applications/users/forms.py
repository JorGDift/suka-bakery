import os
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class UserLoginForm(forms.Form):
    email = forms.CharField(
        label='',
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Correo',
                'class': 'form-control',
            }
        )
    )
    password = forms.CharField(
        label=' ',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '***********',
                'class': 'form-control',
            }
        )
    )

    def clean(self):
        cleaned_data = super(UserLoginForm, self).clean()
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        if not authenticate(mail=email, password=password):
            raise forms.ValidationError('Los datos de usuario no son correctos')

        return self.cleaned_data


class UserCreateOrUpdateForm(UserCreationForm):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Mínimo 8 caracteres, debe incluir letras y números."
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ('name', 'last_name', 'mail', 'phone', 'avatar', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mail': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nombre',
            'last_name': 'Apellido',
            'mail': 'Correo electrónico',
            'phone': 'Teléfono',
            'avatar': 'Foto de perfil',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("El nombre es obligatorio.")
        if len(name) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', name):
            raise ValidationError("El nombre solo puede contener letras y espacios.")
        return name.strip()

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:  # Opcional pero si se ingresa, validar
            if len(last_name) < 2:
                raise ValidationError("El apellido debe tener al menos 2 caracteres.")
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', last_name):
                raise ValidationError("El apellido solo puede contener letras y espacios.")
        return last_name.strip() if last_name else last_name

    def clean_mail(self):
        mail = self.cleaned_data.get('mail')
        if not mail:
            raise ValidationError("El correo electrónico es obligatorio.")

        # Validación básica de formato de email
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', mail):
            raise ValidationError("Ingrese un correo electrónico válido.")

        # Validar unicidad (excepto para el usuario actual en actualización)
        if self.instance.pk:  # Si es una actualización
            if User.objects.filter(mail=mail).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Este correo electrónico ya está registrado.")
        else:  # Si es creación
            if User.objects.filter(mail=mail).exists():
                raise ValidationError("Este correo electrónico ya está registrado.")

        return mail.lower()

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:  # Opcional pero si se ingresa, validar
            # Eliminar espacios, guiones, paréntesis
            phone = re.sub(r'[\s\-\(\)]', '', phone)
            if not phone.isdigit():
                raise ValidationError("El teléfono solo puede contener números y signos de formato.")
            if len(phone) < 8:
                raise ValidationError("El teléfono debe tener al menos 8 dígitos.")
        return phone

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Validar tamaño máximo (5MB)
            max_size = 5 * 1024 * 1024
            if avatar.size > max_size:
                raise ValidationError("La imagen no puede superar los 5MB.")

            # Validar extensiones
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            extension = os.path.splitext(avatar.name)[1].lower()
            if extension not in valid_extensions:
                raise ValidationError("Formato de imagen no válido. Use JPG, PNG o GIF.")
        return avatar

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if password1.isdigit():
            raise ValidationError("La contraseña no puede ser completamente numérica.")
        # Validar complejidad
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("La contraseña debe contener al menos una mayúscula.")
        if not re.search(r'[a-z]', password1):
            raise ValidationError("La contraseña debe contener al menos una minúscula.")
        if not re.search(r'[0-9]', password1):
            raise ValidationError("La contraseña debe contener al menos un número.")
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")

        return cleaned_data


class UserUpdateForm(UserChangeForm):
    # Elimina completamente los campos de contraseña
    password = None

    class Meta:
        model = User
        fields = ('name', 'last_name', 'mail', 'phone', 'avatar', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mail': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegúrate de eliminar cualquier campo relacionado con contraseñas
        if 'password' in self.fields:
            del self.fields['password']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("El nombre es obligatorio.")
        if len(name) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', name):
            raise ValidationError("El nombre solo puede contener letras y espacios.")
        return name.strip()

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:  # Opcional pero si se ingresa, validar
            if len(last_name) < 2:
                raise ValidationError("El apellido debe tener al menos 2 caracteres.")
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', last_name):
                raise ValidationError("El apellido solo puede contener letras y espacios.")
        return last_name.strip() if last_name else last_name

    def clean_mail(self):
        mail = self.cleaned_data.get('mail')
        if not mail:
            raise ValidationError("El correo electrónico es obligatorio.")

        # Validación básica de formato de email
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', mail):
            raise ValidationError("Ingrese un correo electrónico válido.")

        # Validar unicidad (excepto para el usuario actual en actualización)
        if self.instance.pk:  # Si es una actualización
            if User.objects.filter(mail=mail).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Este correo electrónico ya está registrado.")
        else:  # Si es creación
            if User.objects.filter(mail=mail).exists():
                raise ValidationError("Este correo electrónico ya está registrado.")

        return mail.lower()

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:  # Opcional pero si se ingresa, validar
            # Eliminar espacios, guiones, paréntesis
            phone = re.sub(r'[\s\-\(\)]', '', phone)
            if not phone.isdigit():
                raise ValidationError("El teléfono solo puede contener números y signos de formato.")
            if len(phone) < 8:
                raise ValidationError("El teléfono debe tener al menos 8 dígitos.")
        return phone

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Validar tamaño máximo (5MB)
            max_size = 5 * 1024 * 1024
            if avatar.size > max_size:
                raise ValidationError("La imagen no puede superar los 5MB.")

            # Validar extensiones
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            extension = os.path.splitext(avatar.name)[1].lower()
            if extension not in valid_extensions:
                raise ValidationError("Formato de imagen no válido. Use JPG, PNG o GIF.")
        return avatar

        return cleaned_data


class PasswordChangeForm(forms.Form):
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label="Confirmación",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')

        if p1 and p2 and p1 != p2:
            raise ValidationError("Las contraseñas no coinciden")
        return cleaned_data


class UserSearchForm(forms.Form):
    mail = forms.EmailField(
        label="Correo electrónico",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el correo electrónico',
        }),
    )

