from django.contrib import admin
from .models import Line, Smartphone, VivoBox

class LineAdmin(admin.ModelAdmin):
    list_display = ('number', 'telecom', 'name',)
    list_display_links = ('number',)
    list_filter = ('telecom',)

class SmartphoneAdmin(admin.ModelAdmin):
    list_display = ('obj_model', 'imei_1', 'name',)
    list_display_links = ('obj_model',)
    list_filter = ('obj_model',)

class VivoBoxAdmin(admin.ModelAdmin):
    list_display = ('obj_model', 'imei_1', 'name',)
    list_display_links = ('obj_model',)
    list_filter = ('obj_model',)

admin.site.register(Line, LineAdmin)
admin.site.register(Smartphone, SmartphoneAdmin)
admin.site.register(VivoBox, VivoBoxAdmin)
