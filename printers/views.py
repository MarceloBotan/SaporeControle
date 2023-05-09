from django.shortcuts import redirect


from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView

from .models import Printer
from .forms import FormPrinter, FormAddPrinter

from sapore_controle.settings import PAGINATE_BY

class PrinterList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Printer
    #Caminho do arquivo html
    template_name = 'printers/printer_list.html'
    #Número de itens por página
    paginate_by = PAGINATE_BY
    #Nome da variável do Model no html
    context_object_name = 'objects'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_printer'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('name', '-id')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["url_delete"] = '/delete_object/printer/'
        return context

class PrinterEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Printer
    #Caminho do arquivo html
    template_name = 'printers/printer_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormPrinter

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.change_printer'

    def form_valid(self, form):
        line_plan = self.get_object()
        line_plan.name = form.cleaned_data['name']

        line_plan.save()

        return redirect('printer_list')

class PrinterAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Printer
    #Caminho do arquivo html
    template_name = 'printers/printer_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormPrinter

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.add_printer'

    def form_valid(self, form):
        printer, created = Printer.objects.get_or_create(**form.cleaned_data)
        
        if created:
            printer.save()

        return redirect('printer_list')
