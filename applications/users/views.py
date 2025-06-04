# usuarios y autenticación
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from applications.core.views import AdminRequiredMixin


from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404

from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, FormView, DeleteView
from .models import User
from .forms import UserCreateOrUpdateForm, UserSearchForm, UserLoginForm, PasswordChangeForm, UserUpdateForm


# Create your views here.
class UserLoginView(FormView):
    template_name = 'suka_admin/users/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('coreApp:custom-admin-dashboard')

    def form_valid(self, form):
        # se authentica el usuario
        user = authenticate(
            mail=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
        )
        login(self.request, user)

        print(f"Usuario {user} ha iniciado sesión")
        return super(UserLoginView, self).form_valid(form)

    def form_invalid(self, form):
        # Agregar error general
        form.add_error(None, "Email o contraseña incorrectos")
        return super().form_invalid(form)


class UserLogoutView(View):
    def get(self, requets, *args, **kargs):
        logout(requets)

        return HttpResponseRedirect(
            reverse('usersApp:custom-admin-login')
        )


class CustomAdminUserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreateOrUpdateForm
    template_name = 'suka_admin/users/user_create.html'
    success_url = reverse_lazy('usersApp:custom-admin-user-list')


    def form_valid(self, form):
        try:
            user = form.save(commit=False)
            user.is_active = form.cleaned_data.get('is_active', True)
            user.is_staff = form.cleaned_data.get('is_staff', True)
            user.is_superuser = form.cleaned_data.get('is_superuser', True)
            user.save()

            messages.success(self.request,f'¡El usuario {user} ha sido creado exitosamente!')
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f'Ocurrió un error al crear el usuario: {str(e)}')
            return self.form_invalid(form)


    def form_invalid(self, form):
        # Mostrar errores específicos del formulario
        for field, errors in form.errors.items():
            field_label = form.fields[field].label if field in form.fields else field
            for error in errors:
                messages.error(self.request, f"{field_label}: {error}")

        return self.render_to_response(self.get_context_data(form=form))


class CustomAdminUserListView(AdminRequiredMixin, ListView):
    model = User
    context_object_name = 'user_list'
    template_name = 'suka_admin/users/user_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['UserSearchForm'] = UserSearchForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        email = self.request.GET.get('mail')
        return User.objects.search_users_by_email(email)


class CustomAdminUserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm  # Usa el nuevo formulario
    template_name = 'suka_admin/users/user_update.html'
    success_url = reverse_lazy('usersApp:custom-admin-user-list')

    def form_valid(self, form):
        try:
            user = form.save(commit=False)

            # Manejo de avatar
            if form.cleaned_data.get('avatar-clear') and user.avatar:
                user.avatar.delete(save=False)
                user.avatar = None

            user.save()
            messages.success(self.request, f'¡Usuario {user} actualizado exitosamente!')
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f'Error al actualizar: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        # Mostrar errores específicos del formulario
        for field, errors in form.errors.items():
            field_label = form.fields[field].label if field in form.fields else field
            for error in errors:
                messages.error(self.request, f"{field_label}: {error}")
                print(f"{field_label}: {error}")
        return super().form_invalid(form)


class AdminPasswordChangeView(View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        try:
            if not new_password or not confirm_password:
                raise ValidationError("Ambos campos de contraseña son requeridos")

            if new_password != confirm_password:
                raise ValidationError("Las contraseñas no coinciden")

            validate_password(new_password, user)

            user.password = make_password(new_password)
            user.save()

            messages.success(request, 'Contraseña cambiada exitosamente')
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')

        return redirect('usersApp:custom-admin-user-update', pk=pk)


class CustomAdminUserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy('usersApp:custom-admin-user-list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        user = self.object
        # Si pasa las validaciones, proceder
        messages.success(request, 'El usuario ha sido eliminado exitosamente.')
        return super().post(request, *args, **kwargs)