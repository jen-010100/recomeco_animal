from django.urls import path
from . import views

app_name = 'animais'

urlpatterns = [
    path('animais/', views.AnimalListView.as_view(), name='catalogo'),
    path('animais/adocao/', views.AnimalListView.as_view(), {'modalidade': 'adocao'}, name='catalogo_adocao'),
    path('animais/cavalos-e-grande-porte/', views.AnimalListView.as_view(), {'grande_porte': '1'}, name='catalogo_cavalos'),
    path('animais/<int:pk>/', views.AnimalDetailView.as_view(), name='detalhe_animal'),
    path('animais/<int:pk>/solicitar/', views.SolicitacaoCreateView.as_view(), name='solicitar_adocao'),
    path('solicitacao/<int:pk>/cancelar/', views.SolicitacaoDeleteView.as_view(), name='cancelar_solicitacao'),
]

