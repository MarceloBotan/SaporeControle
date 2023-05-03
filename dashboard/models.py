from django.db import models



class Chart(models.Model):
    """
    Data = SQL

    Return Table

    Label   |  Legend  | Total |
    ----------------------------
    'label' | 'legend' | 00000 |
    
    """

    name = models.CharField(max_length=255, default='-', verbose_name='Nome')
    query = models.TextField(verbose_name='Query')
    visible = models.BooleanField(default=True, verbose_name='Visível')

    def __str__(self) -> str:
        return self.name