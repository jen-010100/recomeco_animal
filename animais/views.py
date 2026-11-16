from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from .models import Animal, Solicitacao, Historia
from .forms import SolicitacaoForm


class HomeView(TemplateView):
    """
    Página Inicial institucional com banner de impacto, animais em destaque,
    estatísticas reais do banco e histórias de superação.
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['animais_destaque'] = Animal.objects.filter(status='disponivel').order_by('-data_cadastro')[:6]
        context['cavalos_destaque'] = Animal.objects.filter(
            Q(especie='Cavalo') | Q(porte='Grande'),
            status='disponivel'
        ).order_by('-data_cadastro')[:3]
        context['historias'] = Historia.objects.all().order_by('-data_publicacao')[:3]
        context['total_resgatados'] = Animal.objects.count()
        context['total_adotados'] = Animal.objects.filter(status='adotado').count()
        context['total_disponiveis'] = Animal.objects.filter(status='disponivel').count()
        return context


class AnimalListView(ListView):
    """
    Catálogo dinâmico de animais com paginação, filtros múltiplos e barra de busca.
    """
    model = Animal
    template_name = 'animais.html'
    context_object_name = 'animais'
    paginate_by = 9

    def get_queryset(self):
        queryset = Animal.objects.all().order_by('-data_cadastro')
        params = self.request.GET

        # Busca por texto livre (nome, raça, espécie, histórico, descrição)
        q = params.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) |
                Q(raca__icontains=q) |
                Q(especie__icontains=q) |
                Q(descricao__icontains=q) |
                Q(historico_resgate__icontains=q)
            )

        # Filtro de espécie
        especie = params.get('especie', '').strip()
        if especie:
            queryset = queryset.filter(especie__iexact=especie)

        # Filtro de porte
        porte = params.get('porte', '').strip()
        if porte:
            queryset = queryset.filter(porte__iexact=porte)

        # Filtro de sexo
        sexo = params.get('sexo', '').strip()
        if sexo:
            queryset = queryset.filter(sexo__iexact=sexo)

        # Filtro de modalidade (Adoção Gratuita vs Venda Responsável)
        modalidade = params.get('modalidade', '').strip()
        if modalidade:
            queryset = queryset.filter(modalidade__iexact=modalidade)

        # Filtro de status (disponivel, reservado, adotado)
        status = params.get('status', '').strip()
        if status:
            queryset = queryset.filter(status__iexact=status)

        # Filtro de localização
        localizacao = params.get('localizacao', '').strip()
        if localizacao:
            queryset = queryset.filter(localizacao__icontains=localizacao)

        # Filtro rápido para equinos / grande porte
        grande_porte = params.get('grande_porte', '').strip()
        if grande_porte == '1':
            queryset = queryset.filter(Q(especie='Cavalo') | Q(porte='Grande'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mantém os parâmetros de busca para paginação limpa no template
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['query_string'] = query_params.urlencode()
        context['filtro_atual'] = self.request.GET
        context['especies_disponiveis'] = Animal.ESPECIE_CHOICES
        context['portes_disponiveis'] = Animal.PORTE_CHOICES
        context['sexos_disponiveis'] = Animal.SEXO_CHOICES
        context['modalidades_disponiveis'] = Animal.MODALIDADE_CHOICES
        context['status_disponiveis'] = Animal.STATUS_CHOICES
        return context


class AnimalDetailView(DetailView):
    """
    Página detalhada do animal com galeria de fotografias, histórico de resgate,
    informações clínicas e botão de solicitação condicional.
    """
    model = Animal
    template_name = 'detalhe_animal.html'
    context_object_name = 'animal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        animal = self.get_object()
        context['imagens_extras'] = animal.imagens_adicionais.all()
        context['outros_animais'] = Animal.objects.filter(
            status='disponivel'
        ).exclude(pk=animal.pk).order_by('?')[:3]

        # Verifica se o usuário atual já possui uma solicitação ativa
        if self.request.user.is_authenticated:
            context['solicitacao_existente'] = Solicitacao.objects.filter(
                usuario=self.request.user,
                animal=animal,
                status__in=['pendente', 'em_analise']
            ).first()
        else:
            context['solicitacao_existente'] = None

        return context


class SolicitacaoCreateView(LoginRequiredMixin, CreateView):
    """
    View para envio da solicitação de Adoção ou Demonstração de Interesse em Aquisição.
    Acesso restrito apenas para usuários autenticados.
    """
    model = Solicitacao
    form_class = SolicitacaoForm
    template_name = 'solicitar_adocao.html'
    login_url = reverse_lazy('usuarios:login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(
                request,
                "Para solicitar a adoção ou demonstrar interesse na aquisição responsável, faça login ou cadastre-se na plataforma."
            )
            return redirect(f"{reverse('usuarios:login')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)

    def get_animal(self):
        return get_object_or_404(Animal, pk=self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        kwargs['animal'] = self.get_animal()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        animal = self.get_animal()
        context['animal'] = animal
        # Alerta caso já tenha solicitação
        context['ja_solicitado'] = Solicitacao.objects.filter(
            usuario=self.request.user,
            animal=animal,
            status__in=['pendente', 'em_analise']
        ).exists()
        return context

    def form_valid(self, form):
        animal = self.get_animal()
        if not animal.is_disponivel:
            messages.error(
                self.request,
                f"O animal {animal.nome} não está disponível para novas solicitações no momento."
            )
            return redirect('animais:detalhe_animal', pk=animal.pk)

        # Salva o formulário
        self.object = form.save()
        tipo_str = "Adoção" if animal.modalidade == 'adocao' else "Interesse em Aquisição Responsável"
        messages.success(
            self.request,
            f"Sua solicitação de {tipo_str} para '{animal.nome}' foi enviada com sucesso! Nossa equipe entrará em contato para os próximos passos."
        )
        return redirect('usuarios:minha_conta')


class SolicitacaoDeleteView(LoginRequiredMixin, DeleteView):
    """
    Permite ao interessado cancelar sua solicitação enquanto ela estiver no status 'pendente'.
    Garante que usuários só manipulem suas próprias solicitações.
    """
    model = Solicitacao
    success_url = reverse_lazy('usuarios:minha_conta')
    login_url = reverse_lazy('usuarios:login')

    def get_queryset(self):
        # Usuário só enxerga as próprias solicitações
        return Solicitacao.objects.filter(usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        solicitacao = self.get_object()
        if solicitacao.status not in ['pendente']:
            messages.error(request, "Esta solicitação já está em análise e não pode ser cancelada diretamente.")
            return redirect('usuarios:minha_conta')

        animal_nome = solicitacao.animal.nome
        response = super().delete(request, *args, **kwargs)
        messages.info(request, f"A solicitação para o animal '{animal_nome}' foi cancelada.")
        return response


class SobreNosView(TemplateView):
    """Página institucional Sobre Nós."""
    template_name = 'sobre.html'


class ComoAjudarView(TemplateView):
    """Página institucional Como Ajudar."""
    template_name = 'como_ajudar.html'
