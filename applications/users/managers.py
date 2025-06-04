from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def _create_user(self, mail, name, last_name, phone, password, is_staff, is_superuser, is_active, **extra_fields):
        if not mail:
            raise ValueError('El correo electrónico es obligatorio')

        user = self.model(
            mail=self.normalize_email(mail),
            name=name,
            last_name=last_name,
            phone=phone,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mail, name=None, last_name=None, phone=None, password=None, **extra_fields):
        return self._create_user(mail, name, last_name, phone, password, False, False, True, **extra_fields)

    def create_superuser(self, mail, name, last_name=None, phone=None, password=None, **extra_fields):
        return self._create_user(mail, name, last_name, phone, password, True, True, True, **extra_fields)

    def search_users_by_email(self, e_mail=None):
        queryset = self.get_queryset()
        if e_mail:
            return queryset.filter(mail__icontains=e_mail)
        return queryset
