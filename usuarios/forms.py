from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import Perfil


class CadastroForm(forms.ModelForm):
    nome_completo = forms.CharField(
        max_length=150,
        required=True,
        label="Nome Completo",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Maria Oliveira Silva'
        })
    )
    telefone = forms.CharField(
        max_length=20,
        required=True,
        label="Telefone / WhatsApp",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(00) 00000-0000'
        })
    )
    email = forms.EmailField(
        required=True,
        label="E-mail",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seuemail@exemplo.com'
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Crie uma senha segura (mínimo 6 caracteres)'
        })
    )
    password_confirm = forms.CharField(
        label="Confirmação de Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repita a senha'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Escolha um nome de usuário único'
            })
        }
        labels = {
            'username': 'Nome de Usuário'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este e-mail já está cadastrado em outra conta.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Este nome de usuário já está em uso. Por favor, escolha outro.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "As senhas não conferem. Digite-as novamente.")

        if password and len(password) < 6:
            self.add_error('password', "A senha deve ter no mínimo 6 caracteres.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        # Divide o nome completo em first_name e last_name
        partes_nome = self.cleaned_data['nome_completo'].strip().split(' ', 1)
        user.first_name = partes_nome[0]
        user.last_name = partes_nome[1] if len(partes_nome) > 1 else ''

        if commit:
            user.save()
            # Atualiza o perfil criado automaticamente pelo signal
            perfil, _ = Perfil.objects.get_or_create(user=user)
            perfil.telefone = self.cleaned_data['telefone']
            perfil.save()

        return user


class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label="Usuário ou E-mail",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu usuário ou e-mail cadastrado',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sua senha de acesso'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        if identifier and password:
            # Tenta autenticar pelo username direto
            user = authenticate(username=identifier, password=password)

            # Se não encontrou, tenta autenticar buscando o username pelo email
            if user is None:
                try:
                    user_obj = User.objects.get(email__iexact=identifier)
                    user = authenticate(username=user_obj.username, password=password)
                except (User.DoesNotExist, User.MultipleObjectsReturned):
                    user = None

            if user is None:
                raise ValidationError("Usuário/e-mail ou senha incorretos. Por favor, verifique seus dados.")
            elif not user.is_active:
                raise ValidationError("Esta conta de usuário está desativada.")

            self.user_cache = user

        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)


class PerfilUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Primeiro Nome",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Sobrenome",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        label="E-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Perfil
        fields = ['telefone', 'endereco', 'cidade', 'estado', 'data_nascimento']
        widgets = {
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua, número, complemento'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sua cidade'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UF (ex: SP, PR)'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise ValidationError("Este e-mail já está sendo utilizado por outro usuário.")
        return email

    def save(self, commit=True):
        perfil = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            perfil.save()
        return perfil

