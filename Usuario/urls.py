from django.urls import path
from . import views

urlpatterns = [
    path('', views.ResetIndex.as_view(), name='user_reset'),
    path('Confirma/', views.ResetConfirma.as_view(), name='confirma_troca'),
    path('Perfil/', views.Perfil.as_view(), name='perfil'),
    path('Salva_Perfil/', views.SalvaPerfil.as_view(), name='salva_perfil'),
    path('Gerenciar/', views.GerenciarUsuarios.as_view(), name='gerenciar_usuarios'),
    path('Inativar_Usuario/<int:pk>', views.InativarUsuario.as_view(), name='inativar_usuario'),
]