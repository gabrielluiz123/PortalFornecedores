from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.DetalhesIndex.as_view(), name='detalhes'),
    path('Aguardando/', views.DetalhesIndexAguardando.as_view(), name='detalhes_aguardando'),
    path('Expirado/', views.DetalhesIndexExpirado.as_view(), name='expirado'),
    path('Reprovados/', views.DetalhesIndexReprovados.as_view(), name='detalhes_reprovados'),
    path('Aprovados/', views.DetalhesIndexAprovados.as_view(), name='detalhes_aprovados'),
    path('Aprovar_Revenda/', views.DetalheAprovarRevenda.as_view(), name='aprovar_revenda'),
    path('Atualizar/<int:pk>', views.AtualizarRegistro.as_view(), name='att_registro'),
    path('Renovacao/', include('Renovacao.urls')),
    path('Atualizar_Save/<int:pk>', views.AtualizarRegistroSave.as_view(), name='att_registro_save'),
    path('Detalhe/<int:pk>', views.DetalheIndex.as_view(), name='detalhe'),
    path('DetalheRevenda/<int:pk>', views.DetalheRevendaIndex.as_view(), name='detalhe_revenda'),
    path('Busca/', views.PostBusca.as_view(), name='post_busca'),
    path('aprovar_revenda/<int:pk>', views.Aprovar_Revenda.as_view(), name='aprovar_a_revenda'),
    path('aprovar/<int:pk>', views.Aprovar.as_view(), name='aprovar'),
    path('reprovar/<int:pk>', views.Reprovar.as_view(), name='reprovar'),
    path('reprovar_revenda/<int:pk>', views.Reprovar_Revenda.as_view(), name='reprovar_revenda'),
]