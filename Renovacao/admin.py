from django.contrib import admin
from .models import Renovacao_Registro


class Renovacao_RegistroAdmin(admin.ModelAdmin):
    list_display = ('id', 'registro')
    list_display_links = ('id',)

admin.site.register(Renovacao_Registro, Renovacao_RegistroAdmin)
