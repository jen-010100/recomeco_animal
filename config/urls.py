from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from animais.views import HomeView, SobreNosView, ComoAjudarView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('sobre-nos/', SobreNosView.as_view(), name='sobre'),
    path('como-ajudar/', ComoAjudarView.as_view(), name='como_ajudar'),
    path('', include('animais.urls')),
    path('conta/', include('usuarios.urls')),
]

# Configuração para servir arquivos estáticos e de mídia durante o desenvolvimento local
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
