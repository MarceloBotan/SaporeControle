from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Branch, UploadFile
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from .forms import FormUploadFile
import pandas as pd

class BranchList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Branch
    #Caminho do arquivo html
    template_name = 'telecom/branch_list.html'
    #Número de itens por página
    paginate_by = 20
    #Nome da variável do Model no html
    context_object_name = 'branchs'

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.view_branch'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('branch', '-id')
        return qs

class BranchEdit(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Branch
    #Caminho do arquivo html
    template_name = 'telecom/branch_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'file'
    #Formulário para editar a linha
    form_class = FormUploadFile

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.change_branch'

    def form_valid(self, form):
        upload_file = UploadFile(**form.cleaned_data)

        df = pd.read_excel(upload_file.file, usecols=('B,D,F,I,K'))
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

        return redirect('branch_list')