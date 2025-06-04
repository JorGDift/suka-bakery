from django.contrib import messages
from django.core.exceptions import ValidationError
from django.forms import formset_factory
from django.views.generic import ListView, CreateView, View, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, render
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect


from applications.core.views import AdminRequiredMixin
from .forms import DeliveryCreateForm, DeliveryUpdateForm, QuotationCreateForm, DeliveryFilterForm, QuotationFilterForm, OrderUpdateForm, OrderDetailFormSet
from .models import Delivery, Order, OrderDetail


def get_order_details(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)

        # Obtener los detalles de la orden usando el nombre correcto de la relación
        details = OrderDetail.objects.filter(order=order)

        # Calcular totales
        total_items = sum(detail.quantity for detail in details)
        subtotal = float(order.total or 0) - float(order.shipping_cost or 0)

        data = {
            'order_number': order.id,  # o el campo que uses para el número de orden
            'total_items': total_items,
            'subtotal': f"{subtotal:.2f}",
            'shipping_cost': f"{float(order.shipping_cost or 0):.2f}",
            'total': f"{float(order.total or 0):.2f}",
            'status': getattr(order, 'status', 'pending')  # valor por defecto 'pending' si no existe status
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


class DeliveryCreateView(AdminRequiredMixin, CreateView):
    template_name = 'suka_admin/delivery/delivery_create.html'
    model = Delivery
    form_class = DeliveryCreateForm
    success_url = reverse_lazy('quoteApp:suka_admin_delivery_list')

    def form_valid(self, form):
        try:
            # Crear la instancia pero no guardar todavía
            delivery = form.save(commit=False)

            # Asignar explícitamente la orden
            delivery.order = form.cleaned_data['order']
            print("Order asignada:", delivery.order)

            delivery.status = 'pending' # Establecer status como True

            # Guardar
            delivery.save()
            messages.success(self.request, 'Envío creado exitosamente')
            return super().form_valid(form)
        except Exception as e:
            print("Error específico:", str(e))
            print("Tipo de error:", type(e))
            messages.error(self.request, f'Error al crear el envío: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class DeliveryListView(AdminRequiredMixin, ListView):
    template_name = 'suka_admin/delivery/delivery_list.html'
    model = Delivery
    context_object_name = 'delivery_list'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('order')
        form = DeliveryFilterForm(self.request.GET)

        if form.is_valid():
            if order_number := form.cleaned_data.get('order_number'):
                queryset = queryset.filter(order__order_number__icontains=order_number)

            if status := form.cleaned_data.get('status'):
                queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeliveryFilterForm(self.request.GET or None)
        return context

class DeliveryUpdateView(AdminRequiredMixin, UpdateView):
    template_name = 'suka_admin/delivery/delivery_update.html'
    model = Delivery
    form_class = DeliveryUpdateForm
    success_url = reverse_lazy('quoteApp:suka_admin_delivery_list')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                delivery = form.save(commit=False)

                # Validación adicional
                if not delivery.order:
                    raise ValidationError("Se requiere una orden válida")

                # Mantener el estado original si ya existe
                if self.object.pk and self.object.status != 'pending':
                    delivery.status = self.object.status

                delivery.save()
                form.save_m2m()  # Importante si hay campos ManyToMany

                messages.success(self.request, 'Envío actualizado exitosamente')
                return super().form_valid(form)

        except ValidationError as e:
            messages.error(self.request, str(e))
        except Exception as e:
            messages.error(self.request, f'Error al actualizar el envío: {str(e)}')

        return self.form_invalid(form)

    def form_invalid(self, form):
        error_list = [str(error) for field, errors in form.errors.items() for error in errors]
        messages.error(self.request, f'Errores en el formulario: {" ".join(error_list)}')
        return super().form_invalid(form)

class DeliveryDeleteView(AdminRequiredMixin, DeleteView):
    model = Delivery
    success_url = reverse_lazy('quoteApp:suka_admin_delivery_list')


class QuotationCreateView(AdminRequiredMixin, View):
    template_name = 'suka_admin/quotation/quotation_create.html'

    def get_formset_class(self):
        return formset_factory(
            QuotationCreateForm,
            extra=0,
            min_num=1,
            validate_min=True
        )

    def create_order(self):
        """Crea el objeto Order."""
        try:
            order = Order()
            order.save()
            return order
        except Exception as e:
            raise ValidationError(f"Error al crear la orden: {str(e)}")

    def create_order_detail(self, order, form_data):
        """Crea el detalle del pedido (OrderDetail)."""
        try:
            order_detail = OrderDetail(
                order=order,
                product=form_data['product'],
                cake_flavor=form_data['cake_flavor'],
                cake_size=form_data['cake_size'],
                decoration_price=form_data.get('decoration_price', 0),
                quantity=form_data['quantity']
            )
            order_detail.save()
            return order_detail
        except Exception as e:
            raise ValidationError(f"Error al crear el detalle de la orden: {str(e)}")

    def create_delivery(self, order, form_data):
        """Crea la entrega asociada al pedido (Delivery)."""
        try:
            delivery = Delivery(
                order=order,
                street=form_data['street'],
                neighborhood=form_data['neighborhood'],
                ext_number=form_data['ext_number'],
                int_number=form_data.get('int_number', ''),
                cost=form_data['cost'],
                delivery_date=form_data['delivery_date']
            )
            delivery.save()
            return delivery
        except Exception as e:
            raise ValidationError(f"Error al crear la entrega: {str(e)}")

    def get(self, request, *args, **kwargs):
        """Renderiza el formulario vacío al acceder con GET."""
        QuotationFormSet = self.get_formset_class()
        formset = QuotationFormSet()
        return render(request, self.template_name, {'formset': formset})

    def post(self, request, *args, **kwargs):
        """Procesa los datos al enviar el formulario con POST."""
        QuotationFormSet = self.get_formset_class()
        formset = QuotationFormSet(request.POST)

        if formset.is_valid():
            try:
                with transaction.atomic():
                    # 1. Crear la orden principal
                    order = self.create_order()

                    # 2. Verificar que al menos un formulario tiene datos de producto
                    if not any(form.cleaned_data for form in formset):
                        raise ValidationError("Se requiere al menos un producto")

                    # 3. Buscar datos de envío válidos en TODOS los formularios
                    delivery_data = None
                    for form in formset:
                        cleaned_data = form.cleaned_data
                        # Verificar si hay datos de envío (campos obligatorios)
                        if (
                                cleaned_data.get("street") and
                                cleaned_data.get("neighborhood") and
                                cleaned_data.get("ext_number")
                        ):
                            delivery_data = cleaned_data
                            break  # Usamos el primer formulario con envío válido

                    # 4. Crear los detalles de la orden (productos)
                    for form in formset:
                        if form.cleaned_data:  # Solo si el formulario tiene datos
                            self.create_order_detail(order, form.cleaned_data)

                    # 5. Crear el envío SOLO si hay datos válidos
                    if delivery_data:
                        self.create_delivery(order, delivery_data)

                    messages.success(request, f'Cotización { order } creada exitosamente')
                    return redirect('quoteApp:suka_admin_quotation_list')

            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Error al crear la cotización: {str(e)}')
                if 'order' in locals():  # Rollback manual si falla
                    order.delete()
        else:
            # Mostrar errores de validación del formset
            for form in formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error en {field}: {error}')

        return render(request, self.template_name, {'formset': formset})



class OrderUpdateView(AdminRequiredMixin, UpdateView):
    model = Order
    form_class = OrderUpdateForm
    template_name = 'suka_admin/quotation/quotation_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = OrderDetailFormSet(self.request.POST, instance=self.object, prefix='details')
        else:
            context['formset'] = OrderDetailFormSet(instance=self.object, prefix='details')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            # Contar formularios válidos (no eliminados)
            valid_forms = [f for f in formset.forms if f.is_valid() and not f.cleaned_data.get('DELETE', False)]

            if len(valid_forms) == 0:
                messages.error(self.request, "No puedes eliminar todos los detalles de la orden.")
                return self.form_invalid(form)

            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, 'Orden actualizada exitosamente.')
            return redirect(reverse_lazy('quoteApp:suka_admin_quotation_list'))

        messages.error(self.request, 'Corrige los errores en los detalles.')
        return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Corrige los errores en el formulario principal.')
        return self.render_to_response(self.get_context_data(form=form))



class QuotationListView(AdminRequiredMixin, ListView):
    template_name = 'suka_admin/quotation/quotation_list.html'
    context_object_name = 'quotation_list'
    model = Order
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        form = QuotationFilterForm(self.request.GET)

        if form.is_valid():
            if order_number := form.cleaned_data.get('order_number'):
                queryset = queryset.filter(order_number__icontains=order_number)

            if status := form.cleaned_data.get('status'):
                queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasar el formulario con los datos actuales para mantener los filtros
        context['form'] = QuotationFilterForm(self.request.GET or None)
        return context


class QuotationDetailView(AdminRequiredMixin, DetailView):
    template_name = 'suka_admin/quotation/quote_detail.html'
    model = Order
    context_object_name = 'order'


class QuotationDeletedView(AdminRequiredMixin, DeleteView):
    model = Order
    success_url = reverse_lazy('quoteApp:suka_admin_quotation_list')

    def can_delete_quotation(self, order):
        """
        Método personalizado para validar si se puede eliminar la cotización
        Retorna tuple (can_delete: bool, error_message: str)
        """
        # Verificar si tiene delivery asociado
        if hasattr(order, 'delivery') and order.delivery:
            delivery_status = order.delivery.get_status_display()
            if order.delivery.status == 'delivered':
                messages.error(self.request, f'La cotización tiene un envío asociado, no se puede eliminar esta cotización.')
                return False, f'El envío asociado a la cotización ya ha sido entregado. No se puede eliminar esta cotización.'
            else:
                messages.error(self.request, f'La cotización tiene un envío asociado, ambos se eliminarán')
                return True, f'La cotización tiene un envío asociado, ambos se eliminarán, ¿Está seguro de eliminarlos?'


        # Verificar el estado de la orden
        if order.status in ['confirmed', 'shipped']:
            return False, f'La cotización está en estado "{order.get_status_display()}", ¿está seguro de eliminarla?'
        elif order.status == 'delivered':
            messages.error(self.request, f'La cotización ya ha sido entregada. No se puede eliminar esta cotización.')
            return False, 'No se puede eliminar una cotización ya entregada'

        return True, ''

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Ejecutar validaciones
        can_delete, error_message = self.can_delete_quotation(self.object)

        if not can_delete:
            messages.error(request, error_message)
            return redirect(self.success_url)

        # Si pasa las validaciones, proceder
        messages.success(request, f'La cotización {self.object} ha sido eliminada exitosamente.')
        return super().post(request, *args, **kwargs)
