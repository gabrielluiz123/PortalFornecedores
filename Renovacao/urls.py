from django.urls import path
from . import views

urlpatterns = [
    path('', views.DetalhesIndex.as_view(), name='renovacoes'),
    path('Detalhe/<int:pk>', views.DetalheRenovacao.as_view(), name='detalhe_renovacao'),
    path('AprovarRenovacao/<int:pk>', views.AprovarRenovacao.as_view(), name='aprovar_renovacao'),
    path('ReprovarRenovacao/<int:pk>', views.ReprovarRenovacao.as_view(), name='reprovar_renovacao'),
    path('Renovar/<int:pk>', views.SaveRenovacao.as_view(), name='renovar_registro'),
]