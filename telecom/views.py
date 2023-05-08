from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import StreamingHttpResponse

from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import TemplateView

from django.utils import timezone

from .forms import FormLine, FormAddLine, FormSmartphone, FormAddSmartphone, FormVivoBox, FormAddVivoBox
from .forms import FormSmartphoneModel, FormVivoboxModel, FormLinePlan
from .forms import FormLineStatus, FormLineStatusRFP, FormSmartphoneStatus, FormVivoboxStatus

from django.core.exceptions import PermissionDenied

from django.db.models import Q, Count
from .models import Line, Smartphone, VivoBox
from .models import SmartphoneModel, VivoboxModel, LinePlan
from .models import LineStatus, LineStatusRFP, SmartphoneStatus, VivoboxStatus, LineTelecom

from itertools import chain
from sapore_controle.settings import MEDIA_ROOT
from sapore_controle.settings import PAGINATE_BY
import csv
import os

class Echo:
    def write(self, value):
        return value

@login_required(redirect_field_name='login')
def generate_csv(request, telecom_type, csv_simple):
    if not request.user.has_perm('telecom.view_' + telecom_type):
        #Sobe erro 403 - Permissão Negada
        raise PermissionDenied()
    
    lines = Line.objects.all()
    smartphones = Smartphone.objects.all()
    vivoboxs = VivoBox.objects.all()

    header = ''

    line_headers_simple = ['Numero,Operadora,Plano,Nome,Filial,Status']
    line_headers = ['Numero,SimCard,SimCardAnterior,Operadora,Plano,NF,Nome,Filial,Status,DataAtualizacao']

    smartphone_headers_simple = ['Modelo,IMEI 1,NF,Nome,Filial,Numero,Status']
    smartphone_headers = ['Modelo,IMEI 1,IMEI 2,NF,Nome,Filial,Numero,Status,DataAtualizacao']

    vivobox_headers_simple = ['Modelo,IMEI 1,Nome,Filial,Numero,Status']
    vivobox_headers = ['Modelo,IMEI 1,NF,Nome,Filial,Numero,Status,DataAtualizacao']

    sufix = ''
    prefix = ''

    if telecom_type == 'line':
        prefix = 'linhas_'
        if csv_simple == 1:
            sufix = 'simplificado_'
            header = ([header] for header in line_headers_simple)

            rows = ([str(line.number), str(line.telecom), str(line.plan), str(line.name), 
                        str(line.branch), str(line.status)] for line in lines)
        else:
            header = ([header] for header in line_headers)

            rows = ([str(line.number), str(line.sim_card + "'"), str(line.sim_card_old + "'"), str(line.telecom), 
                        str(line.plan), str(line.receipt), str(line.name), str(line.branch), 
                        str(line.status), str(line.date_update)] for line in lines)
    elif telecom_type == 'smartphone':
        prefix = 'smartphones_'
        if csv_simple == 1:
            sufix = 'simplificado_'
            header = ([header] for header in smartphone_headers_simple)
            rows = ([str(smartphone.obj_model),str(smartphone.imei_1), str(smartphone.receipt), str(smartphone.name), 
                        str(smartphone.branch), str(smartphone.number), str(smartphone.status), 
                        ] for smartphone in smartphones)
        else:
            header = ([header] for header in smartphone_headers)
            rows = ([str(smartphone.obj_model),str(smartphone.imei_1), str(smartphone.imei_2),  str(smartphone.receipt), 
                        str(smartphone.name), str(smartphone.branch), str(smartphone.number), str(smartphone.status), 
                        str(smartphone.date_update), str(smartphone.tracking_code)] for smartphone in smartphones)
    elif telecom_type == 'vivobox':
        prefix = 'vivobox_'
        if csv_simple == 1:
            sufix = 'simplificado_'
            header = ([header] for header in vivobox_headers_simple)
            rows = ([str(vivobox.obj_model),str(vivobox.imei_1), str(vivobox.name), str(vivobox.branch), 
                        str(vivobox.number), str(vivobox.status)] for vivobox in vivoboxs)
        else:
            header = ([header] for header in vivobox_headers)
            rows = ([str(vivobox.obj_model),str(vivobox.imei_1),  str(vivobox.receipt), str(vivobox.name), 
                        str(vivobox.branch), str(vivobox.number), str(vivobox.status), 
                        str(vivobox.date_update), str(vivobox.tracking_code)] for vivobox in vivoboxs)

    result = chain(header, rows)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    return StreamingHttpResponse(
        (writer.writerow(row) for row in result),
        content_type="text/csv",
        headers={'Content-Disposition': 'attachment; filename="controle"' + prefix + sufix +
                 str(timezone.now().strftime("%d-%m-%Y")) + '".csv"'},
    )

############
# LinePlan #
############

class LinePlanList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = LinePlan
    #Caminho do arquivo html
    template_name = 'telecom/param/line/plan_list.html'
    #Número de itens por página
    paginate_by = PAGINATE_BY
    #Nome da variável do Model no html
    context_object_name = 'objects'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_lineplan'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('name', '-id')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["url_delete"] = '/delete_object/line_plan/'
        return context

class LinePlanEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = LinePlan
    #Caminho do arquivo html
    template_name = 'telecom/param/line/plan_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormLinePlan

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.change_lineplan'

    def form_valid(self, form):
        line_plan = self.get_object()
        line_plan.name = form.cleaned_data['name']
        line_plan.plan_type = form.cleaned_data['plan_type']

        line_plan.save()

        return redirect('line_plan_list')

class LinePlanAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = LinePlan
    #Caminho do arquivo html
    template_name = 'telecom/param/line/plan_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormLinePlan

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.add_lineplan'

    def form_valid(self, form):
        line_plan, created = LinePlan.objects.get_or_create(**form.cleaned_data)
        
        if created:
            line_plan.save()

        return redirect('line_plan_list')

##############
# LineStatus #
##############

class LineStatusList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = LineStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/line/status_list.html'
    #Número de itens por página
    paginate_by = PAGINATE_BY
    #Nome da variável do Model no html
    context_object_name = 'objects'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_linestatus'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('name', '-id')
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["url_delete"] = '/delete_object/line_status/'
        return context

class LineStatusEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = LineStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/line/status_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormLineStatus

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.change_linestatus'

    def form_valid(self, form):
        line_status = self.get_object()
        line_status.name = form.cleaned_data['name']

        line_status.save()

        return redirect('line_status_list')

class LineStatusAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = LineStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/line/status_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormLineStatus

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.add_linestatus'

    def form_valid(self, form):
        line_status, created = LineStatus.objects.get_or_create(**form.cleaned_data)
        
        if created:
            line_status.save()

        return redirect('line_status_list')

#################
# LineStatusRFP #
#################

class LineStatusRFPList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = LineStatusRFP
    #Caminho do arquivo html
    template_name = 'telecom/param/line/status_rfp_list.html'
    #Número de itens por página
    paginate_by = PAGINATE_BY
    #Nome da variável do Model no html
    context_object_name = 'objects'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_linestatusrfp'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('name', '-id')
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["url_delete"] = '/delete_object/line_status_rfp/'
        return context

class LineStatusRFPEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = LineStatusRFP
    #Caminho do arquivo html
    template_name = 'telecom/param/line/status_rfp_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormLineStatusRFP

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.change_linestatusrfp'

    def form_valid(self, form):
        line_status_rfp = self.get_object()
        line_status_rfp.name = form.cleaned_data['name']

        line_status_rfp.save()

        return redirect('line_status_rfp_list')

class LineStatusRFPAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = LineStatusRFP
    #Caminho do arquivo html
    template_name = 'telecom/param/line/status_rfp_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormLineStatusRFP

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.add_linestatusrfp'

    def form_valid(self, form):
        line_status_rfp, created = LineStatusRFP.objects.get_or_create(**form.cleaned_data)
        
        if created:
            line_status_rfp.save()

        return redirect('line_status_rfp_list')

##############
# SmartphoneModel #
##############

class SmartphoneModelList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = SmartphoneModel
    #Caminho do arquivo html
    template_name = 'telecom/param/smartphone/model_list.html'
    #Número de itens por página
    paginate_by = PAGINATE_BY
    #Nome da variável do Model no html
    context_object_name = 'objects'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_smartphonemodel'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('name', '-id')
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["url_delete"] = '/delete_object/smartphone_model/'
        return context

class SmartphoneModelEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = SmartphoneModel
    #Caminho do arquivo html
    template_name = 'telecom/param/smartphone/model_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormSmartphoneModel

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.change_smartphonemodel'

    def form_valid(self, form):
        smart_model = self.get_object()
        smart_model.name = form.cleaned_data['name']
        smart_model.date_release = form.cleaned_data['date_release']

        smart_model.save()

        return redirect('smartphone_model_list')

class SmartphoneModelAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = SmartphoneModel
    #Caminho do arquivo html
    template_name = 'telecom/param/smartphone/model_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormSmartphoneModel

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.add_smartphonemodel'

    def form_valid(self, form):
        smart_model, created = SmartphoneModel.objects.get_or_create(**form.cleaned_data)
        
        if created:
            smart_model.save()

        return redirect('smartphone_model_list')

####################
# SmartphoneStatus #
####################

class SmartphoneStatusList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = SmartphoneStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/smartphone/status_list.html'
    #Número de itens por página
    paginate_by = PAGINATE_BY
    #Nome da variável do Model no html
    context_object_name = 'objects'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_smartphonestatus'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('name', '-id')
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["url_delete"] = '/delete_object/smartphone_status/'
        return context

class SmartphoneStatusEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = SmartphoneStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/smartphone/status_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormSmartphoneStatus

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.change_smartphonestatus'

    def form_valid(self, form):
        smart_status = self.get_object()
        smart_status.name = form.cleaned_data['name']

        smart_status.save()

        return redirect('smartphone_status_list')

class SmartphoneStatusAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = SmartphoneStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/smartphone/status_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormSmartphoneStatus

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.add_smartphonestatus'

    def form_valid(self, form):
        smart_status, created = SmartphoneStatus.objects.get_or_create(**form.cleaned_data)
        
        if created:
            smart_status.save()

        return redirect('smartphone_status_list')

############
# VivoboxModel #
############

class VivoboxModelList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = VivoboxModel
    #Caminho do arquivo html
    template_name = 'telecom/param/vivobox/model_list.html'
    #Número de itens por página
    paginate_by = PAGINATE_BY
    #Nome da variável do Model no html
    context_object_name = 'objects'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_vivoboxmodel'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('name', '-id')
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["url_delete"] = '/delete_object/vivobox_model/'
        return context

class VivoboxModelEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = VivoboxModel
    #Caminho do arquivo html
    template_name = 'telecom/param/vivobox/model_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormVivoboxModel
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.change_vivoboxmodel'

    def form_valid(self, form):
        box_model = self.get_object()
        box_model.name = form.cleaned_data['name']

        box_model.save()

        return redirect('vivobox_model_list')

class VivoboxModelAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = VivoboxModel
    #Caminho do arquivo html
    template_name = 'telecom/param/vivobox/model_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormVivoboxModel
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.add_vivoboxmodel'

    def form_valid(self, form):
        box_model, created = VivoboxModel.objects.get_or_create(**form.cleaned_data)
        if created:
            box_model.save()

        return redirect('vivobox_model_list')

#############
# VivoboxStatus #
#############

class VivoboxStatusList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = VivoboxStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/vivobox/status_list.html'
    #Número de itens por página
    paginate_by = PAGINATE_BY
    #Nome da variável do Model no html
    context_object_name = 'objects'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_vivoboxstatus'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('name', '-id')
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["url_delete"] = '/delete_object/vivobox_status/'
        return context

class VivoboxStatusEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = VivoboxStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/vivobox/status_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormVivoboxStatus
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.change_vivoboxstatus'

    def form_valid(self, form):
        box_status = self.get_object()
        box_status.name = form.cleaned_data['name']

        box_status.save()

        return redirect('vivobox_status_list')

class VivoboxStatusAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = VivoboxStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/vivobox/status_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormVivoboxStatus
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.add_vivoboxstatus'

    def form_valid(self, form):
        box_status, created = VivoboxStatus.objects.get_or_create(**form.cleaned_data)
        if created:
            box_status.save()

        return redirect('vivobox_status_list')

##########
# Linhas #
##########

class LineList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Line
    #Caminho do arquivo html
    template_name = 'telecom/line/line_list.html'
    #Número de itens por página
    paginate_by = PAGINATE_BY
    #Nome da variável do Model no html
    context_object_name = 'objects'

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.view_line'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.order_by('telecom', 'number', '-id')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        line_telecom = LineTelecom.objects.all()
        line_plan = LinePlan.objects.all()
        line_status = LineStatus.objects.all()

        context["url_delete"] = '/delete_object/line/'

        context["qs_line_telecom"] = line_telecom
        context["qs_line_plan"] = line_plan
        context["qs_line_status"] = line_status
        return context

#Herda as informações e ordenação da Query do LineList
class LineSearch(LineList):
    template_name = 'telecom/line/line_search.html'

    #Envia a Query com buscando o termo e com filtro de status para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        term = self.request.GET.get('term')
        filter_line = self.request.GET.get('line')
        filter_telecom = self.request.GET.get('filter_telecom')
        filter_plan = self.request.GET.get('filter_plan')
        filter_branch = self.request.GET.get('filter_branch')
        filter_status = self.request.GET.get('filter_status')
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_line:
            print(filter_line)
            qs = qs.filter(
                Q(number__contains=filter_line) | Q(sim_card__contains=filter_line) | Q(sim_card_old__contains=filter_line)
            )
        
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_telecom:
            qs = qs.filter(
                Q(telecom__exact=LineTelecom.objects.get(name=filter_telecom))
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_plan:
            qs = qs.filter(
                Q(plan__exact=LinePlan.objects.get(name=filter_plan))
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_status:
            qs = qs.filter(
                Q(status__exact=LineStatus.objects.get(name=filter_status))
            )

        #Caso tenha filtro, adiciona na Query o filtro
        if filter_branch:
            qs = qs.filter(
                Q(branch__exact=filter_branch)
            )

        if not term:
            return qs

        #Query com ordem, e busca
        qs = qs.filter(
            Q(name__icontains=term)
        )

        return qs

class LineDetails(LoginRequiredMixin, ListView):
    model = Line
    #Caminho do arquivo html
    template_name = 'telecom/line/line_details.html'
    #Nome da variável do Model no html
    context_object_name = 'line'

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Retorna e envia a Query com apenas a linha selecionada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        
        #Busca argumento na URL configurado em views.py
        line_id = self.kwargs.get('pk', None)

        qs = qs.get(id=line_id)
        
        return qs

class LineEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Line
    #Caminho do arquivo html
    template_name = 'telecom/line/line_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'line'
    #Formulário para editar a linha
    form_class = FormLine

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.change_line'

    def form_valid(self, form):
        line = self.get_object()
        line.name = form.cleaned_data['name']
        if line.sim_card != form.cleaned_data['sim_card']:
            line.sim_card_old = line.sim_card
        line.sim_card = form.cleaned_data['sim_card']
        line.branch = form.cleaned_data['branch']
        line.action = form.cleaned_data['action']
        line.name_mapped = form.cleaned_data['name_mapped']
        line.branch_mapped = form.cleaned_data['branch_mapped']
        line.accountable = form.cleaned_data['accountable']
        line.status = form.cleaned_data['status']
        line.status_rfp = form.cleaned_data['status_rfp']
        line.consumption = form.cleaned_data['consumption']
        line.vip = form.cleaned_data['vip']
        
        if (not line.name_mapped or not line.branch_mapped) and line.action == 'OK':
            line.action = 'MAPEAR'
        elif line.name_mapped and line.branch_mapped and line.action == 'MAPEAR':
            line.action = 'OK'

        if self.request.POST.get('auth_attachment-clear') == 'on':
            os.remove(MEDIA_ROOT / line.auth_attachment.name)
            line.auth_attachment = None
        elif line.auth_attachment and self.request.FILES:
            os.remove(MEDIA_ROOT / line.auth_attachment.name)
            line.auth_attachment = form.cleaned_data['auth_attachment']
        else:
            line.auth_attachment = form.cleaned_data['auth_attachment']

        line.save()

        try:
            smartphone = Smartphone.objects.get(number=line.number)
            smartphone.name = line.name
            smartphone.branch = line.branch
            smartphone.date_update = timezone.now()
            smartphone.save()
        except:
            try:
                vivobox = VivoBox.objects.get(number=line.number)
                vivobox.name = line.name
                vivobox.branch = line.branch
                vivobox.date_update = timezone.now()
                vivobox.save()
            except:
                pass
        return redirect('line_details', pk=line.id)
        
class LineAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Line
    #Caminho do arquivo html
    template_name = 'telecom/line/line_add.html'
    #Nome da variável do Model no html
    context_object_name = 'line'
    #Formulário para editar a linha
    form_class = FormAddLine

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.add_line'

    def form_valid(self, form):
        line = Line(**form.cleaned_data)

        line_plan = line.plan.name.upper()
        
        if 'TIM' in line_plan:
            line.telecom, created = LineTelecom.objects.get_or_create(name='TIM')
        elif 'CLARO' in line_plan:
            line.telecom, created = LineTelecom.objects.get_or_create(name='Claro')
        else:
            line.telecom, created = LineTelecom.objects.get_or_create(name='Vivo')

        if (not line.name_mapped or not line.branch_mapped) and line.action == 'OK':
            line.action = 'MAPEAR'
        elif line.name_mapped and line.branch_mapped and line.action == 'MAPEAR':
            line.action = 'OK'

        line.save()

        return redirect('line_list')

##############
# Smartphone #
##############

class SmartphoneList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Smartphone
    #Caminho do arquivo html
    template_name = 'telecom/smartphone/smartphone_list.html'
    #Número de itens por página
    paginate_by = PAGINATE_BY
    #Nome da variável do Model no html
    context_object_name = 'objects'

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.view_smartphone'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.order_by('obj_model', 'imei_1', '-id')

        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        smartphone_model = SmartphoneModel.objects.all()
        smartphone_status = SmartphoneStatus.objects.all()

        context["url_delete"] = '/delete_object/smartphone/'

        context["qs_smartphone_status"] = smartphone_status
        context["qs_smartphone_model"] = smartphone_model
        return context

#Herda as informações e ordenação da Query do smartphoneList
class SmartphoneSearch(SmartphoneList):
    template_name = 'telecom/smartphone/smartphone_search.html'

    #Envia a Query com buscando o termo e com filtro de status para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        term = self.request.GET.get('term')
        filter_model = self.request.GET.get('filter_model')
        filter_branch = self.request.GET.get('filter_branch')
        filter_status = self.request.GET.get('filter_status')
        filter_imei = self.request.GET.get('filter_imei')
        filter_line = self.request.GET.get('filter_line')
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_line:
            qs = qs.filter(
                Q(number__contains=filter_line)
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_imei:
            qs = qs.filter(
                Q(imei_1__contains=filter_imei) | Q(imei_2__contains=filter_imei)
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_model:
            qs = qs.filter(
                Q(obj_model__exact=SmartphoneModel.objects.get(name=filter_model))
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_status:
            qs = qs.filter(
                Q(status__exact=SmartphoneStatus.objects.get(name=filter_status))
            )

        #Caso tenha filtro, adiciona na Query o filtro
        if filter_branch:
            qs = qs.filter(
                Q(branch__iexact=filter_branch)
            )

        if not term:
            return qs

        #Query com ordem, e busca
        qs = qs.filter(
            Q(name__icontains=term)
        )

        return qs

class SmartphoneDetails(LoginRequiredMixin, ListView):
    model = Smartphone
    #Caminho do arquivo html
    template_name = 'telecom/smartphone/smartphone_details.html'
    #Nome da variável do Model no html
    context_object_name = 'smartphone'

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Retorna e envia a Query com apenas a linha selecionada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        
        #Busca argumento na URL configurado em views.py
        smartphone_id = self.kwargs.get('pk', None)

        qs = qs.get(id=smartphone_id)
        
        return qs

class SmartphoneEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Smartphone
    #Caminho do arquivo html
    template_name = 'telecom/smartphone/smartphone_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'smartphone'
    #Formulário para editar a linha
    form_class = FormSmartphone

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.change_smartphone'

    #Se o formulário for válido altera os valores
    def form_valid(self, form):
        smartphone = self.get_object()
        smartphone.name = form.cleaned_data['name']
        smartphone.branch = form.cleaned_data['branch']
        smartphone.status = form.cleaned_data['status']
        smartphone.tracking_code = form.cleaned_data['tracking_code']
        smartphone.date_update = timezone.now()

        if self.request.POST.get('auth_attachment-clear') == 'on':
            os.remove(MEDIA_ROOT / smartphone.auth_attachment.name)
            smartphone.auth_attachment = None
        elif smartphone.auth_attachment and self.request.FILES:
            os.remove(MEDIA_ROOT / smartphone.auth_attachment.name)
            smartphone.auth_attachment = form.cleaned_data['auth_attachment']
        else:
            smartphone.auth_attachment = form.cleaned_data['auth_attachment']

        #Verifica se já possuia uma linha e altera para disponível
        try:
            line_old = Line.objects.get(number=smartphone.number)
            line_old.name = '-'
            line_old.branch = 0
            line_old.status, created = LineStatus.objects.get_or_create(name='Disponivel')
            line_old.date_update = timezone.now()
            line_old.save()
        except:
            pass

        smartphone.number = form.cleaned_data['number']

        #Altera as informações da linha
        try:
            line = Line.objects.get(number=form.cleaned_data['number'])
            line.name = form.cleaned_data['name']

            if form.cleaned_data['branch'] != 0:
                line.branch = form.cleaned_data['branch']

            line.status, created = LineStatus.objects.get_or_create(name='Ativo')
            line.date_update = timezone.now()
            
            line.save()

            smartphone.line_id = line.id
        except:
            pass
        smartphone.save()

        return redirect('smartphone_details', pk=smartphone.id)

class SmartphoneAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Smartphone
    #Caminho do arquivo html
    template_name = 'telecom/smartphone/smartphone_add.html'
    #Nome da variável do Model no html
    context_object_name = 'smartphone'
    #Formulário para editar a linha
    form_class = FormAddSmartphone

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.add_smartphone'

    def form_valid(self, form):
        smartphone = Smartphone(**form.cleaned_data)

        #Verifica se possui linha e altera as informações
        try:
            line = Line.objects.get(number=form.cleaned_data['number'])
            line.name = form.cleaned_data['name']
            if form.cleaned_data['branch'] != 0:
                line.branch = form.cleaned_data['branch']

            line.status, created = LineStatus.objects.get_or_create(name='Ativo')
            line.date_update = timezone.now()

            line.save()
            
            smartphone.line_id = line.id
        except:
            pass

        
        smartphone.save()

        return redirect('smartphone_list')

##############
# VivoBox #
##############

class VivoBoxList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = VivoBox
    #Caminho do arquivo html
    template_name = 'telecom/vivobox/vivobox_list.html'
    #Número de itens por página
    paginate_by = PAGINATE_BY
    #Nome da variável do Model no html
    context_object_name = 'objects'

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.view_vivobox'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.order_by('obj_model', 'imei_1', '-id')

        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        vivobox_model = VivoboxModel.objects.all()
        vivobox_status = VivoboxStatus.objects.all()

        context["url_delete"] = '/delete_object/vivobox/'

        context["qs_vivobox_status"] = vivobox_status
        context["qs_vivobox_model"] = vivobox_model
        return context

#Herda as informações e ordenação da Query do vivoboxList
class VivoBoxSearch(VivoBoxList):
    template_name = 'telecom/vivobox/vivobox_search.html'

    #Envia a Query com buscando o termo e com filtro de status para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        term = self.request.GET.get('term')
        filter_branch = self.request.GET.get('filter_branch')
        filter_status = self.request.GET.get('filter_status')
        filter_model = self.request.GET.get('filter_model')
        filter_imei = self.request.GET.get('filter_imei')
        filter_line = self.request.GET.get('filter_line')
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_line:
            qs = qs.filter(
                Q(number__contains=filter_line)
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_imei:
            qs = qs.filter(
                Q(imei_1__contains=filter_imei)
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_model:
            qs = qs.filter(
                Q(obj_model__exact=VivoboxModel.objects.get(name=filter_model))
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_status:
            qs = qs.filter(
                Q(status__exact=VivoboxStatus.objects.get(name=filter_status))
            )

        #Caso tenha filtro, adiciona na Query o filtro
        if filter_branch:
            qs = qs.filter(
                Q(branch__iexact=filter_branch)
            )

        if not term or term == '':
            return qs

        #Query com ordem, e busca
        qs = qs.filter(
            Q(name__icontains=term)
        )

        return qs

class VivoBoxDetails(LoginRequiredMixin, ListView):
    model = VivoBox
    #Caminho do arquivo html
    template_name = 'telecom/vivobox/vivobox_details.html'
    #Nome da variável do Model no html
    context_object_name = 'vivobox'

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Retorna e envia a Query com apenas a linha selecionada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        
        #Busca argumento na URL configurado em views.py
        vivobox_id = self.kwargs.get('pk', None)

        qs = qs.get(id=vivobox_id)
        
        return qs

class VivoBoxEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = VivoBox
    #Caminho do arquivo html
    template_name = 'telecom/vivobox/vivobox_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'vivobox'
    #Formulário para editar a linha
    form_class = FormVivoBox

    #Permissão para acessar a página
    permission_required = 'telecom.change_vivobox'

    #Se o formulário for válido altera os valores
    def form_valid(self, form):
        vivobox = self.get_object()
        vivobox.name = form.cleaned_data['name']
        vivobox.branch = form.cleaned_data['branch']
        vivobox.status = form.cleaned_data['status']
        vivobox.tracking_code = form.cleaned_data['tracking_code']
        vivobox.date_update = timezone.now()

        if self.request.POST.get('auth_attachment-clear') == 'on':
            os.remove(MEDIA_ROOT / vivobox.auth_attachment.name)
            vivobox.auth_attachment = None
        elif vivobox.auth_attachment and self.request.FILES:
            os.remove(MEDIA_ROOT / vivobox.auth_attachment.name)
            vivobox.auth_attachment = form.cleaned_data['auth_attachment']
        else:
            vivobox.auth_attachment = form.cleaned_data['auth_attachment']

        #Verifica se já possuia uma linha e altera para disponível
        try:
            line_old = Line.objects.get(number=vivobox.number)
            line_old.name = '-'
            line_old.branch = 0
            line_old.status, created = LineStatus.objects.get_or_create(name='Disponivel')
            line_old.date_update = timezone.now()
            line_old.save()
        except:
            pass

        vivobox.number = form.cleaned_data['number']
        
        #Altera as informações da linha
        try:
            line = Line.objects.get(number=form.cleaned_data['number'])
            line.name = form.cleaned_data['name']
            if form.cleaned_data['branch'] != 0:
                line.branch = form.cleaned_data['branch']
            line.status, created = LineStatus.objects.get_or_create(name='Ativo')
            line.date_update = timezone.now()

            line.save()
            vivobox.line_id = line.id
        except:
            pass

        vivobox.save()
        return redirect('vivobox_details', pk=vivobox.id)

class VivoBoxAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = VivoBox
    #Caminho do arquivo html
    template_name = 'telecom/vivobox/vivobox_add.html'
    #Nome da variável do Model no html
    context_object_name = 'vivobox'
    #Formulário para editar a linha
    form_class = FormAddVivoBox

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.add_vivobox'

    def form_valid(self, form):
        vivobox = VivoBox(**form.cleaned_data)

        #Verifica se possui linha e altera as informações
        try:
            line = Line.objects.get(number=form.cleaned_data['number'])
            line.name = form.cleaned_data['name']
            if form.cleaned_data['branch'] != 0:
                line.branch = form.cleaned_data['branch']

            line.status, created = LineStatus.objects.get_or_create(name='Ativo')
            line.date_update = timezone.now()

            line.save()
            vivobox.line_id = line.id
        except:
            pass

        vivobox.save()

        return redirect('vivobox_list')