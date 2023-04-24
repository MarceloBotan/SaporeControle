from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Branch, UploadFile
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from .forms import FormUploadFile
from django.contrib import messages

from sapore_controle.settings import MEDIA_ROOT
import pandas as pd
import os
import warnings

class BranchList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Branch
    #Caminho do arquivo html
    template_name = 'branch/branch_list.html'
    #Número de itens por página
    paginate_by = 20
    #Nome da variável do Model no html
    context_object_name = 'branchs'

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'branch.view_branch'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('branch', '-id')
        return qs

class BranchEdit(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = UploadFile
    #Caminho do arquivo html
    template_name = 'branch/branch_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'files'
    #Formulário para editar a linha
    form_class = FormUploadFile

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'branch.change_branch'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        files = UploadFile.objects.all()

        context['files'] = list(files)
        return context

    def form_valid(self, form):
        if not form.cleaned_data['file']:
            messages.error(self.request, 'Campo vazio')
            return redirect('branch_edit')

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            df = pd.read_excel(form.cleaned_data['file'], usecols=('B,D,F,I,K'), engine='openpyxl')
        
        keys = ['CDFILIAL', 'NMFILIAL', 'ESTRUTURA', 'UNIDADE_ENCERRADA', 'NOME_REGIONAL']
        for df_key in df.keys():
            if df_key in keys:
                continue
            messages.error(self.request, 'Campos inválidos')
            return redirect('branch_edit')

        docs_old = UploadFile.objects.all()
        docs_old.delete()

        upload_file = UploadFile(**form.cleaned_data)

        for df_branch in df.values:
            branch, created = Branch.objects.get_or_create(branch=df_branch[0])
            branch.name = df_branch[1]
            branch.structure = df_branch[2]
            if df_branch[3] == 'S':
                branch.closed = True
            elif df_branch[3] == 'N':
                branch.closed = False
            branch.regional = df_branch[4]

            branch.save()

        upload_file.file = None
        upload_file.save()

        return redirect('branch_list')