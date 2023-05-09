from django.contrib import admin
from .models import Printer

class PrinterAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'name',)
    list_display_links = ('serial_number',)
    list_filter = ('serial_number',)

admin.site.register(Printer, PrinterAdmin)
