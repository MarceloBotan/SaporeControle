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
from .forms import FormSmartModel, FormBoxModel, FormLinePlan
from .forms import FormLineStatus, FormLineStatusRFP, FormSmartStatus, FormBoxStatus

from django.core.exceptions import PermissionDenied

from django.db.models import Q, Count
from .models import Line, Smartphone, VivoBox
from .models import SmartModel, BoxModel, LinePlan
from .models import LineStatus, LineStatusRFP, SmartStatus, BoxStatus, LineTelecom

from itertools import chain
from sapore_controle.settings import MEDIA_ROOT
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
                        str(smartphone.date_update)] for smartphone in smartphones)
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
                        str(vivobox.date_update)] for vivobox in vivoboxs)

    result = chain(header, rows)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    return StreamingHttpResponse(
        (writer.writerow(row) for row in result),
        content_type="text/csv",
        headers={'Content-Disposition': 'attachment; filename="controle"' + prefix + sufix +
                 str(timezone.now().strftime("%d-%m-%Y")) + '".csv"'},
    )

@login_required(redirect_field_name='login')
def delete_model(request, telecom_type, model_id):
    if 'sapore_telecom' not in request.user.groups.get().name and 'admin' not in request.user.groups.get().name:
        #Sobre erro 403 - Permissão Negada
        raise PermissionDenied()

    if telecom_type == 'vivobox':
        try:
            box_model = BoxModel.objects.get(id=model_id)
            box_model.delete()
        except:
            messages.error(request, 'Modelo não pode ser deletado')
        return redirect('v_model_list')
    
    elif telecom_type == 'smartphone':
        try:
            smart_model = SmartModel.objects.get(id=model_id)
            smart_model.delete()
        except:
            messages.error(request, 'Modelo não pode ser deletado')
        return redirect('s_model_list')
        
    elif telecom_type == 'line':
        try:
            line_plan = LinePlan.objects.get(id=model_id)
            line_plan.delete()
        except:
            messages.error(request, 'Modelo não pode ser deletado')
        return redirect('line_plan_list')
    
    return redirect('index')

@login_required(redirect_field_name='login')
def delete_status(request, telecom_type, status_id, rfp):
    if 'sapore_telecom' not in request.user.groups.get().name and 'admin' not in request.user.groups.get().name:
        #Sobre erro 403 - Permissão Negada
        raise PermissionDenied()

    if telecom_type == 'vivobox':
        try:
            box_status = BoxStatus.objects.get(id=status_id)
            box_status.delete()
        except:
            messages.error(request, 'Modelo não pode ser deletado')
        return redirect('v_status_list')
    
    elif telecom_type == 'smartphone':
        try:
            smart_status = SmartStatus.objects.get(id=status_id)
            smart_status.delete()
        except:
            messages.error(request, 'Modelo não pode ser deletado')
        return redirect('s_status_list')
    
    elif telecom_type == 'line' and rfp == 1:
        try:
            line_plan = LineStatusRFP.objects.get(id=status_id)
            line_plan.delete()
        except:
            messages.error(request, 'Modelo não pode ser deletado')
        return redirect('line_status_rfp_list')
    
    elif telecom_type == 'line':
        try:
            line_plan = LineStatus.objects.get(id=status_id)
            line_plan.delete()
        except:
            messages.error(request, 'Modelo não pode ser deletado')
        return redirect('line_status_list')

    return redirect('index')

@login_required(redirect_field_name='login')
def index(request):
    if 'sapore_telecom' in request.user.groups.get().name:
        return redirect('dashboard')
    elif 'tg_' in request.user.groups.get().name:
        return redirect('line_list')
    return render(request, 'telecom/index.html')

#############
# Dashboard #
#############

class Dashboard(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    #Caminho do arquivo html
    template_name = 'telecom/dashboard.html'    
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_lineplan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        def object_by_status_by_model(objects):
            object_by_status_by_model = {}
            for object in objects:
                model_count = {}
                try:
                    model_name = object.obj_model.name
                except:
                    model_name = object.telecom.name
                status_name = object.status.name
                model_count[model_name] = object.status_count
                if status_name not in object_by_status_by_model.keys():
                    object_by_status_by_model[status_name] = model_count
                    continue
                object_by_status_by_model[status_name].update(model_count)
            return object_by_status_by_model

        def split_object(object, _objectmodels, _objectstatus, object_name):
            object_status_count = []
            object_models = []
            object_status = []
            object_filter_models = []
            i = 0
            for model in _objectmodels:
                object_models.append(model.name)
                model_status_count = []
                has_filter = False
                if len(list(self.request.GET)) > 0:
                    if object_name in list(self.request.GET)[0]:
                        has_filter = True
                if self.request.GET.get(object_name + model.name) == 'on' or not has_filter:
                    object_filter_models.append(model.name)

                    for status in _objectstatus:
                        if status.name not in object_status:
                            object_status.append(status.name)
                        if status.name in object.keys():
                            if model.name in object[status.name].keys():
                                model_status_count.append(object[status.name][model.name])
                                continue
                            model_status_count.append(0)
                    object_status_count.append(model_status_count)
                i += 1

            if not object_filter_models:
                object_filter_models = object_models
            
            return object_status_count, object_models, object_status, object_filter_models

        smartphones = Smartphone.objects.raw(
            'select sp.id, count(sp.id) as status_count \
	            from telecom_smartphone sp \
                group by sp.status_id, sp.obj_model_id'
        )

        _smartmodels = SmartModel.objects.all()
        _smartstatus = SmartStatus.objects.all()

        smartphone_by_status_by_model = object_by_status_by_model(smartphones)

        smartphone_status_count, smartphone_models, \
            smartphone_status, smartphone_filter_models = split_object(
                smartphone_by_status_by_model, 
                _smartmodels,
                _smartstatus,
                'smartphone_')

        vivoboxs = VivoBox.objects.raw(
            'select vb.id, count(vb.id) as status_count \
	            from telecom_vivobox vb \
                group by vb.status_id, vb.obj_model_id'
        )

        _boxmodels = BoxModel.objects.all()
        _boxstatus = BoxStatus.objects.all()

        vivobox_by_status_by_model = object_by_status_by_model(vivoboxs)

        vivobox_status_count, vivobox_models, \
            vivobox_status, vivobox_filter_models = split_object(
                vivobox_by_status_by_model,
                _boxmodels,
                _boxstatus,
                'vivobox_'
            )

        lines = Line.objects.raw(
            'select l.id, count(l.id) as status_count \
	            from telecom_line l \
                group by l.status_id, l.telecom_id'
        )

        _linetelecom = LineTelecom.objects.all()
        _linestatus = LineStatus.objects.all()

        line_by_status_by_model = object_by_status_by_model(lines)

        line_status_count, line_telecom, \
            line_status, line_filter_telecom = split_object(
                line_by_status_by_model,
                _linetelecom,
                _linestatus,
                'line_telecom_'
            )

        print(line_status, line_telecom, line_filter_telecom, line_status_count, line_by_status_by_model)
        # print(smartphone_status, smartphone_models, smartphone_filter_models, smartphone_status_count, smartphone_by_status_by_model)

        context["qs_smartphone_status"] = smartphone_status
        context["qs_smartphone_models"] = smartphone_models
        context["qs_smartphone_filter_models"] = smartphone_filter_models
        context["qs_smartphone_count"] = smartphone_status_count
        context["qs_smartphone"] = smartphone_by_status_by_model

        context["qs_line_status"] = line_status
        context["qs_line_telecom"] = line_telecom
        context["qs_line_filter_telecom"] = line_filter_telecom
        context["qs_line_count"] = line_status_count
        context["qs_line"] = line_by_status_by_model

        context["qs_vivobox_status"] = vivobox_status
        context["qs_vivobox_models"] = vivobox_models
        context["qs_vivobox_filter_models"] = vivobox_filter_models
        context["qs_vivobox_count"] = vivobox_status_count
        context["qs_vivobox"] = vivobox_by_status_by_model

        return context

############
# LinePlan #
############

class LinePlanList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = LinePlan
    #Caminho do arquivo html
    template_name = 'telecom/param/line/plan_list.html'
    #Número de itens por página
    paginate_by = 20
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
    paginate_by = 20
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
    paginate_by = 20
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
# SmartModel #
##############

class SmartModelList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = SmartModel
    #Caminho do arquivo html
    template_name = 'telecom/param/smartphone/model_list.html'
    #Número de itens por página
    paginate_by = 20
    #Nome da variável do Model no html
    context_object_name = 'objects'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_smartmodel'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('name', '-id')
        return qs

class SmartModelEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = SmartModel
    #Caminho do arquivo html
    template_name = 'telecom/param/smartphone/model_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormSmartModel

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.change_smartmodel'

    def form_valid(self, form):
        smart_model = self.get_object()
        smart_model.name = form.cleaned_data['name']
        smart_model.date_release = form.cleaned_data['date_release']

        smart_model.save()

        return redirect('s_model_list')

class SmartModelAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = SmartModel
    #Caminho do arquivo html
    template_name = 'telecom/param/smartphone/model_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormSmartModel

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.add_smartmodel'

    def form_valid(self, form):
        smart_model, created = SmartModel.objects.get_or_create(**form.cleaned_data)
        
        if created:
            smart_model.save()

        return redirect('s_model_list')

####################
# SmartphoneStatus #
####################

class SmartStatusList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = SmartStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/smartphone/status_list.html'
    #Número de itens por página
    paginate_by = 20
    #Nome da variável do Model no html
    context_object_name = 'objects'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_smartstatus'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('name', '-id')
        return qs

class SmartStatusEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = SmartStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/smartphone/status_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormSmartStatus

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.change_smartstatus'

    def form_valid(self, form):
        smart_status = self.get_object()
        smart_status.name = form.cleaned_data['name']

        smart_status.save()

        return redirect('s_status_list')

class SmartStatusAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = SmartStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/smartphone/status_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormSmartStatus

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.add_smartstatus'

    def form_valid(self, form):
        smart_status, created = SmartStatus.objects.get_or_create(**form.cleaned_data)
        
        if created:
            smart_status.save()

        return redirect('s_status_list')

############
# BoxModel #
############

class BoxModelList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = BoxModel
    #Caminho do arquivo html
    template_name = 'telecom/param/vivobox/model_list.html'
    #Número de itens por página
    paginate_by = 20
    #Nome da variável do Model no html
    context_object_name = 'objects'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_boxmodel'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('name', '-id')
        return qs

class BoxModelEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = BoxModel
    #Caminho do arquivo html
    template_name = 'telecom/param/vivobox/model_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormBoxModel
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.change_boxmodel'

    def form_valid(self, form):
        box_model = self.get_object()
        box_model.name = form.cleaned_data['name']

        box_model.save()

        return redirect('v_model_list')

class BoxModelAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = BoxModel
    #Caminho do arquivo html
    template_name = 'telecom/param/vivobox/model_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormBoxModel
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.add_boxmodel'

    def form_valid(self, form):
        box_model, created = BoxModel.objects.get_or_create(**form.cleaned_data)
        if created:
            box_model.save()

        return redirect('v_model_list')

#############
# BoxStatus #
#############

class BoxStatusList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = BoxStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/vivobox/status_list.html'
    #Número de itens por página
    paginate_by = 20
    #Nome da variável do Model no html
    context_object_name = 'objects'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_boxstatus'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('name', '-id')
        return qs

class BoxStatusEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = BoxStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/vivobox/status_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormBoxStatus
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.change_boxstatus'

    def form_valid(self, form):
        box_status = self.get_object()
        box_status.name = form.cleaned_data['name']

        box_status.save()

        return redirect('v_status_list')

class BoxStatusAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = BoxStatus
    #Caminho do arquivo html
    template_name = 'telecom/param/vivobox/status_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormBoxStatus
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.add_boxstatus'

    def form_valid(self, form):
        box_status, created = BoxStatus.objects.get_or_create(**form.cleaned_data)
        if created:
            box_status.save()

        return redirect('v_status_list')

##########
# Linhas #
##########

class LineList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Line
    #Caminho do arquivo html
    template_name = 'telecom/line/line_list.html'
    #Número de itens por página
    paginate_by = 20
    #Nome da variável do Model no html
    context_object_name = 'lines'

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
    paginate_by = 20
    #Nome da variável do Model no html
    context_object_name = 'smartphones'

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

        smartphone_model = SmartModel.objects.all()

        smartphone_status = SmartStatus.objects.all()

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
                Q(obj_model__exact=SmartModel.objects.get(name=filter_model))
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_status:
            qs = qs.filter(
                Q(status__exact=SmartStatus.objects.get(name=filter_status))
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
    paginate_by = 20
    #Nome da variável do Model no html
    context_object_name = 'vivoboxs'

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

        vivobox_model = BoxModel.objects.all()

        vivobox_status = BoxStatus.objects.all()

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
                Q(obj_model__exact=BoxModel.objects.get(name=filter_model))
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_status:
            qs = qs.filter(
                Q(status__exact=BoxStatus.objects.get(name=filter_status))
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