from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, ListView, UpdateView, CreateView
from django.contrib import messages
from django.db import connection

from telecom.models import Line, Smartphone, VivoBox
from telecom.models import SmartModel, BoxModel
from telecom.models import LineStatus, SmartStatus, BoxStatus, LineTelecom

from django.core.exceptions import PermissionDenied

from .forms import FormChartAdd, FormChartEdit
from .models import Chart

from sapore_controle.settings import PAGINATE_BY


@login_required(redirect_field_name='login')
def index(request):
    user_permission_group = request.user.groups.get().name

    if 'telecom' in user_permission_group:
        return redirect('dashboard_telecom')
    return render(request, 'dashboard/index.html')

#############
# Dashboard #
#############

class DashboardTelecom(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    #Caminho do arquivo html
    template_name = 'dashboard/dashboard.html'
    #Redireciona caso não estiver logado
    login_url = '/accounts/login/'
    #Permissão para acessar a página
    permission_required = 'telecom.view_lineplan'

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
            qs_titles.append(chart.name)
            qs_labels.append([])
            qs_totals.append([])
            qs_legends.append([])

            split_data = chart.data.split()
            txt = ''
            for slice in split_data:
                txt += slice + ' '
            with connection.cursor() as c:
                c.execute(txt)
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

@login_required(redirect_field_name='login')
def delete_chart(request, id):
    if 'sapore_telecom' not in request.user.groups.get().name and 'admin' not in request.user.groups.get().name:
        #Sobre erro 403 - Permissão Negada
        raise PermissionDenied()

    chart = Chart.objects.get(id=id)
    chart.delete()
    
    messages.success(request, 'Gráfico removido')
    return redirect('chart_list')

############
# Gráficos #
############

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

        context["url_delete"] = '/dashboard/delete_chart/'
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
        chart.data = form.cleaned_data['data']

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

