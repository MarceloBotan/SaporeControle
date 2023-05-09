from django.forms import ModelForm

from .models import Printer

from branch.models import Branch

class FormPrinter(ModelForm):
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
        model = Printer
        fields = ['name']

class FormAddPrinter(ModelForm):
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
        model = Printer
        fields = ['name']
