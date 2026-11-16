from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.urls import reverse


class Animal(models.Model):
    """
    Modelo representativo dos animais acolhidos pela plataforma Recomeço Animal.
    Atende tanto à modalidade de Adoção Gratuita quanto à de Venda Responsável por Valor Acessível.
    """

    ESPECIE_CHOICES = [
        ('Cachorro', 'Cachorro'),
        ('Gato', 'Gato'),
        ('Cavalo', 'Cavalo / Equino'),
        ('Coelho', 'Coelho'),
        ('Passaro', 'Pássaro (Legalizado)'),
        ('Porquinho-da-índia', 'Porquinho-da-índia'),
        ('Outro', 'Outro'),
    ]

    SEXO_CHOICES = [
        ('Macho', 'Macho'),
        ('Femea', 'Fêmea'),
    ]

    PORTE_CHOICES = [
        ('Pequeno', 'Pequeno'),
        ('Medio', 'Médio'),
        ('Grande', 'Grande'),
    ]

    MODALIDADE_CHOICES = [
        ('adocao', 'Adoção Gratuita'),
        ('venda', 'Venda Responsável por Valor Acessível'),
    ]

    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('reservado', 'Reservado'),
        ('adotado', 'Adotado / Destinado'),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome do Animal")
    especie = models.CharField(max_length=40, choices=ESPECIE_CHOICES, verbose_name="Espécie")
    raca = models.CharField(max_length=100, verbose_name="Raça / Mistura")
    idade = models.CharField(max_length=50, verbose_name="Idade Aproximada")
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, verbose_name="Sexo")
    porte = models.CharField(max_length=20, choices=PORTE_CHOICES, verbose_name="Porte")
    descricao = models.TextField(verbose_name="Descrição e Apresentação")
    historico_resgate = models.TextField(verbose_name="Histórico de Maus-tratos e Resgate")
    condicoes_saude = models.TextField(verbose_name="Condições Atuais de Saúde e Vacinação")
    necessidades_especiais = models.TextField(
        blank=True,
        default="",
        verbose_name="Necessidades Especiais ou Cuidados Contínuos"
    )
    personalidade = models.TextField(
        blank=True,
        default="",
        verbose_name="Personalidade e Comportamento"
    )
    imagem_principal = models.ImageField(
        upload_to="animais/",
        verbose_name="Imagem Principal"
    )
    modalidade = models.CharField(
        max_length=20,
        choices=MODALIDADE_CHOICES,
        default='adocao',
        verbose_name="Modalidade de Destinação"
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Acessível de Contribuição (R$)",
        help_text="Aplicável prioritariamente para animais de grande porte (equinos) para cobrir manutenção."
    )
    localizacao = models.CharField(
        max_length=120,
        verbose_name="Localização (Cidade - Estado)",
        help_text="Ex: Curitiba - PR"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='disponivel',
        verbose_name="Situação / Status Atual"
    )
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='animais_cadastrados',
        verbose_name="Responsável pelo Resgate / Cadastro"
    )
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )

    class Meta:
        verbose_name = "Animal Resgatado"
        verbose_name_plural = "Animais Resgatados"
        ordering = ['-data_cadastro']

    def __str__(self):
        return f"{self.nome} ({self.get_especie_display()}) - {self.get_modalidade_display()}"

    def clean(self):
        super().clean()
        if self.valor and self.valor < Decimal('0.00'):
            raise ValidationError({'valor': 'O valor não pode ser negativo.'})

        # Se for adoção gratuita, valor deve ser zerado
        if self.modalidade == 'adocao' and self.valor and self.valor > Decimal('0.00'):
            self.valor = Decimal('0.00')

    @property
    def is_disponivel(self):
        return self.status == 'disponivel'

    @property
    def is_grande_porte_ou_equino(self):
        return self.especie == 'Cavalo' or self.porte == 'Grande'

    def get_absolute_url(self):
        return reverse('animais:detalhe_animal', kwargs={'pk': self.pk})


class ImagemAnimal(models.Model):
    """
    Galeria de fotografias adicionais para detalhamento do animal resgatado.
    """
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='imagens_adicionais',
        verbose_name="Animal"
    )
    imagem = models.ImageField(
        upload_to="animais/galeria/",
        verbose_name="Fotografia Adicional"
    )
    legenda = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Legenda / Momento do Resgate"
    )
    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fotografia Adicional"
        verbose_name_plural = "Galeria de Fotografias"

    def __str__(self):
        return f"Foto de {self.animal.nome} - {self.legenda or 'Sem legenda'}"


class Solicitacao(models.Model):
    """
    Modelo de solicitação de adoção ou demonstração de interesse em aquisição responsável.
    Estabelece relação entre User e Animal com controle de status e histórico.
    """

    TIPO_CHOICES = [
        ('adocao', 'Solicitação de Adoção Gratuita'),
        ('venda', 'Demonstração de Interesse em Venda Responsável'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em análise'),
        ('aprovada', 'Aprovada'),
        ('recusada', 'Recusada'),
        ('concluida', 'Concluída'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='solicitacoes',
        verbose_name="Interessado"
    )
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='solicitacoes',
        verbose_name="Animal Solicitado"
    )
    tipo_solicitacao = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Solicitação"
    )
    justificativa = models.TextField(
        verbose_name="Por que você deseja adotar ou acolher este animal?",
        help_text="Conte sobre sua motivação e carinho para com o animal."
    )
    experiencia_animais = models.TextField(
        verbose_name="Experiência prévia com animais de estimação / grande porte",
        help_text="Já teve animais antes? Possui veterinário de confiança?"
    )
    condicoes_moradia = models.TextField(
        verbose_name="Condições de moradia e espaço físico",
        help_text="Descreva sua residência (casa, apartamento, quintal telado, sítio, hípica, etc.)."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name="Status da Solicitação"
    )
    observacoes_admin = models.TextField(
        blank=True,
        default="",
        verbose_name="Observações do Administrador / Equipe de Resgate",
        help_text="Anotações internas sobre entrevista, triagem e inspeção do local."
    )
    data_solicitacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Solicitação"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data da Última Atualização"
    )

    class Meta:
        verbose_name = "Solicitação de Adoção / Interesse"
        verbose_name_plural = "Solicitações de Adoção e Interesses"
        ordering = ['-data_solicitacao']

    def __str__(self):
        return f"Solicitação #{self.id} - {self.usuario.get_full_name() or self.usuario.username} -> {self.animal.nome} ({self.get_status_display()})"

    def clean(self):
        super().clean()
        # Não permitir solicitação para animais indisponíveis
        if self.animal_id and not self.animal.is_disponivel and not self.pk:
            raise ValidationError(
                f"O animal {self.animal.nome} não está disponível no momento (Status: {self.animal.get_status_display()})."
            )

        # Não permitir solicitações ativas duplicadas do mesmo usuário para o mesmo animal
        if self.usuario_id and self.animal_id and not self.pk:
            solicitacoes_ativas = Solicitacao.objects.filter(
                usuario=self.usuario,
                animal=self.animal,
                status__in=['pendente', 'em_analise']
            )
            if solicitacoes_ativas.exists():
                raise ValidationError(
                    f"Você já possui uma solicitação em andamento para o animal {self.animal.nome}."
                )


class Historia(models.Model):
    """
    Histórias de superação de animais resgatados para conscientização e inspiração.
    """
    titulo = models.CharField(max_length=150, verbose_name="Título da História")
    descricao = models.TextField(verbose_name="Relato de Superação e Recuperação")
    imagem = models.ImageField(
        upload_to="historias/",
        verbose_name="Fotografia de Superação"
    )
    animal_relacionado = models.ForeignKey(
        Animal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historias',
        verbose_name="Animal Relacionado (Opcional)"
    )
    data_publicacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Publicação"
    )

    class Meta:
        verbose_name = "História de Superação"
        verbose_name_plural = "Histórias de Superação"
        ordering = ['-data_publicacao']

    def __str__(self):
        return self.titulo
