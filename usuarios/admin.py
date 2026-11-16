from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil do Usuário (Endereço e Contato)'
    fk_name = 'user'
    fields = ('telefone', 'data_nascimento', 'endereco', 'cidade', 'estado')


# Re-registra o modelo User com o PerfilInline integrado
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'get_telefone',
        'get_cidade_estado',
        'is_staff',
        'date_joined',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'perfil__telefone', 'perfil__cidade')

    def get_telefone(self, obj):
        return getattr(obj.perfil, 'telefone', '') if hasattr(obj, 'perfil') else ''
    get_telefone.short_description = "Telefone"

    def get_cidade_estado(self, obj):
        if hasattr(obj, 'perfil') and obj.perfil.cidade:
            return f"{obj.perfil.cidade}/{obj.perfil.estado}"
        return "-"
    get_cidade_estado.short_description = "Cidade/UF"


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefone', 'cidade', 'estado', 'data_nascimento', 'data_cadastro')
    list_filter = ('estado', 'data_cadastro')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'telefone', 'cidade')
    ordering = ('-data_cadastro',)
