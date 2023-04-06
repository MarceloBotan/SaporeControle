from django.contrib import admin
from .models import Line, Smartphone, VivoBox

class LineAdmin(admin.ModelAdmin):
    list_display = ('number', 'telecom', 'name',)
    list_display_links = ('number',)
    list_filter = ('telecom',)

class SmartphoneAdmin(admin.ModelAdmin):
    list_display = ('s_model', 'imei_1', 'name',)
    list_display_links = ('s_model',)
    list_filter = ('s_model',)

class VivoBoxAdmin(admin.ModelAdmin):
    list_display = ('v_model', 'imei_1', 'name',)
    list_display_links = ('v_model',)
    list_filter = ('v_model',)

admin.site.register(Line, LineAdmin)
admin.site.register(Smartphone, SmartphoneAdmin)
admin.site.register(VivoBox, VivoBoxAdmin)
