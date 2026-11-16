from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    """
    Modelo de perfil estendido para o Usuário do sistema.
    Atende aos requisitos de dados adicionais de contato e localização.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name="Usuário"
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone / WhatsApp"
    )
    endereco = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Endereço Completo"
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cidade"
    )
    estado = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="Estado (UF)"
    )
    data_nascimento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Nascimento"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"
        ordering = ['-data_cadastro']

    def __str__(self):
        nome_exibicao = self.user.get_full_name() or self.user.username
        return f"Perfil de {nome_exibicao} ({self.user.email})"


@receiver(post_save, sender=User)
def criar_ou_salvar_perfil(sender, instance, created, **kwargs):
    """
    Garante que todo User criado possua automaticamente um Perfil associado.
    """
    if created:
        Perfil.objects.create(user=instance)
    else:
        # Garante criação mesmo se criado via fixtures/superuser sem o sinal inicial
        Perfil.objects.get_or_create(user=instance)
