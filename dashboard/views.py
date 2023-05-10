from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, ListView, UpdateView, CreateView
from django.contrib import messages
from django.db import connection

from django.core.exceptions import PermissionDenied

from django.db.models import Q
from telecom.models import Line, Smartphone, Vivobox
from telecom.models import SmartphoneModel, VivoboxModel, LinePlan
from telecom.models import LineStatus, LineStatusRFP, SmartphoneStatus, VivoboxStatus

from .forms import FormChartAdd, FormChartEdit
from .models import Chart

from sapore_controle.settings import PAGINATE_BY

@login_required(redirect_field_name='login')
def index(request):
    try:
        user_permission_group = request.user.groups.get().name

        if 'tg' in user_permission_group:
            return redirect('line_list')
        if 'telecom' in user_permission_group:
            return redirect('dashboard_telecom')
    except:
        pass
    return render(request, 'dashboard/index.html')

@login_required(redirect_field_name='login')
def delete_object(request, _type, _id):
    url_redirect = _type + '_list'
    _object = None

    if not user_has_perm(request, 'delete', _type):
        messages.error(request, f'Seu usuário não possui acesso para deletar esse item')
        return redirect(url_redirect)

    try:
        _object = get_object(_type, _id)
    except:
        messages.error(request, 'Item não encontrado')
        return redirect(url_redirect)

    try:
        _object.delete()
        messages.success(request, 'Item removido')
        return redirect(url_redirect)
    except:
        messages.error(request, 'Item não pode ser removido')
    
    return redirect(url_redirect)

@login_required(redirect_field_name='login')
def edit_object(request, _type, _id):
    url_list = _type + '_list'
    url_edit = _type + '_edit'

    if not user_has_perm(request, 'change', _type):
        messages.error(request, f'Seu usuário não possui acesso para editar esse item')
        return redirect(url_list)

    return redirect(url_edit, _id)

@login_required(redirect_field_name='login')
def add_object(request, _type):
    url_list = _type + '_list'
    url_add = _type + '_add'

    if not user_has_perm(request, 'add', _type):
        messages.error(request, f'Seu usuário não possui acesso para adicionar esse item')
        return redirect(url_list)

    return redirect(url_add)

def get_object(_type, _id):
    object = None
    if 'line' in _type:
        if 'plan' in _type:
            object = LinePlan.objects.get(id=_id)
        elif 'status_rfp' in _type:
            object = LineStatusRFP.objects.get(id=_id)
        elif 'status' in _type:
            object = LineStatus.objects.get(id=_id)
        else:
            object = Line.objects.get(id=_id)
    elif 'smartphone' in _type:
        if 'model' in _type:
            object = SmartphoneModel.objects.get(id=_id)
        elif 'status' in _type:
            object = SmartphoneStatus.objects.get(id=_id)
        else:
            object = Smartphone.objects.get(id=_id)
    elif 'vivobox' in _type:
        if 'model' in _type:
            object = VivoboxModel.objects.get(id=_id)
        elif 'status' in _type:
            object = VivoboxStatus.objects.get(id=_id)
        else:
            object = Vivobox.objects.get(id=_id)
    elif 'chart' in _type:
        object = Chart.objects.get(id=_id)
    return object

def user_has_perm(request, permission, _type):
    qs_groups = request.user.groups.all()
    for qs_group in qs_groups:
        if qs_group.permissions.filter(Q(codename__contains=permission) & Q(codename__contains=_type.replace('_',''))):
            return True
    return False

#############
# Dashboard #
#############

class DashboardTelecom(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    #Caminho do arquivo html
    template_name = 'dashboard/dashboard.html'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'dashboard.view_chart'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        charts = Chart.objects.all()

        qs_titles = []
        qs_labels = []
        qs_legends = []
        qs_totals = []

        _qs = None
        i = 0
        for chart in charts:
            if not chart.visible:
                continue

            qs_titles.append(chart.name)
            qs_labels.append([])
            qs_totals.append([])
            qs_legends.append([])

            split_data = chart.query.split()
            txt = ''
            for slice in split_data:
                txt += slice + ' '
            with connection.cursor() as c:
                try:
                    c.execute(txt)
                except:
                    continue
                _qs = c.fetchall()

                _legends = -1
                for k in range(len(_qs)):
                    if _qs[k][0] not in qs_labels[i]:
                        qs_labels[i].append(_qs[k][0])
                        
                    if _qs[k][1] not in qs_legends[i]:
                        qs_legends[i].append(_qs[k][1])
                        qs_totals[i].append([_qs[k][2]])
                        _legends += 1
                    else:
                        qs_totals[i][_legends].append(_qs[k][2])
            i += 1

        context['qs_titles'] = qs_titles
        context['qs_labels'] = qs_labels
        context['qs_legends'] = qs_legends
        context['qs_totals'] = qs_totals

        return context

############
# Gráficos #
############

def chart_visibility(request, _id, show):
    try:
        chart = Chart.objects.get(id=_id)
        chart.visible = show
        chart.save()
    except:
        messages.error(request, 'Id não encontrado')

    return redirect('chart_list')

class ChartList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Chart
    #Caminho do arquivo html
    template_name = 'dashboard/chart_list.html'
    #Número de itens por página
    paginate_by = PAGINATE_BY
    #Nome da variável do Model no html
    context_object_name = 'objects'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'dashboard.view_chart'

    #Envia a Query ordenada para o HTML
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('name', '-id')
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["url_delete"] = '/delete_object/chart/'
        return context

class ChartEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Chart
    #Caminho do arquivo html
    template_name = 'dashboard/chart_edit.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormChartEdit

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'dashboard.change_chart'

    def form_valid(self, form):
        chart = self.get_object()
        chart.name = form.cleaned_data['name']
        chart.query = form.cleaned_data['query']
        chart.visible = form.cleaned_data['visible']

        chart.save()

        return redirect('chart_list')

class ChartAdd(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Chart
    #Caminho do arquivo html
    template_name = 'dashboard/chart_add.html'
    #Nome da variável do Model no html
    context_object_name = 'object'
    #Formulário para editar a linha
    form_class = FormChartAdd

    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'

    #Permissão para acessar a página
    permission_required = 'dashboard.add_chart'

    def form_valid(self, form):
        chart, created = Chart.objects.get_or_create(**form.cleaned_data)
        
        if created:
            chart.save()

        return redirect('chart_list')

