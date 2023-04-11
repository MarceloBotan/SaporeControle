from django.forms import ModelForm
from .models import Line, Smartphone, VivoBox, Branch
from telecom import models


def validator_line(self, data):
    name = data.get('name')
    sim_card = data.get('sim_card')
    status = data.get('status')
    branch = data.get('branch')
    name_mapped = data.get('name_mapped')
    branch_mapped = data.get('branch_mapped')

    #Verifica campo Status
    if status == '-':
        self.add_error(
            'status',
            'Preencha o campo Status'
        )
    
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

    if status == 'ATIVO' or status == 'AGUARDANDO ENDERECO' or status == 'ATUALIZADO' or status == 'VIP':
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
        fields = ['name', 'branch', 'status', 'action', 'sim_card', 'receipt', 'auth_attachment',\
                   'name_mapped', 'branch_mapped']

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
        fields = ['name', 'telecom', 'plan', 'number', 'sim_card','branch', 'status', 'action', \
                  'receipt', 'auth_attachment', 'name_mapped', 'branch_mapped']

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

    #Verifica campo Status
    if status == '-':
        self.add_error(
            'status',
            'Preencha o campo Status'
        )

    #Valida Linha
    if number != 0:
        try:
            line = Line.objects.get(number=number)

            #Verifica o plano da linha
            if models.LINE_PLAN_TYPES[line.plan] != 'VOZ':
                self.add_error(
                    'number',
                    'Plano da linha não é de Voz'
                )
    
            #Verifica se a linha já possui colaborador associado
            try:
                smartphone = Smartphone.objects.get(number=number)
                if (line.name != '-' and line.name != smartphone.name) or (line.branch and line.branch != branch):
                    self.add_error(
                        'number',
                        'Número já associado a uma Filial ou um Colaborador'
                    )
            except:
                pass
        except:
            self.add_error(
                'number',
                'Número não existe na relação'
            )

    if status == 'AGUARDANDO TERMO' or status == 'TERMO ASSINADO' or \
        status == 'AGUARDANDO ENDERECO' or status == 'ENVIADO' or status == 'ENTREGUE': 
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
        s_model = data.get('s_model')

        validator_smartphone(self, data)

        #Verifica se preencheu o campo Plano
        if s_model == '-':
            self.add_error(
                's_model',
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
        fields = ['s_model', 'imei_1', 'imei_2', 'receipt', 'status', 'name', 'branch', 'number', 'auth_attachment']

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

    #Verifica campo Status
    if status == '-':
        self.add_error(
            'status',
            'Preencha o campo Status'
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

    if status == 'AGUARDANDO TERMO' or status == 'TERMO ASSINADO' or \
        status == 'AGUARDANDO ENDERECO' or status == 'ENVIADO' or status == 'ENTREGUE':        
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
        v_model = data.get('v_model')

        validator_vivobox(self, data)

        #Verifica se preencheu o campo Plano
        if v_model == '-':
            self.add_error(
                'v_model',
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
        fields = ['v_model', 'imei_1', 'receipt', 'status', 'name', 'branch', 'number', 'auth_attachment']

