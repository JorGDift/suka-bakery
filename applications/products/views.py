from django.contrib import messages
import json

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect


from  applications.core.views import AdminRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from .models import Product, ProductImage, Category, CakeFlavor, CakeSize
from .forms import SearchProductForm, CreateProductForm, CategoryCreateForm, CakeFlavorCreateForm, CakeSizeForm

# Create your views here.

############################################
############ PRODUCTOS #####################
############################################
class CustomAdminCreateProductView(AdminRequiredMixin, CreateView):
    model = Product
    form_class = CreateProductForm
    template_name = 'suka_admin/product/product_create.html'
    success_url = reverse_lazy('productApp:product-list')

    def form_valid(self, form):
        """Se ejecuta cuando el formulario es válido."""
        # Guardar el producto
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()

        # Procesar imágenes
        for image in self.request.FILES.getlist('images'):
            ProductImage.objects.create(
                product=self.object,
                image=image
            )

        messages.success(
            self.request,
            f'¡El producto {self.object.name} ha sido creado exitosamente!'
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """Se ejecuta cuando el formulario es inválido."""
        messages.error(
            self.request,
            'Por favor corrige los errores en el formulario.'
        )
        return super().form_invalid(form)


class CustomAdminProductListView(AdminRequiredMixin, ListView):
    template_name = 'suka_admin/product/product_list.html'
    model = Product
    context_object_name = 'product_list'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        """Añadir contexto para el template"""
        context = super().get_context_data(**kwargs)

        # Obtener los parámetros de búsqueda
        product_name = self.request.GET.get('productName', '').strip()
        product_category_id = self.request.GET.get('productCategory')

        # Inicializar categoría como None
        product_category_name = None

        # Si existe un ID de categoría, obtener su nombre
        if product_category_id:
            try:
                category = Category.objects.get(id=product_category_id)
                product_category_name = category.name
            except Category.DoesNotExist:
                product_category_name = None

        # Parámetros para preservar las búsquedas en el template
        context['query_params'] = {
            'product_name': product_name,
            'product_category': product_category_name,  # Ahora contiene el nombre de la categoría
        }

        # Pasar formulario de búsqueda al template
        context['SearchProductForm'] = SearchProductForm(self.request.GET)

        return context

    def get_queryset(self):
        """Filtrar los productos con el manager personalizado"""
        # Obtener los parámetros de la URL
        product_name = self.request.GET.get('productName', '').strip()
        product_category = self.request.GET.get('productCategory')

        # Utilizar el Manager para aplicar los filtros
        return Product.objects.filter_products(product_name, product_category)


class CustomAdminProductUpdateView(AdminRequiredMixin, UpdateView):
    template_name = 'suka_admin/product/product_update.html'
    model = Product
    form_class = CreateProductForm
    success_url = reverse_lazy('productApp:product-list')

    def form_valid(self, form):
        response = super().form_valid(form)

        # Manejar las imágenes eliminadas
        images_to_delete = self.request.POST.get('images_to_delete')
        if images_to_delete:
            # Convertir la cadena de IDs a lista de enteros
            removed_ids = [int(img_id) for img_id in images_to_delete.split(',') if img_id.strip().isdigit()]
            if removed_ids:
                ProductImage.objects.filter(id__in=removed_ids, product=self.object).delete()

        # Manejar las nuevas imágenes
        files = self.request.FILES.getlist('images')
        for file in files:
            ProductImage.objects.create(
                product=self.object,
                image=file
            )

        messages.success(self.request, 'El producto ha sido actualizado exitosamente.')
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Por favor corrige los errores en el formulario.'
        )
        return super().form_invalid(form)


class CustomAdminProductDeletView(AdminRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('productApp:product-list')

    def post(self, request, *args, **kwargs):
        messages.success(request, 'El producto ha sido eliminado exitosamente.')
        return super().post(request, *args, **kwargs)



############################################
############ CATEGORÍAS ####################
############################################

class CustomAdminCreateCategoryView(AdminRequiredMixin, CreateView):
    template_name = 'suka_admin/category/category_create.html'
    form_class = CategoryCreateForm
    success_url = reverse_lazy('productApp:admin-category-list')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(
                self.request,
                f'¡La categoría {self.object.name} ha sido creada exitosamente!'
            )
            return response
        except Exception as e:
            messages.error(self.request, f'Error al crear la categoría: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        # Mostrar errores específicos
        for field, errors in form.errors.items():
            if field == '__all__':
                # Errores generales del formulario
                for error in errors:
                    messages.error(self.request, f"Error: {error}")
            else:
                # Errores específicos de cada campo
                field_name = form.fields[field].label or field
                for error in errors:
                    messages.error(
                        self.request,
                        f"Error en {field_name}: {error}"
                    )

        return super().form_invalid(form)


class CustomAdminCategoryListView(AdminRequiredMixin, ListView):
    template_name = 'suka_admin/category/category_list.html'
    model = Category
    context_object_name = 'category_list'


class CustomAdminCategoryUpdateView(AdminRequiredMixin, UpdateView):
    template_name = 'suka_admin/category/category_update.html'
    form_class = CategoryCreateForm
    model = Category
    success_url = reverse_lazy('productApp:admin-category-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'¡La categoría {self.object.name} ha sido actualizada exitosamente!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


class CustomAdminCategoryDeletedView(AdminRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('productApp:admin-category-list')

    def can_delete_category(self, category):
        """
            Método personalizado para validar si se puede eliminar la categoría
            Retorna tuple (can_delete: bool, error_message: str)
        """
        # Validación 1: Productos asociados
        if category.products.exists():
            product_count = category.products.count()
            return False, f'No se puede eliminar la categoría porque tiene {product_count} producto(s) asociado(s).'

        return True, ''

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Ejecutar validaciones
        can_delete, error_message = self.can_delete_category(self.object)

        if not can_delete:
            messages.error(request, error_message)
            return redirect(self.success_url)

        # Si pasa las validaciones, proceder
        messages.success(request, 'La categoría ha sido eliminada exitosamente.')
        return super().post(request, *args, **kwargs)


############################################
############ SABORES ######################
############################################

class CustomAdminFlavorsCreateView(AdminRequiredMixin, CreateView):
    template_name = 'suka_admin/flavors/flavor_create.html'
    model = CakeFlavor
    form_class = CakeFlavorCreateForm
    success_url = reverse_lazy('productApp:admin-flavor-list')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, f'¡El sabor {self.object.name} ha sido creado exitosamente!')
            return response
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


class CustomAdminFlavorsListView(AdminRequiredMixin, ListView):
    template_name = 'suka_admin/flavors/flavor_list.html'
    model = CakeFlavor
    context_object_name = 'flavor_list'

class CustomAdminFlavorsUpdateView(AdminRequiredMixin, UpdateView):
    template_name = 'suka_admin/flavors/flavor_update.html'
    model = CakeFlavor
    form_class = CakeFlavorCreateForm
    success_url = reverse_lazy('productApp:admin-flavor-list')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, f'¡El sabor {self.object.name} ha sido actualizado exitosamente!')
            return response
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


class CustomAdminFlavorsDeletedView(AdminRequiredMixin, DeleteView):
    model = CakeFlavor
    success_url = reverse_lazy('productApp:admin-flavor-list')

    def can_delete_flavor(self, flavor):
        """
            Método personalizado para validar si se puede eliminar el sabor
            Retorna tuple (can_delete: bool, error_message: str)
        """
        # Validación principal: Productos asociados (según tu modelo)
        if flavor.products.exists():
            product_count = flavor.products.count()
            return False, f'No se puede eliminar el sabor porque tiene {product_count} producto(s) asociado(s).'


        return True, ''

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Ejecutar validaciones
        can_delete, error_message = self.can_delete_flavor(self.object)

        if not can_delete:
            messages.error(request, error_message)
            return redirect(self.success_url)

        # Si pasa las validaciones, proceder
        messages.success(request, 'El sabor ha sido eliminado exitosamente.')
        return super().post(request, *args, **kwargs)


############################################
############ TAMAÑOS ######################
############################################
class CustomAdminSizesCreateView(AdminRequiredMixin, CreateView):
    template_name = 'suka_admin/sizes/sizes_create.html'
    model = CakeSize
    form_class = CakeSizeForm
    success_url = reverse_lazy('productApp:admin-size-list')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, f'¡El tamaño {self.object.name} ha sido creado exitosamente!')
            return response
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)

class CustomAdminSizesListView(AdminRequiredMixin, ListView):
    template_name = 'suka_admin/sizes/sizes_list.html'
    model = CakeSize
    context_object_name = 'size_list'

class CustomAdminSizeUpdateView(AdminRequiredMixin, UpdateView):
    template_name = 'suka_admin/sizes/zise_update.html'
    model = CakeSize
    form_class = CakeSizeForm
    success_url = reverse_lazy('productApp:admin-size-list')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, f'¡El tamaño {self.object.name} ha sido actualizado exitosamente!')
            return response
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


class CustomAdminSizeDeletedView(AdminRequiredMixin, DeleteView):
    model = CakeSize
    success_url = reverse_lazy('productApp:admin-size-list')

    def can_delete_size(self, size):
        """
            Método personalizado para validar si se puede eliminar el tamaño
            Retorna tuple (can_delete: bool, error_message: str)
        """
        # Validación principal: Productos asociados (según tu modelo)
        if size.products.exists():
            product_count = size.products.count()
            return False, f'No se puede eliminar el tamaño porque tiene {product_count} producto(s) asociado(s).'

        return True, ''

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Ejecutar validaciones
        can_delete, error_message = self.can_delete_size(self.object)

        if not can_delete:
            messages.error(request, error_message)
            return redirect(self.success_url)

        # Si pasa las validaciones, proceder
        messages.success(request, 'El tamaño ha sido eliminado exitosamente.')
        return super().post(request, *args, **kwargs)