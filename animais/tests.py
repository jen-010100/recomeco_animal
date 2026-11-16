from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Animal, Solicitacao, Historia


class AnimalModelAndViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='joao_teste',
            email='joao@teste.com',
            password='senha_segura_123',
            first_name='João',
            last_name='Silva'
        )
        self.outro_user = User.objects.create_user(
            username='maria_teste',
            email='maria@teste.com',
            password='senha_segura_123'
        )
        self.animal_adocao = Animal.objects.create(
            nome='Bob',
            especie='Cachorro',
            raca='SRD',
            idade='1 ano',
            sexo='Macho',
            porte='Medio',
            descricao='Cãozinho amoroso',
            historico_resgate='Encontrado perdido em praça',
            condicoes_saude='Vacinado e castrado',
            modalidade='adocao',
            valor=Decimal('0.00'),
            localizacao='Curitiba - PR',
            status='disponivel'
        )
        self.animal_venda = Animal.objects.create(
            nome='Relâmpago',
            especie='Cavalo',
            raca='Quarto de Milha',
            idade='4 anos',
            sexo='Macho',
            porte='Grande',
            descricao='Cavalo manso para lazer',
            historico_resgate='Resgatado de sobrecarga',
            condicoes_saude='Exames negativos para AIE e Mormo',
            modalidade='venda',
            valor=Decimal('500.00'),
            localizacao='Campo Largo - PR',
            status='disponivel'
        )

    def test_pagina_inicial_publica(self):
        """Página inicial deve ser acessível publicamente e retornar status 200."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Uma nova chance começa com você.')
        self.assertContains(response, 'Bob')

    def test_catalogo_animais_e_filtros(self):
        """Catálogo deve permitir filtrar por espécie, modalidade e termo de busca."""
        response = self.client.get(reverse('animais:catalogo'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bob')
        self.assertContains(response, 'Relâmpago')

        # Filtro de espécie Cavalo
        response_cavalo = self.client.get(reverse('animais:catalogo'), {'especie': 'Cavalo'})
        self.assertContains(response_cavalo, 'Relâmpago')
        self.assertNotContains(response_cavalo, 'Bob')

        # Busca por palavra-chave
        response_busca = self.client.get(reverse('animais:catalogo'), {'q': 'Bob'})
        self.assertContains(response_busca, 'Bob')
        self.assertNotContains(response_busca, 'Relâmpago')

    def test_detalhes_animal_publico(self):
        """Página de detalhes deve exibir informações completas do animal."""
        response = self.client.get(reverse('animais:detalhe_animal', kwargs={'pk': self.animal_adocao.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bob')
        self.assertContains(response, 'Encontrado perdido em praça')

    def test_restricao_acesso_solicitar_adocao(self):
        """Usuário NÃO autenticado deve ser redirecionado para a página de login ao tentar solicitar adoção."""
        url = reverse('animais:solicitar_adocao', kwargs={'pk': self.animal_adocao.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('usuarios:login'), response.url)

    def test_solicitacao_adocao_sucesso_usuario_autenticado(self):
        """Usuário autenticado deve conseguir enviar solicitação de adoção com sucesso."""
        self.client.login(username='joao_teste', password='senha_segura_123')
        url = reverse('animais:solicitar_adocao', kwargs={'pk': self.animal_adocao.pk})
        
        dados = {
            'justificativa': 'Tenho muito amor e espaço para cuidar do Bob com carinho.',
            'experiencia_animais': 'Já criei cães por 5 anos.',
            'condicoes_moradia': 'Casa murada e quintal amplo.',
            'termo_responsabilidade': True,
        }
        response = self.client.post(url, data=dados)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('usuarios:minha_conta'))

        # Verifica se a solicitação foi salva no banco
        solicitacao = Solicitacao.objects.filter(usuario=self.user, animal=self.animal_adocao).first()
        self.assertIsNotNone(solicitacao)
        self.assertEqual(solicitacao.tipo_solicitacao, 'adocao')
        self.assertEqual(solicitacao.status, 'pendente')

    def test_bloqueio_solicitacao_duplicada(self):
        """Impede que o mesmo usuário envie solicitação duplicada para o mesmo animal enquanto ativa."""
        self.client.login(username='joao_teste', password='senha_segura_123')
        url = reverse('animais:solicitar_adocao', kwargs={'pk': self.animal_adocao.pk})
        
        # Cria a primeira solicitação
        Solicitacao.objects.create(
            usuario=self.user,
            animal=self.animal_adocao,
            tipo_solicitacao='adocao',
            justificativa='Primeira solicitação',
            status='pendente'
        )

        dados = {
            'justificativa': 'Tentando enviar de novo',
            'experiencia_animais': 'Muitos anos',
            'condicoes_moradia': 'Casa boa',
            'termo_responsabilidade': True,
        }
        response = self.client.post(url, data=dados)
        self.assertEqual(response.status_code, 200) # Volta com erro no form
        self.assertContains(response, 'Você já enviou uma solicitação em análise')

    def test_cancelamento_solicitacao_pelo_proprio_usuario(self):
        """Usuário pode cancelar sua própria solicitação enquanto pendente."""
        self.client.login(username='joao_teste', password='senha_segura_123')
        solicitacao = Solicitacao.objects.create(
            usuario=self.user,
            animal=self.animal_adocao,
            tipo_solicitacao='adocao',
            justificativa='Gostaria de adotar',
            status='pendente'
        )
        url_cancelar = reverse('animais:cancelar_solicitacao', kwargs={'pk': solicitacao.pk})
        response = self.client.post(url_cancelar)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Solicitacao.objects.filter(pk=solicitacao.pk).exists())
