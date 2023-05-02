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
    data = models.TextField()

    def __str__(self) -> str:
        return self.name