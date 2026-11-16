import os
import sys
from decimal import Decimal
import django
from urllib.request import urlretrieve, Request, urlopen
from PIL import Image, ImageDraw, ImageFont

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from usuarios.models import Perfil
from animais.models import Animal, ImagemAnimal, Solicitacao, Historia


def gerar_imagem_fallback(caminho, texto, cor_fundo, largura=800, altura=600):
    """Cria uma imagem de alta qualidade usando Pillow caso o download falhe."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    img = Image.new('RGB', (largura, altura), color=cor_fundo)
    draw = ImageDraw.Draw(img)
    
    # Desenha moldura e detalhes visuais
    draw.rectangle([20, 20, largura-20, altura-20], outline=(255, 255, 255), width=4)
    draw.rectangle([35, 35, largura-35, altura-35], outline=(255, 255, 255), width=2)
    
    # Adiciona texto no centro
    draw.text((largura // 2 - 150, altura // 2 - 20), texto, fill=(255, 255, 255))
    img.save(caminho, format='JPEG', quality=90)


def baixar_ou_gerar_imagem(url, caminho_relativo, texto_fallback, cor_fallback):
    """Tenta baixar imagem real da internet; caso não haja rede, gera via Pillow."""
    caminho_absoluto = os.path.join(django.conf.settings.MEDIA_ROOT, caminho_relativo)
    os.makedirs(os.path.dirname(caminho_absoluto), exist_ok=True)
    
    if os.path.exists(caminho_absoluto) and os.path.getsize(caminho_absoluto) > 30000:
        return caminho_relativo

    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urlopen(req, timeout=10) as response, open(caminho_absoluto, 'wb') as out_file:
            out_file.write(response.read())
        print(f"[OK] Imagem baixada: {caminho_relativo}")
    except Exception as e:
        print(f"[AVISO] Download falhou para {caminho_relativo} ({e}). Gerando imagem com Pillow...")
        gerar_imagem_fallback(caminho_absoluto, texto_fallback, cor_fallback)
        print(f"[OK] Imagem fallback gerada: {caminho_relativo}")

    return caminho_relativo


def main():
    print("Iniciando povoamento do banco de dados Recomeço Animal...")

    # 1. Superusuário Admin
    admin_user, created_admin = User.objects.get_or_create(username='admin', defaults={
        'email': 'admin@recomecoanimal.org.br',
        'first_name': 'Administrador',
        'last_name': 'Geral',
        'is_staff': True,
        'is_superuser': True
    })
    admin_user.set_password('admin123@password')
    admin_user.save()
    perfil_admin, _ = Perfil.objects.get_or_create(user=admin_user)
    perfil_admin.telefone = '(41) 99999-0000'
    perfil_admin.cidade = 'Curitiba'
    perfil_admin.estado = 'PR'
    perfil_admin.save()
    print("Superusuário 'admin' criado/atualizado com sucesso.")

    # 2. Usuário de Teste / Adotante
    demo_user, created_demo = User.objects.get_or_create(username='adotante', defaults={
        'email': 'adotante@email.com',
        'first_name': 'Carlos',
        'last_name': 'Eduardo Silva',
    })
    demo_user.set_password('adotante123@password')
    demo_user.save()
    perfil_demo, _ = Perfil.objects.get_or_create(user=demo_user)
    perfil_demo.telefone = '(41) 98888-1234'
    perfil_demo.endereco = 'Rua das Acácias, nº 150, Jardim Botânico'
    perfil_demo.cidade = 'Curitiba'
    perfil_demo.estado = 'PR'
    perfil_demo.save()
    print("Usuário comum 'adotante' criado/atualizado com sucesso.")

    # 3. Imagens dos 8 animais e histórias
    img_thor = baixar_ou_gerar_imagem(
        'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=800&q=80',
        'animais/thor.jpg',
        'Thor - Cão Resgatado',
        (128, 99, 79)
    )
    img_mel = baixar_ou_gerar_imagem(
        'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=800&q=80',
        'animais/mel.jpg',
        'Mel - Gatinha Resgatada',
        (79, 128, 97)
    )
    img_pipoca = baixar_ou_gerar_imagem(
        'https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?auto=format&fit=crop&w=800&q=80',
        'animais/pipoca.jpg',
        'Pipoca - Coelho',
        (180, 160, 140)
    )
    img_azulao = baixar_ou_gerar_imagem(
        'https://images.unsplash.com/photo-1552728089-57bdde30beb3?auto=format&fit=crop&w=800&q=80',
        'animais/azulao.jpg',
        'Azulão - Pássaro Legalizado',
        (36, 75, 58)
    )
    img_estrela = baixar_ou_gerar_imagem(
        'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=800&q=80',
        'animais/estrela.jpg',
        'Estrela - Égua Resgatada',
        (85, 60, 45)
    )
    img_campeao = baixar_ou_gerar_imagem(
        'https://images.unsplash.com/photo-1598974357801-cbca100e6571?auto=format&fit=crop&w=800&q=80',
        'animais/campeao.jpg',
        'Campeão - Cavalo Resgatado',
        (45, 65, 55)
    )
    img_luna = baixar_ou_gerar_imagem(
        'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=800&q=80',
        'animais/luna.jpg',
        'Luna - Necessidades Especiais',
        (110, 125, 115)
    )
    img_amora = baixar_ou_gerar_imagem(
        'https://images.unsplash.com/photo-1573865526739-10659fec78a5?auto=format&fit=crop&w=800&q=80',
        'animais/amora.jpg',
        'Amora - Gata em Recuperação',
        (75, 90, 80)
    )

    # Imagens extras de galeria
    img_extra_thor = baixar_ou_gerar_imagem(
        'https://images.unsplash.com/photo-1587300003388-59208cc962cb?auto=format&fit=crop&w=800&q=80',
        'animais/galeria/thor_extra.jpg',
        'Thor Brincando',
        (140, 110, 90)
    )
    img_extra_campeao = baixar_ou_gerar_imagem(
        'https://images.unsplash.com/photo-1566251037378-5e04e3bec343?auto=format&fit=crop&w=800&q=80',
        'animais/galeria/campeao_extra.jpg',
        'Campeão no Pasto',
        (60, 80, 70)
    )

    # 4. Cadastro dos 8 animais fictícios obrigatórios
    animais_dados = [
        {
            'nome': 'Thor',
            'especie': 'Cachorro',
            'raca': 'Vira-lata (SRD Caramelo)',
            'idade': '2 anos',
            'sexo': 'Macho',
            'porte': 'Medio',
            'descricao': 'Thor é um cachorro extremamente alegre, companheiro e brincalhão. Adora caminhadas no parque, aprende comandos com rapidez e se dá muito bem com crianças e outros animais.',
            'historico_resgate': 'Foi resgatado em uma avenida de grande movimento após ser abandonado em uma caixa de papelão sob chuva torrencial. Estava desidratado e com muito receio de humanos, mas recuperou totalmente a confiança através de muito carinho e adestramento positivo.',
            'condicoes_saude': 'Castrado, vermifugado, microchipado e vacinado com V10 e antirrábica.',
            'necessidades_especiais': 'Nenhuma. Saúde de ferro e excelente disposição para brincadeiras diárias.',
            'personalidade': 'Dócil, afetuoso, ativo e leal.',
            'imagem_principal': img_thor,
            'modalidade': 'adocao',
            'valor': Decimal('0.00'),
            'localizacao': 'Curitiba - PR',
            'status': 'disponivel',
        },
        {
            'nome': 'Mel',
            'especie': 'Gato',
            'raca': 'SRD Tricolor',
            'idade': '1 ano e 6 meses',
            'sexo': 'Femea',
            'porte': 'Pequeno',
            'descricao': 'Mel é uma gatinha calma, ronronenta e muito carinhosa. Gosta de tirar sonecas ao sol e de receber cafuné na cabeça. Ideal para viver em apartamento com telas de proteção.',
            'historico_resgate': 'Vítima de maus-tratos em um imóvel desocupado onde era mantida trancada sem água nem alimento. Resgatada após denúncia de vizinhos à delegacia ambiental, passou por reidratação e terapia de socialização.',
            'condicoes_saude': 'Testada negativa para FIV e FeLV, castrada, vacinada com tríplice felina e desparasitada.',
            'necessidades_especiais': 'Apenas alimentação úmida complementar para estímulo renal.',
            'personalidade': 'Calma, tímida no primeiro contato, mas muito apegada aos tutores.',
            'imagem_principal': img_mel,
            'modalidade': 'adocao',
            'valor': Decimal('0.00'),
            'localizacao': 'Curitiba - PR',
            'status': 'disponivel',
        },
        {
            'nome': 'Pipoca',
            'especie': 'Coelho',
            'raca': 'Mini Lion Head',
            'idade': '8 meses',
            'sexo': 'Macho',
            'porte': 'Pequeno',
            'descricao': 'Pipoca é um coelhinho esperto, curioso e que adora comer feno fresco e folhas verdes escuras. Já é acostumado a usar a caixa higiênica e vive solto em ambiente seguro.',
            'historico_resgate': 'Comprado por impulso em feira ilegal e descartado em um terreno baldio com ferimentos nas patas por confinamento em gaiola de arame inadequada. Foi tratado com pomadas cicatrizantes e nutrição balanceada.',
            'condicoes_saude': 'Dentes desgastados naturalmente com alimentação correta, desparasitado e sob rotina veterinária especializada em exóticos.',
            'necessidades_especiais': 'Necessita de piso antiderrapante e espaço livre de fiações elétricas para passear com segurança.',
            'personalidade': 'Curioso, tranquilo e curioso ao interagir com humanos gentis.',
            'imagem_principal': img_pipoca,
            'modalidade': 'adocao',
            'valor': Decimal('0.00'),
            'localizacao': 'São José dos Pinhais - PR',
            'status': 'disponivel',
        },
        {
            'nome': 'Azulão',
            'especie': 'Passaro',
            'raca': 'Canário-da-terra (Passeriforme)',
            'idade': '3 anos',
            'sexo': 'Macho',
            'porte': 'Pequeno',
            'descricao': 'Azulão é uma ave reabilitada de cativeiro ilegal que não possui condições anatômicas de reintrodução plena à natureza devido a atrofia muscular prévia nas asas. Canta alegremente ao amanhecer.',
            'historico_resgate': 'Apreendido pela Polícia Ambiental em cativeiro clandestino irregular em gaiola minúscula. Passou por processo de reabilitação motora e autorização de guarda doméstica assistida pelo órgão ambiental competente.',
            'condicoes_saude': 'Mudas de penas perfeitas, anilhado e registrado, alimentando-se de mix de sementes nobres e verduras.',
            'necessidades_especiais': 'Viveiro amplo horizontal com poleiros naturais e enriquecimento ambiental.',
            'personalidade': 'Ativo, comunicativo e melodioso.',
            'imagem_principal': img_azulao,
            'modalidade': 'adocao',
            'valor': Decimal('0.00'),
            'localizacao': 'Araucária - PR',
            'status': 'disponivel',
        },
        {
            'nome': 'Estrela',
            'especie': 'Cavalo',
            'raca': 'Mestiça Quarto de Milha',
            'idade': '6 anos',
            'sexo': 'Femea',
            'porte': 'Grande',
            'descricao': 'Estrela é uma égua forte, nobre e de olhar doce. Caminha com docilidade na guia e adora receber cenouras e carinhos na crina. Ideal para sítios familiares que buscam uma companheira para lazer respeitoso.',
            'historico_resgate': 'Vítima de tração animal forçada em área urbana com sobrecarga de entulhos de construção. Foi resgatada com escoriações no lombo, desidratação severa e desnutrição. Recebeu suplementação e repouso em piquete verde por 8 meses.',
            'condicoes_saude': 'Exames de Mormo e Anemia Infecciosa Equina (AIE) negativos, cascos tratados e balanceados por casqueador profissional, vacinação antirrábica e contra tétano em dia.',
            'necessidades_especiais': 'Não deve ser submetida a esforço físico de tração. Requer piquete telado com pasto limpo e cocheira ventilada.',
            'personalidade': 'Serena, paciente, mansa e dócil.',
            'imagem_principal': img_estrela,
            'modalidade': 'venda',
            'valor': Decimal('450.00'),
            'localizacao': 'Campo Largo - PR',
            'status': 'disponivel',
        },
        {
            'nome': 'Campeão',
            'especie': 'Cavalo',
            'raca': 'Mangalarga Marchador',
            'idade': '5 anos',
            'sexo': 'Macho',
            'porte': 'Grande',
            'descricao': 'Campeão é um cavalo de porte imponente e marcha macia. Muito inteligente e obediente, responde aos comandos de voz com leveza e serenidade.',
            'historico_resgate': 'Pertencia a um criador que faliu e o abandonou sem alimentação e assistência veterinária em uma fazenda embargada. Apresentava cólica crônica tratada a tempo pela nossa equipe.',
            'condicoes_saude': 'Exames sorológicos negativos para AIE e Mormo. Vermifugado e vacinado.',
            'necessidades_especiais': 'Alimentação rica em volumoso e piquete com água fresca corrente.',
            'personalidade': 'Atento, protetor e bastante dócil no manejo diário.',
            'imagem_principal': img_campeao,
            'modalidade': 'venda',
            'valor': Decimal('850.00'),
            'localizacao': 'Ponta Grossa - PR',
            'status': 'disponivel',
        },
        {
            'nome': 'Luna',
            'especie': 'Cachorro',
            'raca': 'Sem Raça Definida',
            'idade': '3 anos',
            'sexo': 'Femea',
            'porte': 'Medio',
            'descricao': 'Luna é a prova viva de que o amor supera qualquer barreira! Possui paraplegia nas patas traseiras decorrente de atropelamento antigo, mas corre feliz da vida utilizando sua cadeirinha de rodas adaptada.',
            'historico_resgate': 'Encontrada à beira da rodovia após ser atropelada e deixada sem socorro. Passou por cirurgia de descompressão e sessões de acupuntura e fisioterapia que devolveram sua autonomia e alegria.',
            'condicoes_saude': 'Castrada, vacinada e com acompanhamento neurológico estável.',
            'necessidades_especiais': 'Uso de cadeirinha de rodas para passeios ao ar livre e auxílio em esvaziamento vesical profilático.',
            'personalidade': 'Extremamente afetuosa, brincalhona e cheia de energia positiva.',
            'imagem_principal': img_luna,
            'modalidade': 'adocao',
            'valor': Decimal('0.00'),
            'localizacao': 'Curitiba - PR',
            'status': 'disponivel',
        },
        {
            'nome': 'Amora',
            'especie': 'Gato',
            'raca': 'Mestiça Siamês',
            'idade': '1 ano',
            'sexo': 'Femea',
            'porte': 'Pequeno',
            'descricao': 'Amora tem olhos azuis penetrantes e uma meiguice incomparável. Ama ficar no colo e dormir aninhada em mantas quentinhas.',
            'historico_resgate': 'Resgatada de uma colônia de gatos em área de descarte irregular de lixo onde sofria constantes ameaças e falta de alimento. Foi acolhida, desparasitada e aprendeu o que é viver em segurança.',
            'condicoes_saude': 'FIV/FeLV negativos, castrada, vermifugada e imunizada com vacina quádrupla felina.',
            'necessidades_especiais': 'Requer residência 100% telada (sem rotas de fuga).',
            'personalidade': 'Carinhosa, tranquila e muito companheira.',
            'imagem_principal': img_amora,
            'modalidade': 'adocao',
            'valor': Decimal('0.00'),
            'localizacao': 'Pinhais - PR',
            'status': 'disponivel',
        },
    ]

    for dados in animais_dados:
        animal_obj, criado = Animal.objects.update_or_create(
            nome=dados['nome'],
            defaults={
                'especie': dados['especie'],
                'raca': dados['raca'],
                'idade': dados['idade'],
                'sexo': dados['sexo'],
                'porte': dados['porte'],
                'descricao': dados['descricao'],
                'historico_resgate': dados['historico_resgate'],
                'condicoes_saude': dados['condicoes_saude'],
                'necessidades_especiais': dados['necessidades_especiais'],
                'personalidade': dados['personalidade'],
                'imagem_principal': dados['imagem_principal'],
                'modalidade': dados['modalidade'],
                'valor': dados['valor'],
                'localizacao': dados['localizacao'],
                'status': dados['status'],
                'responsavel': admin_user,
            }
        )
        print(f"Animal '{animal_obj.nome}' cadastrado/atualizado.")

    # 5. Adiciona fotos adicionais na galeria
    thor_obj = Animal.objects.filter(nome='Thor').first()
    if thor_obj:
        ImagemAnimal.objects.get_or_create(
            animal=thor_obj,
            imagem=img_extra_thor,
            defaults={'legenda': 'Thor brincando no gramado da ONG'}
        )

    campeao_obj = Animal.objects.filter(nome='Campeão').first()
    if campeao_obj:
        ImagemAnimal.objects.get_or_create(
            animal=campeao_obj,
            imagem=img_extra_campeao,
            defaults={'legenda': 'Campeão descansando no piquete'}
        )

    # 6. Histórias de Superação reais para a página inicial
    img_hist1 = baixar_ou_gerar_imagem(
        'https://images.unsplash.com/photo-1548767797-d8c844163c4c?auto=format&fit=crop&w=800&q=80',
        'historias/superacao_estrela.jpg',
        'Estrela e seu novo recomeço',
        (40, 70, 50)
    )
    img_hist2 = baixar_ou_gerar_imagem(
        'https://images.unsplash.com/photo-1548199973-03cce0bbc87b?auto=format&fit=crop&w=800&q=80',
        'historias/superacao_thor.jpg',
        'Thor em família',
        (120, 80, 60)
    )
    img_hist3 = baixar_ou_gerar_imagem(
        'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=800&q=80',
        'historias/superacao_mel.jpg',
        'Mel acolhida com amor',
        (60, 90, 80)
    )

    historias_dados = [
        {
            'titulo': 'Da Tração Urbana ao Piquete de Paz: O Renascimento de Estrela',
            'descricao': 'Após anos puxando carroça pesada e sofrendo com a desnutrição, a égua Estrela foi acolhida pela equipe da Recomeço Animal. Hoje recuperou peso, pelagem brilhante e desfruta da dignidade e carinho que sempre mereceu.',
            'imagem': img_hist1,
            'animal_relacionado': Animal.objects.filter(nome='Estrela').first(),
        },
        {
            'titulo': 'De Uma Caixa de Papelão Sob a Chuva a Cão Companheiro: O Recomeço de Thor',
            'descricao': 'Abandonado ainda filhote em uma rodovia movimentada, Thor encontrou nos veterinários da plataforma o tratamento e a socialização necessários para se tornar o amigo mais leal e alegre que uma família pode sonhar.',
            'imagem': img_hist2,
            'animal_relacionado': Animal.objects.filter(nome='Thor').first(),
        },
        {
            'titulo': 'Curando as Cicatrizes do Abandono: A Doçura da Gata Mel',
            'descricao': 'Resgatada de um cativeiro insalubre, Mel redescobriu a sensação de segurança. Com dedicação e muito afeto diário, ela hoje ronrona feliz para todos os que a visitam.',
            'imagem': img_hist3,
            'animal_relacionado': Animal.objects.filter(nome='Mel').first(),
        },
    ]

    for h_dado in historias_dados:
        Historia.objects.update_or_create(
            titulo=h_dado['titulo'],
            defaults={
                'descricao': h_dado['descricao'],
                'imagem': h_dado['imagem'],
                'animal_relacionado': h_dado['animal_relacionado'],
            }
        )
    print("Histórias de superação cadastradas.")

    # 7. Solicitações de Demonstração para testar o sistema de ponta a ponta
    if thor_obj and demo_user:
        Solicitacao.objects.get_or_create(
            usuario=demo_user,
            animal=thor_obj,
            defaults={
                'tipo_solicitacao': 'adocao',
                'justificativa': 'Moro em uma casa com quintal amplo e telado, trabalho em regime híbrido e quero proporcionar uma vida digna e cheia de carinho para o Thor.',
                'experiencia_animais': 'Já tive cães na infância e atualmente conto com suporte de uma clínica veterinária próxima de casa.',
                'condicoes_moradia': 'Casa própria térrea com muros de 2,5m e área gramada para passeios diários.',
                'status': 'em_analise',
                'observacoes_admin': 'Documentação inicial enviada pelo candidato. Entrevista agendada para sábado.',
            }
        )

    estrela_obj = Animal.objects.filter(nome='Estrela').first()
    if estrela_obj and demo_user:
        Solicitacao.objects.get_or_create(
            usuario=demo_user,
            animal=estrela_obj,
            defaults={
                'tipo_solicitacao': 'venda',
                'justificativa': 'Possuo uma chácara de lazer em Campo Largo com cocheira construída e outros equinos bem cuidados. Quero acolher a Estrela para descanso e passeio leve.',
                'experiencia_animais': 'Manejo cavalos há mais de 10 anos, com ferrageador quinzenal e veterinário equino responsável.',
                'condicoes_moradia': 'Piquete de 2 alqueires com pastagem mista de tífton e grama estrela, bebedouro automático e cerca de réguas.',
                'status': 'pendente',
                'observacoes_admin': '',
            }
        )

    print("Solicitações de demonstração criadas com sucesso.")
    print("=== BANCO DE DADOS POVOADO COM SUCESSO! ===")


if __name__ == '__main__':
    main()
