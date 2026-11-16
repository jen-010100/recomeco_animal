from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('cadastro/', views.CadastroView.as_view(), name='cadastro'),
    path('login/', views.LoginUsuarioView.as_view(), name='login'),
    path('logout/', views.LogoutUsuarioView.as_view(), name='logout'),
    path('minha-conta/', views.MinhaContaView.as_view(), name='minha_conta'),
]

