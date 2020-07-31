from django.contrib import admin
from .models import Cliente_Final, Revenda, Vendedor, Revenda_User, Empresa


class RevendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'razao_social', 'cnpj', 'date_entered')
    list_display_links = ('id', 'razao_social')
    search_fields = ('razao_social', 'cnpj')


class Cliente_FinalAdmin(admin.ModelAdmin):
    list_display = ('id', 'razao_social', 'cnpj', 'date_entered')
    list_display_links = ('id', 'razao_social')
    search_fields = ('razao_social', 'cnpj')


class VendedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'empresa')
    list_display_links = ('id', 'nome')
    search_fields = ('id', 'nome', 'empresa')


class Revenda_UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'revenda')
    list_display_links = ('id', 'nome')
    search_fields = ('id', 'nome', 'revenda')


class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    list_display_links = ('id', 'nome')
    search_fields = ('id', 'nome')


admin.site.register(Revenda, RevendaAdmin)
admin.site.register(Cliente_Final, Cliente_FinalAdmin)
admin.site.register(Vendedor, VendedorAdmin)
admin.site.register(Revenda_User, Revenda_UserAdmin)
admin.site.register(Empresa, EmpresaAdmin)

