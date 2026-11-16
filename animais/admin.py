from django.contrib import admin
from django.utils.html import format_html
from .models import Animal, ImagemAnimal, Solicitacao, Historia


class ImagemAnimalInline(admin.TabularInline):
    """Permite adicionar várias fotos adicionais diretamente na edição do animal."""
    model = ImagemAnimal
    extra = 1
    fields = ('imagem', 'legenda', 'preview_imagem')
    readonly_fields = ('preview_imagem',)

    def preview_imagem(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="width: 80px; height: 60px; object-fit: cover; border-radius: 6px;" />',
                obj.imagem.url
            )
        return "Sem imagem"
    preview_imagem.short_description = "Prévia"


class SolicitacaoInline(admin.StackedInline):
    """Exibe solicitações recebidas para este animal diretamente na página dele."""
    model = Solicitacao
    extra = 0
    can_delete = False
    fields = ('usuario', 'tipo_solicitacao', 'status', 'data_solicitacao', 'justificativa')
    readonly_fields = ('usuario', 'tipo_solicitacao', 'data_solicitacao', 'justificativa')


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        'preview_foto',
        'nome',
        'especie',
        'raca',
        'idade',
        'porte',
        'modalidade_badge',
        'valor_formatado',
        'status',
        'localizacao',
        'data_cadastro',
    )
    list_filter = ('modalidade', 'status', 'especie', 'porte', 'sexo', 'data_cadastro')
    search_fields = ('nome', 'raca', 'especie', 'localizacao', 'descricao', 'historico_resgate')
    ordering = ('-data_cadastro',)
    list_editable = ('status',)
    inlines = [ImagemAnimalInline, SolicitacaoInline]

    fieldsets = (
        ('Identificação e Espécie', {
            'fields': (
                ('nome', 'especie'),
                ('raca', 'sexo'),
                ('idade', 'porte'),
                'localizacao',
            )
        }),
        ('Destinação e Valores', {
            'fields': (
                ('modalidade', 'valor'),
                'status',
                'responsavel',
            ),
            'description': 'Configure se o animal está para adoção gratuita ou venda responsável com valor acessível.'
        }),
        ('Histórico e Saúde do Animal', {
            'fields': (
                'descricao',
                'historico_resgate',
                'condicoes_saude',
                'necessidades_especiais',
                'personalidade',
            )
        }),
        ('Fotografia Principal', {
            'fields': ('imagem_principal',),
        }),
    )

    actions = ['marcar_como_disponivel', 'marcar_como_reservado', 'marcar_como_adotado']

    def preview_foto(self, obj):
        if obj.imagem_principal:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.imagem_principal.url
            )
        return "Sem foto"
    preview_foto.short_description = "Foto"

    def modalidade_badge(self, obj):
        if obj.modalidade == 'adocao':
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
                '#244B3A',
                'Adoção Gratuita'
            )
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            '#80634F',
            'Venda Responsável'
        )
    modalidade_badge.short_description = "Modalidade"

    def status_badge(self, obj):
        cores = {
            'disponivel': '#2e7d32',
            'reservado': '#ed6c02',
            'adotado': '#0288d1',
        }
        cor = cores.get(obj.status, '#666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            cor,
            obj.get_status_display()
        )
    status_badge.short_description = "Situação"

    def valor_formatado(self, obj):
        if obj.modalidade == 'adocao' or obj.valor == 0:
            return "Gratuito"
        return f"R$ {obj.valor:.2f}"
    valor_formatado.short_description = "Valor"

    @admin.action(description="Marcar selecionados como Disponível")
    def marcar_como_disponivel(self, request, queryset):
        queryset.update(status='disponivel')
        self.message_user(request, "Animais marcados como Disponível.")

    @admin.action(description="Marcar selecionados como Reservado")
    def marcar_como_reservado(self, request, queryset):
        queryset.update(status='reservado')
        self.message_user(request, "Animais marcados como Reservado.")

    @admin.action(description="Marcar selecionados como Adotado / Destinado")
    def marcar_como_adotado(self, request, queryset):
        queryset.update(status='adotado')
        self.message_user(request, "Animais marcados como Adotado / Destinado.")


@admin.register(Solicitacao)
class SolicitacaoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'usuario_info',
        'animal_nome',
        'tipo_solicitacao_badge',
        'status',
        'data_solicitacao',
        'data_atualizacao',
    )
    list_filter = ('status', 'tipo_solicitacao', 'data_solicitacao')
    search_fields = (
        'usuario__first_name',
        'usuario__last_name',
        'usuario__username',
        'usuario__email',
        'animal__nome',
        'justificativa',
        'condicoes_moradia'
    )
    ordering = ('-data_solicitacao',)
    list_editable = ('status',)

    fieldsets = (
        ('Identificação da Solicitação', {
            'fields': (
                ('usuario', 'animal'),
                ('tipo_solicitacao', 'status'),
                ('data_solicitacao', 'data_atualizacao'),
            )
        }),
        ('Informações Fornecidas pelo Interessado', {
            'fields': (
                'justificativa',
                'experiencia_animais',
                'condicoes_moradia',
            )
        }),
        ('Avaliação e Gestão Interna da ONG', {
            'fields': ('observacoes_admin',),
            'description': 'Espaço para registrar entrevistas, vistoria residencial ou motivos de deferimento/indeferimento.'
        }),
    )
    readonly_fields = ('data_solicitacao', 'data_atualizacao')

    actions = ['aprovar_solicitacao', 'colocar_em_analise', 'recusar_solicitacao', 'concluir_solicitacao']

    def usuario_info(self, obj):
        nome = obj.usuario.get_full_name() or obj.usuario.username
        return f"{nome} ({obj.usuario.email})"
    usuario_info.short_description = "Interessado"

    def animal_nome(self, obj):
        return f"{obj.animal.nome} ({obj.animal.get_especie_display()})"
    animal_nome.short_description = "Animal"

    def tipo_solicitacao_badge(self, obj):
        return obj.get_tipo_solicitacao_display()
    tipo_solicitacao_badge.short_description = "Tipo"

    def status_badge(self, obj):
        cores = {
            'pendente': '#ed6c02',
            'em_analise': '#0288d1',
            'aprovada': '#2e7d32',
            'recusada': '#d32f2f',
            'concluida': '#455a64',
        }
        cor = cores.get(obj.status, '#666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            cor,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"

    @admin.action(description="Aprovar solicitações selecionadas")
    def aprovar_solicitacao(self, request, queryset):
        queryset.update(status='aprovada')
        self.message_user(request, "Solicitações aprovadas com sucesso.")

    @admin.action(description="Colocar em análise")
    def colocar_em_analise(self, request, queryset):
        queryset.update(status='em_analise')
        self.message_user(request, "Solicitações colocadas em análise.")

    @admin.action(description="Recusar solicitações selecionadas")
    def recusar_solicitacao(self, request, queryset):
        queryset.update(status='recusada')
        self.message_user(request, "Solicitações recusadas.")

    @admin.action(description="Concluir processo de adoção/aquisição")
    def concluir_solicitacao(self, request, queryset):
        for sol in queryset:
            sol.status = 'concluida'
            sol.save()
            # Atualiza status do animal para adotado
            sol.animal.status = 'adotado'
            sol.animal.save()
        self.message_user(request, "Processos concluídos e animais marcados como Adotados.")


@admin.register(Historia)
class HistoriaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'animal_relacionado', 'preview_foto', 'data_publicacao')
    list_filter = ('data_publicacao',)
    search_fields = ('titulo', 'descricao', 'animal_relacionado__nome')
    ordering = ('-data_publicacao',)

    def preview_foto(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" />',
                obj.imagem.url
            )
        return "Sem foto"
    preview_foto.short_description = "Foto"


# Customização dos cabeçalhos do Django Admin
admin.site.site_header = "Recomeço Animal — Gestão Administrativa"
admin.site.site_title = "Recomeço Animal Admin"
admin.site.index_title = "Painel de Controle e Gestão de Resgates"
