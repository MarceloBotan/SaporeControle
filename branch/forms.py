from django.forms import ModelForm
from .models import  UploadFile

#Formulário para editar uma linha
class FormUploadFile(ModelForm):
    #Define os campos a serem alterados
    class Meta:
        model = UploadFile
        fields = ['file']