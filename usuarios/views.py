from django.shortcuts import render, redirect
from django.views.generic import CreateView, FormView, View, UpdateView
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse

from .models import Perfil
from .forms import CadastroForm, LoginForm, PerfilUpdateForm


class CadastroView(CreateView):
    """
    View de registro de novo usuário com validações de dados e criação de perfil.
    """
    form_class = CadastroForm
    template_name = 'cadastro.html'
    success_url = reverse_lazy('usuarios:minha_conta')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('usuarios:minha_conta')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        # Faz o login automático do usuário recém-cadastrado
        login(self.request, user)
        messages.success(
            self.request,
            f"Seja muito bem-vindo(a), {user.first_name or user.username}! Sua conta no Recomeço Animal foi criada com sucesso."
        )
        return redirect(self.success_url)


class LoginUsuarioView(FormView):
    """
    View de autenticação que aceita tanto Nome de Usuário quanto E-mail.
    """
    form_class = LoginForm
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('usuarios:minha_conta')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f"Olá, {user.first_name or user.username}! Login realizado com sucesso.")

        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('usuarios:minha_conta')


class LogoutUsuarioView(View):
    """
    View para encerramento de sessão com mensagem de confirmação.
    """
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Você saiu da sua conta. Volte sempre ao Recomeço Animal!")
        return redirect('home')

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Você saiu da sua conta. Volte sempre ao Recomeço Animal!")
        return redirect('home')


class MinhaContaView(LoginRequiredMixin, UpdateView):
    """
    Painel do usuário com informações cadastrais, edição de perfil e
    acompanhamento detalhado das solicitações de adoção e interesses.
    """
    model = Perfil
    form_class = PerfilUpdateForm
    template_name = 'minha_conta.html'
    success_url = reverse_lazy('usuarios:minha_conta')
    login_url = reverse_lazy('usuarios:login')

    def get_object(self, queryset=None):
        perfil, _ = Perfil.objects.get_or_create(user=self.request.user)
        return perfil

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Busca todas as solicitações feitas pelo usuário com informações dos animais
        solicitacoes = self.request.user.solicitacoes.select_related('animal').order_by('-data_solicitacao')
        context['solicitacoes'] = solicitacoes
        context['total_solicitacoes'] = solicitacoes.count()
        context['solicitacoes_pendentes'] = solicitacoes.filter(status__in=['pendente', 'em_analise']).count()
        context['solicitacoes_aprovadas'] = solicitacoes.filter(status__in=['aprovada', 'concluida']).count()
        return context

    def form_valid(self, form):
        messages.success(self.request, "Seus dados de perfil foram atualizados com sucesso!")
        return super().form_valid(form)
