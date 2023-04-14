from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import StreamingHttpResponse

from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import TemplateView

from django.utils import timezone

from .forms import FormLine, FormAddLine, FormSmartphone, FormAddSmartphone, FormVivoBox, FormAddVivoBox
from .forms import FormSmartModel, FormBoxModel, FormLinePlan

from django.core.exceptions import PermissionDenied

from django.db.models import Q, Count
from .models import Line, Smartphone, VivoBox, LinePlan
from .models import SmartModel, BoxModel

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
        #Sobre erro 403 - Permissão Negada
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

    match telecom_type:
        case 'line':
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
        case 'smartphone':
            prefix = 'smartphones_'
            if csv_simple == 1:
                sufix = 'simplificado_'
                header = ([header] for header in smartphone_headers_simple)
                rows = ([str(smartphone.s_model),str(smartphone.imei_1), str(smartphone.receipt), str(smartphone.name), 
                            str(smartphone.branch), str(smartphone.number), str(smartphone.status), 
                            ] for smartphone in smartphones)
            else:
                header = ([header] for header in smartphone_headers)
                rows = ([str(smartphone.s_model),str(smartphone.imei_1), str(smartphone.imei_2),  str(smartphone.receipt), 
                            str(smartphone.name), str(smartphone.branch), str(smartphone.number), str(smartphone.status), 
                            str(smartphone.date_update)] for smartphone in smartphones)
        case 'vivobox':
            prefix = 'vivobox_'
            if csv_simple == 1:
                sufix = 'simplificado_'
                header = ([header] for header in vivobox_headers_simple)
                rows = ([str(vivobox.v_model),str(vivobox.imei_1), str(vivobox.name), str(vivobox.branch), 
                            str(vivobox.number), str(vivobox.status)] for vivobox in vivoboxs)
            else:
                header = ([header] for header in vivobox_headers)
                rows = ([str(vivobox.v_model),str(vivobox.imei_1),  str(vivobox.receipt), str(vivobox.name), 
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
    if 'sapore' not in request.user.groups.get().name:
        #Sobre erro 403 - Permissão Negada
        raise PermissionDenied()

    match telecom_type:
        case 'vivobox':
            try:
                box_model = BoxModel.objects.get(id=model_id)
                box_model.delete()
            except:
                messages.error(request, 'Modelo não pode ser deletado')
            return redirect('v_model_list')
        
        case 'smartphone':
            try:
                smart_model = SmartModel.objects.get(id=model_id)
                smart_model.delete()
            except:
                messages.error(request, 'Modelo não pode ser deletado')
            return redirect('s_model_list')
        
        case 'line':
            try:
                line_plan = LinePlan.objects.get(id=model_id)
                line_plan.delete()
            except:
                messages.error(request, 'Modelo não pode ser deletado')
            return redirect('line_plan_list')
    
    return redirect('index')

class Index(LoginRequiredMixin, TemplateView):
    #Caminho do arquivo html
    template_name = 'telecom/index.html'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

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

        smartphone_status = (Smartphone.objects
            .filter()
            .values('status')
            .annotate(status_count=Count('status'))
            .order_by('status')
        )

        smartphone_models = (Smartphone.objects
            .filter()
            .values('s_model')
            .annotate(s_model_count=Count('s_model'))
            .order_by('s_model')
        )

        smartphones = Smartphone.objects \
            .filter() \
            .values('status', 's_model') \
            .annotate(status_count=Count('status')) \
            .order_by('status')

        smartphone_filter_models = []
        smartphone_models_names = []
        s_models = []
        for s_model in smartphone_models:
            smart_model = SmartModel.objects.get(id=s_model['s_model']).name
            smartphone_models_names.append(smart_model)
            if self.request.GET.get('smartphone_' + smart_model) == 'on':
                smartphone_filter_models.append(smart_model)
                s_models.append(smart_model)

        if not smartphone_filter_models:
            for s_model in smartphone_models_names:
                smart_model = s_model
                smartphone_filter_models.append(smart_model)
                s_models.append(smart_model)

        s_model_count = []
        for i in range(len(s_models)):
            smartphone_model = []
            for s in smartphone_status:
                has_append_model = False
                for smartphone in smartphones:
                    if smartphone['status'].upper() != s['status'].upper():
                        continue
                    
                    if SmartModel.objects.get(id=smartphone['s_model']).name == s_models[i]:
                        smartphone_model.append(smartphone['status_count'])
                        has_append_model = True
                    
                if not has_append_model:
                    smartphone_model.append(0)
            s_model_count.append(smartphone_model)
        
        line_status = (Line.objects
            .filter()
            .values('status')
            .annotate(status_count=Count('status'))
            .order_by('status')
        )

        line_telecom = (Line.objects
            .filter()
            .values('telecom')
            .annotate(status_count=Count('telecom'))
            .order_by('telecom')
        )

        lines = (Line.objects
            .filter()
            .values('status', 'telecom')
            .annotate(status_count=Count('status'))
            .order_by('status')
        )

        filter_line_telecom = []
        telecoms = []
        for telecom in line_telecom:
            if self.request.GET.get('line_telecom_' + telecom['telecom']) == 'on':
                filter_line_telecom.append(telecom['telecom'])
                telecoms.append(telecom['telecom'])

        if not filter_line_telecom:
            for telecom in line_telecom:
                filter_line_telecom.append(telecom['telecom'])
                telecoms.append(telecom['telecom'].upper())

        telecom_count = []
        for i in range(len(telecoms)):
            aux = []
            for s in line_status:
                has_append_aux = False
                for line in lines:
                    if line['status'].upper() != s['status'].upper():
                        continue

                    if line['telecom'].upper() == telecoms[i]:
                        aux.append(line['status_count'])
                        has_append_aux = True
                    
                if not has_append_aux:
                    aux.append(0)
            telecom_count.append(aux)
        
        vivobox_status = (VivoBox.objects
            .filter()
            .values('status')
            .annotate(status_count=Count('status'))
            .order_by('status')
        )

        vivobox_models = (VivoBox.objects
            .filter()
            .values('v_model')
            .annotate(status_count=Count('v_model'))
            .order_by('v_model')
        )

        vivoboxs = (VivoBox.objects
            .filter()
            .values('status', 'v_model')
            .annotate(status_count=Count('status'))
            .order_by('status')
        )

        vivobox_filter_models = []
        vivobox_models_names = []
        v_models = []
        for v_model in vivobox_models:
            box_model = BoxModel.objects.get(id=v_model['v_model']).name
            vivobox_models_names.append(box_model)
            if self.request.GET.get('vivobox_' + box_model) == 'on':
                vivobox_filter_models.append(box_model)
                v_models.append(box_model)

        if not vivobox_filter_models:
            for v_model in vivobox_models_names:
                vivobox_filter_models.append(v_model)
                v_models.append(v_model)

        v_model_count = []
        for i in range(len(v_models)):
            vivobox_model = []
            for v in vivobox_status:
                has_append_model = False
                for vivobox in vivoboxs:
                    if vivobox['status'].upper() != v['status'].upper():
                        continue
                    
                    if BoxModel.objects.get(id=vivobox['v_model']).name == v_models[i]:
                        vivobox_model.append(vivobox['status_count'])
                        has_append_model = True
                    
                if not has_append_model:
                    vivobox_model.append(0)
            v_model_count.append(vivobox_model)

        context["qs_smartphone_status"] = list(smartphone_status)
        context["qs_smartphone_models"] = smartphone_models_names
        context["qs_smartphone_filter_models"] = smartphone_filter_models
        context["qs_smartphone_count"] = list(s_model_count)
        context["qs_smartphone"] = list(smartphones)

        context["qs_line_status"] = list(line_status)
        context["qs_line_telecom"] = list(line_telecom)
        context["qs_line_count"] = list(telecom_count)
        context["qs_line_filter_telecom"] = filter_line_telecom
        context["qs_line"] = lines

        context["qs_vivobox_status"] = list(vivobox_status)
        context["qs_vivobox_models"] = vivobox_models_names
        context["qs_vivobox_filter_models"] = vivobox_filter_models
        context["qs_vivobox_count"] = list(v_model_count)
        context["qs_vivobox"] = list(vivoboxs)

        return context

############
# LinePlan #
############

class LinePlanList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = LinePlan
    #Caminho do arquivo html
    template_name = 'telecom/param/line_plan_list.html'
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
    template_name = 'telecom/param/line_plan_edit.html'
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

        line_plan.save()

        return redirect('line_plan_list')

class LinePlanAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = LinePlan
    #Caminho do arquivo html
    template_name = 'telecom/param/line_plan_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormLinePlan

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'telecom.add_lineplan'

    def form_valid(self, form):
        smart_model, created = LinePlan.objects.get_or_create(**form.cleaned_data)
        
        if created:
            smart_model.save()

        return redirect('line_plan_list')

##############
# SmartModel #
##############

class SmartModelList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = SmartModel
    #Caminho do arquivo html
    template_name = 'telecom/param/s_model_list.html'
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
    template_name = 'telecom/param/s_model_edit.html'
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
    template_name = 'telecom/param/s_model_add.html'
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

############
# BoxModel #
############

class BoxModelList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = BoxModel
    #Caminho do arquivo html
    template_name = 'telecom/param/v_model_list.html'
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
    template_name = 'telecom/param/v_model_edit.html'
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
    template_name = 'telecom/param/v_model_add.html'
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

        line_telecom = (Line.objects
            .filter()
            .values('telecom')
            .annotate(telecom_count=Count('telecom'))
            .order_by('telecom')
        )

        line_plan = (Line.objects
            .filter()
            .values('plan')
            .annotate(plan_count=Count('plan'))
            .order_by('plan')
        )

        line_status = (Line.objects
            .filter()
            .values('status')
            .annotate(status_count=Count('status'))
            .order_by('status')
        )

        context["qs_line_telecom"] = list(line_telecom)
        context["qs_line_plan"] = list(line_plan)
        context["qs_line_status"] = list(line_status)
        return context
        
#Herda as informações e ordenação da Query do LineList
class LineSearch(LineList):
    template_name = 'telecom/line/line_search.html'

    #Envia a Query com buscando o termo e com filtro de status para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        term = self.request.GET.get('term')
        filter_telecom = self.request.GET.get('filter_telecom')
        filter_plan = self.request.GET.get('filter_plan')
        filter_branch = self.request.GET.get('filter_branch')
        filter_status = self.request.GET.get('filter_status')
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_telecom:
            qs = qs.filter(
                Q(telecom__iexact=filter_telecom)
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_plan:
            qs = qs.filter(
                Q(plan__iexact=filter_plan)
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_status:
            qs = qs.filter(
                Q(status__iexact=filter_status)
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
            Q(name__icontains=term) | Q(number__contains=term) | Q(telecom__icontains=term) | Q(plan__icontains=term) | \
            Q(sim_card__contains=term) | Q(sim_card_old__contains=term) | Q(branch__contains=term)
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

        qs = qs.order_by('s_model', 'imei_1', '-id')

        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        smartphone_s_model = (Smartphone.objects
            .filter()
            .values('s_model')
            .annotate(s_model_count=Count('s_model'))
            .order_by('s_model')
        )

        smartphone_status = (Smartphone.objects
            .filter()
            .values('status')
            .annotate(status_count=Count('status'))
            .order_by('status')
        )

        context["qs_smartphone_status"] = list(smartphone_status)
        context["qs_smartphone_s_model"] = list(smartphone_s_model)
        return context

#Herda as informações e ordenação da Query do smartphoneList
class SmartphoneSearch(SmartphoneList):
    template_name = 'telecom/smartphone/smartphone_search.html'

    #Envia a Query com buscando o termo e com filtro de status para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        term = self.request.GET.get('term')
        filter_s_model = self.request.GET.get('filter_s_model')
        filter_branch = self.request.GET.get('filter_branch')
        filter_status = self.request.GET.get('filter_status')
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_s_model:
            qs = qs.filter(
                Q(s_model__iexact=filter_s_model)
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_status:
            qs = qs.filter(
                Q(status__iexact=filter_status)
            )

        #Caso tenha filtro, adiciona na Query o filtro
        if filter_branch:
            qs = qs.filter(
                Q(branch__iexact=filter_status)
            )

        if not term:
            return qs

        #Query com ordem, e busca
        qs = qs.filter(
            Q(name__icontains=term) | Q(number__contains=term) | Q(imei_1__contains=term) | Q(imei_2__contains=term) | \
            Q(s_model__contains=term) | Q(branch__contains=term)
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
            line_old.status = 'DISPONIVEL'
            line_old.date_update = timezone.now()
            line_old.save()
        except:
            pass

        smartphone.number = form.cleaned_data['number']

        #Altera as informações da linha
        try:
            line = Line.objects.get(number=form.cleaned_data['number'])
            line.name = form.cleaned_data['name']
            line.branch = form.cleaned_data['branch']

            line.status = 'ATIVO'
            line.date_update = timezone.now()
            line.save()
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
            line.branch = form.cleaned_data['branch']
            line.status = 'ATIVO'
            line.date_update = timezone.now()
            line.save()
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

        qs = qs.order_by('v_model', 'imei_1', '-id')

        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        vivobox_v_model = (VivoBox.objects
            .filter()
            .values('v_model')
            .annotate(v_model_count=Count('v_model'))
            .order_by('v_model')
        )

        vivobox_status = (VivoBox.objects
            .filter()
            .values('status')
            .annotate(status_count=Count('status'))
            .order_by('status')
        )

        context["qs_vivobox_status"] = list(vivobox_status)
        context["qs_vivobox_v_model"] = list(vivobox_v_model)
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
        filter_v_model = self.request.GET.get('filter_v_model')
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_v_model:
            qs = qs.filter(
                Q(v_model__iexact=filter_v_model)
            )
   
        #Caso tenha filtro, adiciona na Query o filtro
        if filter_status:
            qs = qs.filter(
                Q(status__iexact=filter_status)
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
            Q(name__icontains=term) | Q(number__contains=term) | Q(imei_1__contains=term) | \
            Q(v_model__contains=term) | Q(branch__contains=term)
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
            line_old.status = 'DISPONIVEL'
            line_old.date_update = timezone.now()
            line_old.save()
        except:
            pass

        vivobox.number = form.cleaned_data['number']
        
        #Altera as informações da linha
        try:
            line = Line.objects.get(number=form.cleaned_data['number'])
            line.name = form.cleaned_data['name']
            line.branch = form.cleaned_data['branch']
            line.status = 'ATIVO'
            line.date_update = timezone.now()
            line.save()
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
            line.branch = form.cleaned_data['branch']
            line.status = 'ATIVO'
            line.date_update = timezone.now()
            line.save()
        except:
            pass

        vivobox.save()

        return redirect('vivobox_list')