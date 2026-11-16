from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from usuarios.models import Perfil


class UsuariosAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'lucas_silva',
            'email': 'lucas@exemplo.com',
            'nome_completo': 'Lucas Silva Santos',
            'telefone': '(41) 97777-6666',
            'password': 'senha_segura_123',
            'password_confirm': 'senha_segura_123',
        }

    def test_cadastro_usuario_sucesso(self):
        """Usuário deve conseguir se cadastrar com validação de dados e perfil associado."""
        url = reverse('usuarios:cadastro')
        response = self.client.post(url, data=self.user_data)
        self.assertEqual(response.status_code, 302)
        
        # Verifica se o usuário foi criado no banco
        user = User.objects.filter(username='lucas_silva').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'lucas@exemplo.com')
        self.assertEqual(user.first_name, 'Lucas')
        self.assertEqual(user.last_name, 'Silva Santos')

        # Verifica se o perfil foi criado e recebeu o telefone
        self.assertTrue(hasattr(user, 'perfil'))
        self.assertEqual(user.perfil.telefone, '(41) 97777-6666')

    def test_cadastro_senhas_diferentes(self):
        """Cadastro com senhas divergentes deve falhar com erro amigável."""
        dados = self.user_data.copy()
        dados['password_confirm'] = 'senha_diferente_999'
        url = reverse('usuarios:cadastro')
        response = self.client.post(url, data=dados)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'As senhas não conferem')

    def test_login_com_username_e_logout(self):
        """Usuário consegue logar com username e posteriormente deslogar."""
        user = User.objects.create_user(
            username='marcos_teste',
            email='marcos@email.com',
            password='minha_senha_123'
        )
        url_login = reverse('usuarios:login')
        response = self.client.post(url_login, data={
            'username_or_email': 'marcos_teste',
            'password': 'minha_senha_123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('usuarios:minha_conta'))

        # Logout
        url_logout = reverse('usuarios:logout')
        response_logout = self.client.get(url_logout)
        self.assertEqual(response_logout.status_code, 302)
        self.assertRedirects(response_logout, reverse('home'))

    def test_login_com_email(self):
        """Usuário consegue logar utilizando seu endereço de e-mail."""
        User.objects.create_user(
            username='renata_teste',
            email='renata@email.com',
            password='minha_senha_123'
        )
        url_login = reverse('usuarios:login')
        response = self.client.post(url_login, data={
            'username_or_email': 'renata@email.com',
            'password': 'minha_senha_123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('usuarios:minha_conta'))

    def test_restricao_acesso_minha_conta(self):
        """Visitante anônimo não pode acessar 'Minha Conta' sem login."""
        url = reverse('usuarios:minha_conta')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('usuarios:login'), response.url)
