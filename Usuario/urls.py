from django.urls import path
from . import views

urlpatterns = [
    path('', views.ResetIndex.as_view(), name='user_reset'),
    path('Confirma/', views.ResetConfirma.as_view(), name='confirma_troca'),
]