from django.forms import ModelForm

from .models import Chart

###########
# Gráfico #
###########

class FormChartEdit(ModelForm):
    #Validar e alterar os campos do formulário
    def clean(self):
        data = self.cleaned_data
        name = data.get('name')

        #Verifica campo Nome
        if name == '-' or not name:
            self.add_error(
                'name',
                'Preencha o campo Nome'
            )
    
    #Define os campos a serem alterados
    class Meta:
        model = Chart
        fields = ['name', 'query', 'visible']

##########
# Status #
##########

class FormChartAdd(ModelForm):
    #Validar e alterar os campos do formulário
    def clean(self):
        data = self.cleaned_data
        name = data.get('name')

        #Verifica campo Nome
        if name == '-' or not name:
            self.add_error(
                'name',
                'Preencha o campo Nome'
            )
    
    #Define os campos a serem alterados
    class Meta:
        model = Chart
        fields = ['name', 'query', 'visible']
