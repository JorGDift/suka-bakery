from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import UserManager

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField('Nombre', max_length=50)
    last_name = models.CharField('Apellido', max_length=50, null=True, blank=True)
    mail = models.EmailField('Correo', max_length=50, unique=True)
    avatar = models.ImageField('Foto', upload_to='users', blank=True, null=True)
    phone = models.CharField('Teléfono', max_length=15, blank=True, null=True)
    is_staff = models.BooleanField('Es staff', default=True)
    is_active = models.BooleanField('Es activo', default=True)
    created = models.DateTimeField('Creación', auto_now_add=True)
    upgrade = models.DateTimeField('Actualización', auto_now=True)

    # campo para inicio de sesión
    USERNAME_FIELD = 'mail'

    REQUIRED_FIELDS = [
        'name',
    ]

    objects = UserManager()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-created']

    def __str__(self):
        return str(self.name)