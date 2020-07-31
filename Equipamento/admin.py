from django.contrib import admin
from .models import Equipamento, Equip_Projeto


class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pn', 'date_entered')
    list_display_links = ('id', 'pn')
    search_fields = ('pn',)


class Equip_ProjetoAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_projeto', 'id_equip', 'valor', 'qty')
    list_display_links = ('id',)
    search_fields = ('id', 'id_projeto', 'id_equip')


admin.site.register(Equipamento, EquipamentoAdmin)
admin.site.register(Equip_Projeto, Equip_ProjetoAdmin)

