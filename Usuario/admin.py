from django.contrib import admin
from .models import Usuario

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'user')
    list_display_links = ('id',)


admin.site.register(Usuario, UsuarioAdmin)