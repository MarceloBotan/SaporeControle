from django.forms import ModelForm

from .models import Line, Smartphone, VivoBox
from .models import SmartModel, BoxModel, LinePlan
from .models import LineStatus, LineStatusRFP, SmartStatus, BoxStatus

from branch.models import Branch

################
# Plano/Modelo #
################

class FormLinePlan(ModelForm):
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
        model = LinePlan
        fields = ['name', 'plan_type']

class FormSmartModel(ModelForm):
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
        model = SmartModel
        fields = ['name', 'date_release']

class FormBoxModel(ModelForm):
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
        model = BoxModel
        fields = ['name']

##########
# Status #
##########

class FormLineStatus(ModelForm):
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
        model = LineStatus
        fields = ['name']

class FormLineStatusRFP(ModelForm):
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
        model = LineStatusRFP
        fields = ['name']

class FormSmartStatus(ModelForm):
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
        model = SmartStatus
        fields = ['name']

class FormBoxStatus(ModelForm):
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
        model = BoxStatus
        fields = ['name']

#########
# Linha #
#########

def validator_line(self, data):
    name = data.get('name')
    sim_card = data.get('sim_card')
    status = data.get('status')
    branch = data.get('branch')
    name_mapped = data.get('name_mapped')
    branch_mapped = data.get('branch_mapped')
    
    #Valida Filial
    try:
        model_branch = Branch.objects.get(branch=branch)

        if model_branch.closed and (branch < 1599 or branch > 1999):
            self.add_error(
                'branch',
                'Filial encerrada'
            )
    except:
        if branch != 0 and (branch < 1599 or branch > 1999):
            self.add_error(
                'branch',
                'Filial inválida'
            )

    if status.name != 'Disponivel':
        #Valida nome
        if name == '-' and name_mapped:
            self.add_error(
                'name',
                'Preencha o campo Nome'
            )
        
        #Verifica se Filial foi digitada
        if branch == 0 and branch_mapped:
            self.add_error(
                'branch',
                'Preencha o campo Filial'
            )

    #Valida campo "sim_card"
    if len(sim_card) != 20:
        self.add_error(
            'sim_card',
            'SIM card precisa ter 20 caracteres'
        )

#Formulário para editar uma linha
class FormLine(ModelForm):
    #Validar e alterar os campos do formulário
    def clean(self):
        data = self.cleaned_data
        
        validator_line(self, data)

    #Define os campos a serem alterados
    class Meta:
        model = Line
        fields = ['name', 'sim_card', 'branch', 'action', 'name_mapped', 'branch_mapped', \
                  'accountable', 'status', 'status_rfp', 'consumption', 'vip', 'auth_attachment']

#Formulário para adicionar uma nova linha
class FormAddLine(ModelForm):
    #Validar e alterar os campos do formulário
    def clean(self):
        data = self.cleaned_data
        number = data.get('number')
        plan = data.get('plan')
        telecom = data.get('telecom')
    
        validator_line(self, data)
        
        #Verifica se preencheu o campo Plano
        if plan == '-':
            self.add_error(
                'plan',
                'Selecione um Plano'
            )

        #Verifica se preencheu o campo Operadora
        if telecom == '-':
            self.add_error(
                'telecom',
                'Selecione uma Operadora'
            )

        #Valida campo "number"
        if number < 11000000000 or number > 99999999999:
            self.add_error(
                'number',
                'Número inválido'
            )

        #Procura se número já existe
        try:
            Line.objects.get(number=number)
            self.add_error(
                'number',
                'Número já registrado'
            )
        except:
            pass

    #Define os campos a serem alterados
    class Meta:
        model = Line
        fields = ['name', 'number', 'sim_card', 'plan', 'branch', 'receipt', \
                   'status', 'status_rfp', 'vip', 'auth_attachment']

def validator_smartphone(self, data):
    name = data.get('name')
    number = data.get('number')
    branch = data.get('branch')
    status = data.get('status')

    #Valida Filial
    try:
        model_branch = Branch.objects.get(branch=branch)

        if model_branch.closed and (branch < 1599 or branch > 1999):
            self.add_error(
                'branch',
                'Filial encerrada'
            )
    except:
        if branch != 0 and (branch < 1599 or branch > 1999):
            self.add_error(
                'branch',
                'Filial inválida'
            )

    #Valida Linha
    if number != 0:
        try:
            line = Line.objects.get(number=number)

            line_plan = LinePlan.objects.get(name=line.plan)
            
            #Verifica o plano da linha
            if line_plan.plan_type != 'VOZ':
                self.add_error(
                    'number',
                    'Plano da linha não é de Voz'
                )
    
            #Verifica se a linha já possui colaborador associado
            if (line.name != '-' and line.name) or (line.branch and line.branch != branch):
                self.add_error(
                    'number',
                    'Número já associado a uma Filial ou um Colaborador'
                )
        except:
            self.add_error(
                'number',
                'Número não existe na relação'
            )

    if status.name != 'Estoque':
        #Valida Nome
        if name == '-':
            self.add_error(
                'name',
                'Preencha o campo Nome'
            )
        
        #Verifica se Filial foi digitada
        if branch == 0:
            self.add_error(
                'branch',
                'Preencha o campo Filial'
            )
        
        #Verifica se Linha foi digitada
        if number == 0:
            self.add_error(
                'number',
                'Preencha o campo Número'
            )

#Formulário para editar um smartphone
class FormSmartphone(ModelForm):
    #Validar e alterar os campos do formulário
    def clean(self):
        data = self.cleaned_data
    
        validator_smartphone(self, data)

    #Define os campos a serem alterados
    class Meta:
        model = Smartphone
        fields = ['status', 'name', 'branch', 'number', 'auth_attachment']

#Formulário para adicionar um novo smartphone
class FormAddSmartphone(ModelForm):
    def clean(self):
        data = self.cleaned_data
        imei_1 = data.get('imei_1')
        obj_model = data.get('obj_model')

        validator_smartphone(self, data)

        #Verifica se preencheu o campo Plano
        if obj_model == '-':
            self.add_error(
                'obj_model',
                'Selecione um Modelo'
            )
        
        #Valida o IMEI
        if not imei_1 or len(imei_1) != 15:
            self.add_error(
                'imei_1',
                'IMEI inválido'
            )

        #Procura se smartphone já existe
        try:
            Smartphone.objects.get(imei_1=imei_1)
            self.add_error(
                'imei_1',
                'Smartphone já registrado'
            )
        except:
            pass

    #Define os campos a serem alterados
    class Meta:
        model = Smartphone
        fields = ['obj_model', 'imei_1', 'imei_2', 'receipt', 'status', 'name', 'branch', 'number', 'auth_attachment']

def validator_vivobox(self, data):
    name = data.get('name')
    number = data.get('number')
    branch = data.get('branch')
    status = data.get('status')

    #Valida Filial
    try:
        model_branch = Branch.objects.get(branch=branch)

        if model_branch.closed and (branch < 1599 or branch > 1999):
            self.add_error(
                'branch',
                'Filial encerrada'
            )
    except:
        if branch != 0 and (branch < 1599 or branch > 1999):
            self.add_error(
                'branch',
                'Filial inválida'
            )

    #Valida Linha
    if number != 0:
        try:
            line = Line.objects.get(number=number)

            #Verifica o plano da linha
            #if line.plan != 'BOX':
            #    self.add_error(
            #        'number',
            #        'Plano da linha não é Box'
            #    )
    
            #Verifica se a linha já possui colaborador associado
            if (line.name != '-' and line.name != name) or (line.branch and line.branch != branch):
                self.add_error(
                    'number',
                    'Número já associado a uma Filial ou um Colaborador'
                )
        except:
            self.add_error(
                'number',
                'Número não existe na relação'
            )

    if status.name != 'Estoque':
        #Valida Nome
        if name == '-':
            self.add_error(
                'name',
                'Preencha o campo Nome'
            )

        #Verifica se Filial foi digitada
        if branch == 0:
            self.add_error(
                'branch',
                'Preencha o campo Filial'
            )
        
        #Verifica se Linha foi digitada
        if number == 0:
            self.add_error(
                'number',
                'Preencha o campo Número'
            )

#Formulário para editar um VivoBox
class FormVivoBox(ModelForm):
    #Validar e alterar os campos do formulário
    def clean(self):
        data = self.cleaned_data
        
        validator_vivobox(self, data)
    
    #Define os campos a serem alterados
    class Meta:
        model = VivoBox
        fields = ['status', 'name', 'branch', 'number', 'auth_attachment']

#Formulário para adicionar um novo VivoBox
class FormAddVivoBox(ModelForm):
    def clean(self):
        data = self.cleaned_data
        imei_1 = data.get('imei_1')
        obj_model = data.get('obj_model')

        validator_vivobox(self, data)

        #Verifica se preencheu o campo Plano
        if obj_model == '-':
            self.add_error(
                'obj_model',
                'Selecione um Modelo'
            )

        #Valida o IMEI
        if not imei_1 or len(imei_1) != 15:
            self.add_error(
                'imei_1',
                'IMEI inválido'
            )
        
        #Procura se smartphone já existe
        try:
            VivoBox.objects.get(imei_1=imei_1)
            self.add_error(
                'imei_1',
                'VivoBox já registrado'
            )
        except:
            pass

    #Define os campos a serem alterados
    class Meta:
        model = VivoBox
        fields = ['obj_model', 'imei_1', 'receipt', 'status', 'name', 'branch', 'number', 'auth_attachment']

