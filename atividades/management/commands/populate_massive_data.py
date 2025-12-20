from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from atividades.models import Curso, Categoria, CategoriaCurso, Aluno, Semestre, Atividade
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Popula o sistema com dados massivos: 50 alunos por curso/semestre e 50 atividades por aluno.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando população massiva de dados...'))
        
        # Buscar todos os cursos e semestres
        cursos = list(Curso.objects.all())
        semestres = list(Semestre.objects.all())
        
        if not cursos:
            self.stdout.write(self.style.ERROR('Nenhum curso encontrado. Execute populate_initial_data primeiro.'))
            return
        
        if not semestres:
            self.stdout.write(self.style.ERROR('Nenhum semestre encontrado. Execute populate_initial_data primeiro.'))
            return
        
        # Nomes fictícios para alunos
        primeiros_nomes = [
            'João', 'Maria', 'Pedro', 'Ana', 'Lucas', 'Juliana', 'Carlos', 'Fernanda',
            'Rafael', 'Beatriz', 'Bruno', 'Camila', 'Gabriel', 'Larissa', 'Felipe',
            'Mariana', 'Diego', 'Amanda', 'Thiago', 'Letícia', 'André', 'Bianca',
            'Rodrigo', 'Carolina', 'Leonardo', 'Isabela', 'Gustavo', 'Natália', 'Matheus',
            'Bruna', 'Ricardo', 'Patrícia', 'Vinícius', 'Aline', 'Marcelo', 'Jéssica',
            'Daniel', 'Vanessa', 'Paulo', 'Cristina', 'Fernando', 'Renata', 'Alexandre',
            'Priscila', 'Fábio', 'Adriana', 'Henrique', 'Simone', 'Maurício', 'Tatiana'
        ]
        
        sobrenomes = [
            'Silva', 'Santos', 'Oliveira', 'Souza', 'Lima', 'Pereira', 'Costa', 'Ferreira',
            'Rodrigues', 'Almeida', 'Nascimento', 'Carvalho', 'Araújo', 'Ribeiro', 'Martins',
            'Rocha', 'Alves', 'Monteiro', 'Mendes', 'Barbosa', 'Cardoso', 'Castro', 'Dias',
            'Gomes', 'Pinto', 'Ramos', 'Fernandes', 'Freitas', 'Moura', 'Cavalcanti'
        ]
        
        # Nomes de atividades fictícias
        atividades_nomes = [
            'Workshop de Tecnologia',
            'Palestra sobre Inovação',
            'Curso de Python Avançado',
            'Seminário de Engenharia',
            'Minicurso de Design Thinking',
            'Congresso Nacional',
            'Evento Acadêmico Internacional',
            'Oficina de Desenvolvimento Web',
            'Curso de Inglês Técnico',
            'Participação em Mesa Redonda',
            'Monitoria de Programação',
            'Iniciação Científica',
            'Publicação de Artigo',
            'Apresentação de TCC',
            'Curso de Gestão de Projetos',
            'Workshop de UX/UI',
            'Palestra sobre Inteligência Artificial',
            'Curso de Análise de Dados',
            'Seminário de Sustentabilidade',
            'Minicurso de Robótica',
            'Congresso Regional',
            'Evento de Empreendedorismo',
            'Oficina de Marketing Digital',
            'Curso de Espanhol',
            'Participação em Defesa de Mestrado',
            'Extensão Universitária',
            'Pesquisa de Campo',
            'Produção de Conteúdo Digital',
            'Curso de Fotografia',
            'Workshop de Comunicação',
            'Palestra sobre Liderança',
            'Curso de Excel Avançado',
            'Seminário de Direitos Humanos',
            'Minicurso de Blockchain',
            'Congresso Internacional',
            'Evento de Networking',
            'Oficina de Redação Científica',
            'Curso de Alemão Básico',
            'Participação em Banca de TCC',
            'Projeto de Extensão',
            'Estudo de Caso',
            'Produção Audiovisual',
            'Curso de Edição de Vídeo',
            'Workshop de Produtividade',
            'Palestra sobre Carreira',
            'Curso de Power BI',
            'Seminário de Ética',
            'Minicurso de Cloud Computing',
            'Congresso de Ciências',
            'Evento Cultural'
        ]
        
        descricoes = [
            'Participação como ouvinte no evento',
            'Atividade realizada com aproveitamento',
            'Curso completo com certificado',
            'Participação ativa durante todo o evento',
            'Aprendizado significativo na área',
            'Experiência enriquecedora',
            'Desenvolvimento de competências técnicas',
            'Networking e troca de experiências',
            'Atualização profissional',
            'Aprofundamento teórico e prático'
        ]
        
        total_alunos = 0
        total_atividades = 0
        
        # Para cada curso
        for curso in cursos:
            self.stdout.write(f'\nProcessando curso: {curso.nome}')
            
            # Buscar todas as categorias associadas a este curso
            categorias_curso = list(CategoriaCurso.objects.filter(curso=curso))
            
            if not categorias_curso:
                self.stdout.write(self.style.WARNING(f'  Nenhuma categoria encontrada para {curso.nome}. Pulando...'))
                continue
            
            # Para cada semestre
            for semestre in semestres:
                self.stdout.write(f'  Semestre: {semestre.nome}')
                
                # Filtrar categorias deste semestre
                categorias_semestre = [cc for cc in categorias_curso if cc.semestre == semestre]
                
                if not categorias_semestre:
                    self.stdout.write(self.style.WARNING(f'    Nenhuma categoria para este semestre. Pulando...'))
                    continue
                
                # Criar 50 alunos
                for i in range(50):
                    # Gerar nome único
                    primeiro_nome = random.choice(primeiros_nomes)
                    sobrenome = random.choice(sobrenomes)
                    username = f'{primeiro_nome.lower()}_{sobrenome.lower()}_{curso.nome.replace(" ", "")[:3].lower()}_{semestre.nome.replace(".", "")}_{i+1}'
                    
                    # Criar usuário
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': f'{username}@example.com',
                            'first_name': primeiro_nome,
                            'last_name': sobrenome
                        }
                    )
                    
                    if created:
                        user.set_password('senha123')
                        user.save()
                    
                    # Criar aluno
                    aluno, created_aluno = Aluno.objects.get_or_create(
                        user=user,
                        defaults={
                            'curso': curso,
                            'semestre_ingresso': semestre
                        }
                    )
                    
                    if created_aluno:
                        total_alunos += 1
                    
                    # Criar 50 atividades para este aluno
                    for j in range(50):
                        categoria = random.choice(categorias_semestre)
                        
                        # Definir datas dentro do período do semestre
                        if semestre.data_inicio and semestre.data_fim:
                            data_inicio = datetime.strptime(str(semestre.data_inicio), '%Y-%m-%d')
                            data_fim = datetime.strptime(str(semestre.data_fim), '%Y-%m-%d')
                            dias_diferenca = (data_fim - data_inicio).days
                            data_atividade = data_inicio + timedelta(days=random.randint(0, dias_diferenca))
                        else:
                            data_atividade = datetime.now()
                        
                        # Horas entre 2 e 40
                        horas = random.randint(2, 40)
                        
                        # 70% das atividades já aprovadas
                        if random.random() < 0.7:
                            # Aprovadas com 80-100% das horas ou rejeitadas
                            if random.random() < 0.9:  # 90% aprovadas
                                horas_aprovadas = random.randint(int(horas * 0.8), horas)
                            else:  # 10% rejeitadas
                                horas_aprovadas = 0
                        else:
                            horas_aprovadas = None  # 30% aguardando aprovação
                        
                        nome_atividade = random.choice(atividades_nomes)
                        descricao = random.choice(descricoes)
                        
                        # Criar atividade (pulando validação para agilizar)
                        atividade = Atividade(
                            aluno=aluno,
                            categoria=categoria,
                            nome=nome_atividade,
                            descricao=descricao,
                            horas=horas,
                            horas_aprovadas=horas_aprovadas,
                            data=data_atividade.date(),
                            documento=None  # Sem documento
                        )
                        
                        # Salvar sem chamar clean() para ser mais rápido
                        atividade.save_base(raw=True)
                        total_atividades += 1
                    
                    # Feedback a cada 10 alunos
                    if (i + 1) % 10 == 0:
                        self.stdout.write(f'    Criados {i + 1}/50 alunos...')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ População massiva concluída!'))
        self.stdout.write(self.style.SUCCESS(f'  Total de alunos criados: {total_alunos}'))
        self.stdout.write(self.style.SUCCESS(f'  Total de atividades criadas: {total_atividades}'))
