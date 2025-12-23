from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from atividades.models import Curso, Categoria, CategoriaCurso, Aluno, Coordenador, CursoPorSemestre, Semestre
import random
import time

class Command(BaseCommand):
    help = 'Popula o sistema com dados iniciais: usuários, cursos, categorias e associações.'

    def handle(self, *args, **options):
        tempo_inicio = time.time()
        
        self.stdout.write(self.style.WARNING('='*60))
        self.stdout.write(self.style.WARNING('POPULAÇÃO DE DADOS INICIAIS'))
        self.stdout.write(self.style.WARNING('='*60))
        
        # Grupos
        self.stdout.write('\n[1/7] Criando grupos...')
        inicio = time.time()
        grupos = {
            'Coordenador': Group.objects.get_or_create(name='Coordenador')[0],
            'Gestor': Group.objects.get_or_create(name='Gestor')[0],
        }
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(grupos)} grupos criados em {time.time()-inicio:.2f}s'))

        # Semestres
        self.stdout.write('\n[2/7] Criando semestres...')
        inicio = time.time()
        semestres_info = [
            {'nome': '2020.1', 'data_inicio': '2020-02-01', 'data_fim': '2020-07-31'},
            {'nome': '2020.2', 'data_inicio': '2020-08-01', 'data_fim': '2020-12-20'},
            {'nome': '2021.1', 'data_inicio': '2021-02-01', 'data_fim': '2021-07-31'},
            {'nome': '2021.2', 'data_inicio': '2021-08-01', 'data_fim': '2021-12-20'},
            {'nome': '2022.1', 'data_inicio': '2022-02-01', 'data_fim': '2022-07-31'},
            {'nome': '2022.2', 'data_inicio': '2022-08-01', 'data_fim': '2022-12-20'},
            {'nome': '2023.1', 'data_inicio': '2023-02-01', 'data_fim': '2023-07-31'},
            {'nome': '2023.2', 'data_inicio': '2023-08-01', 'data_fim': '2023-12-20'},
            {'nome': '2024.1', 'data_inicio': '2024-02-01', 'data_fim': '2024-07-31'},
            {'nome': '2024.2', 'data_inicio': '2024-08-01', 'data_fim': '2024-12-20'},
            {'nome': '2025.1', 'data_inicio': '2025-02-01', 'data_fim': '2025-07-31'},
            {'nome': '2025.2', 'data_inicio': '2025-08-01', 'data_fim': '2025-12-20'},
        ]
        
        # Criar semestres que não existem
        semestres_existentes = set(Semestre.objects.values_list('nome', flat=True))
        semestres_para_criar = []
        for info in semestres_info:
            if info['nome'] not in semestres_existentes:
                semestres_para_criar.append(Semestre(
                    nome=info['nome'],
                    data_inicio=info['data_inicio'],
                    data_fim=info['data_fim']
                ))
        
        if semestres_para_criar:
            Semestre.objects.bulk_create(semestres_para_criar)
            self.stdout.write(self.style.SUCCESS(f'  ✓ {len(semestres_para_criar)} semestres criados'))
        else:
            self.stdout.write(f'  → Todos os semestres já existem')
        
        semestres = list(Semestre.objects.all())
        self.stdout.write(self.style.SUCCESS(f'  ✓ Total de {len(semestres)} semestres em {time.time()-inicio:.2f}s'))

        # Cursos
        self.stdout.write('\n[3/7] Criando cursos...')
        inicio = time.time()
        cursos_info = [
            {'nome': 'Sistemas de Informação', 'horas_requeridas': 600},
            {'nome': 'Design Gráfico', 'horas_requeridas': 400},
            {'nome': 'Engenharia da Computação', 'horas_requeridas': 500},
            {'nome': 'Arquitetura e Urbanismo', 'horas_requeridas': 450},
            {'nome': 'Engenharia Ambiental', 'horas_requeridas': 250},
            {'nome': 'Engenharia Elétrica', 'horas_requeridas': 350},
            {'nome': 'Engenharia Mecânica', 'horas_requeridas': 400},
            {'nome': 'Administração', 'horas_requeridas': 200},    
            {'nome': 'Ciência da Computação', 'horas_requeridas': 550},
            {'nome': 'Publicidade e Propaganda', 'horas_requeridas': 300},
            {'nome': 'Jornalismo', 'horas_requeridas': 250},
            {'nome': 'Relações Públicas', 'horas_requeridas': 200},
            {'nome': 'Marketing', 'horas_requeridas': 150},
            {'nome': 'Recursos Humanos', 'horas_requeridas': 400},
            {'nome': 'Finanças', 'horas_requeridas': 350},
            {'nome': 'Contabilidade', 'horas_requeridas': 300},
            {'nome': 'Logística', 'horas_requeridas': 250},
            {'nome': 'Turismo', 'horas_requeridas': 200},
            {'nome': 'Gastronomia', 'horas_requeridas': 150},
            {'nome': 'Hotelaria', 'horas_requeridas': 100},
            {'nome': 'Direito', 'horas_requeridas': 600},
            {'nome': 'Medicina', 'horas_requeridas': 800},
            {'nome': 'Enfermagem', 'horas_requeridas': 500},
            {'nome': 'Fisioterapia', 'horas_requeridas': 400},
            {'nome': 'Nutrição', 'horas_requeridas': 300},
            {'nome': 'Odontologia', 'horas_requeridas': 450},
            {'nome': 'Farmácia', 'horas_requeridas': 350},
            {'nome': 'Psicologia', 'horas_requeridas': 400},
            {'nome': 'Educação Física', 'horas_requeridas': 250},
            {'nome': 'Pedagogia', 'horas_requeridas': 200},
            {'nome': 'História', 'horas_requeridas': 150},
            {'nome': 'Geografia', 'horas_requeridas': 100},
            {'nome': 'Letras', 'horas_requeridas': 300},
            {'nome': 'Filosofia', 'horas_requeridas': 200},
            {'nome': 'Sociologia', 'horas_requeridas': 150},
            {'nome': 'Antropologia', 'horas_requeridas': 100},
            {'nome': 'Biologia', 'horas_requeridas': 400},
            {'nome': 'Química', 'horas_requeridas': 350},
            {'nome': 'Física', 'horas_requeridas': 300},
        ]
        
        # Criar cursos que não existem
        cursos_existentes = set(Curso.objects.values_list('nome', flat=True))
        cursos_para_criar = []
        for info in cursos_info:
            if info['nome'] not in cursos_existentes:
                cursos_para_criar.append(Curso(
                    nome=info['nome'],
                    horas_requeridas=info['horas_requeridas']
                ))

        
        if cursos_para_criar:
            Curso.objects.bulk_create(cursos_para_criar)
            self.stdout.write(self.style.SUCCESS(f'  ✓ {len(cursos_para_criar)} cursos criados'))
        else:
            self.stdout.write(f'  → Todos os cursos já existem')
        
        cursos = list(Curso.objects.all())
        self.stdout.write(self.style.SUCCESS(f'  ✓ Total de {len(cursos)} cursos em {time.time()-inicio:.2f}s'))

        for curso in cursos:
            for semestre in semestres:
                    CursoPorSemestre.objects.get_or_create(
                        curso=curso,
                        semestre=semestre,
                        defaults={'horas_requeridas': curso.horas_requeridas}
                    )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Configurações de CursoPorSemestre garantidas para todos os cursos e semestres'))
        
        # Categorias
        self.stdout.write('\n[4/7] Criando categorias...')
        inicio = time.time()
        categorias_nomes = [
            "Curso de idioma",
            "Participação como ouvinte em defesas (TCC, mestrado, doutorado)",
            "Participação em evento acadêmico (congresso, seminário, workshop, palestra)",
            "Participação em comissão organizadora de eventos",
            "Atividade acadêmica não creditada no curso",
            "Participação em curso afins (oficina, minicurso, extensão, capacitação)",
            "Ministrante de curso/extensão/palestra; debatedor em mesa-redonda",
            "Participação em curso na área específica (oficina, minicurso, extensão)",
            "Monitoria (mín. 20h/semestre)",
            "Iniciação científica (mín. 150h)",
            "Publicação de artigo científico/resumo em anais (autor/coautor)",
            "Publicação de produção autoral (foto, artigo, exposição, reportagem) em periódico/site",
            "Apresentação de trabalho científico (incl. pôster) em evento regional/nacional/internacional",
            "Autor/coautor de capítulo de livro ou produção na revista Cayana",
            "Publicação de artigo científico completo em periódico",
            "Estágio Curricular Orientado",
            "Disciplinas Optativas e Eletivas oferecidas",
        ]
        
        # Criar categorias que não existem
        categorias_existentes = set(Categoria.objects.values_list('nome', flat=True))
        categorias_para_criar = []
        for nome in categorias_nomes:
            if nome not in categorias_existentes:
                categorias_para_criar.append(Categoria(nome=nome))
        
        if categorias_para_criar:
            Categoria.objects.bulk_create(categorias_para_criar)
            self.stdout.write(self.style.SUCCESS(f'  ✓ {len(categorias_para_criar)} categorias criadas'))
        else:
            self.stdout.write(f'  → Todas as categorias já existem')
        
        categorias = list(Categoria.objects.all())
        self.stdout.write(self.style.SUCCESS(f'  ✓ Total de {len(categorias)} categorias em {time.time()-inicio:.2f}s'))

        # CursoCategoria (associação)
        self.stdout.write('\n[5/7] Associando categorias aos cursos por semestre...')
        inicio = time.time()
        
        total_associacoes = len(cursos) * len(categorias) * len(semestres)
        self.stdout.write(f'  → Total de associações a criar: {total_associacoes}')
        
        # Buscar associações existentes
        associacoes_existentes = set(
            CategoriaCurso.objects.values_list('curso_id', 'categoria_id', 'semestre_id')
        )
        
        associacoes_para_criar = []
        total_processadas = 0
        
        for idx_curso, curso in enumerate(cursos, 1):
            for categoria in categorias:
                for semestre in semestres:
                    # Verificar se já existe
                    if (curso.id, categoria.id, semestre.id) not in associacoes_existentes:
                        limite_horas = random.randint(10, 60)
                        associacoes_para_criar.append(CategoriaCurso(
                            curso=curso,
                            categoria=categoria,
                            limite_horas=limite_horas,
                            equivalencia_horas='1h = 1h',
                            semestre=semestre
                        ))
                    
                    total_processadas += 1
            
            # Feedback a cada 5 cursos
            if idx_curso % 5 == 0:
                self.stdout.write(f'  → Processados {idx_curso}/{len(cursos)} cursos ({total_processadas}/{total_associacoes} associações)')
        
        # Criar em lote
        if associacoes_para_criar:
            self.stdout.write(f'\n  → Criando {len(associacoes_para_criar)} novas associações no banco...')
            # Criar em lotes de 1000 para evitar problemas de memória
            batch_size = 1000
            for i in range(0, len(associacoes_para_criar), batch_size):
                batch = associacoes_para_criar[i:i+batch_size]
                CategoriaCurso.objects.bulk_create(batch, ignore_conflicts=True)
                self.stdout.write(f'    → Lote {i//batch_size + 1}/{(len(associacoes_para_criar)-1)//batch_size + 1} criado ({i+len(batch)}/{len(associacoes_para_criar)})')
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ {len(associacoes_para_criar)} associações criadas'))
        else:
            self.stdout.write(f'  → Todas as associações já existem')
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Total de associações em {time.time()-inicio:.2f}s'))

        # Coordenador
        self.stdout.write('\n[6/7] Criando coordenadores...')
        inicio = time.time()
        
        usuarios_para_criar = []
        coordenadores_para_criar = []
        
        # Coordenador geral
        coord_username = 'coordenador'
        if not User.objects.filter(username=coord_username).exists():
            coord_user = User(
                username=coord_username,
                email=f'{coord_username}@example.com'
            )
            coord_user.set_password('senha123')
            usuarios_para_criar.append(coord_user)
        
        # Coordenadores por curso
        for curso in cursos:
            username = f'coord_{curso.nome.replace(" ", "_").lower()}'
            if not User.objects.filter(username=username).exists():
                user = User(
                    username=username,
                    email=f'{username}@example.com'
                )
                user.set_password('senha123')
                usuarios_para_criar.append(user)
        
        # Criar usuários em lote
        if usuarios_para_criar:
            User.objects.bulk_create(usuarios_para_criar)
            self.stdout.write(self.style.SUCCESS(f'  ✓ {len(usuarios_para_criar)} usuários coordenadores criados'))
        else:
            self.stdout.write(f'  → Todos os usuários coordenadores já existem')
        
        # Adicionar ao grupo e criar objetos Coordenador
        coord_geral = User.objects.get(username='coordenador')
        coord_geral.groups.add(grupos['Coordenador'])
        
        si_curso = Curso.objects.filter(nome='Sistemas de Informação').first()
        if si_curso:
            Coordenador.objects.get_or_create(user=coord_geral, curso=si_curso)
        
        coords_criados = 1
        for curso in cursos:
            username = f'coord_{curso.nome.replace(" ", "_").lower()}'
            user = User.objects.get(username=username)
            user.groups.add(grupos['Coordenador'])
            Coordenador.objects.get_or_create(user=user, curso=curso)
            coords_criados += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ {coords_criados} coordenadores configurados em {time.time()-inicio:.2f}s'))
        
        # Gestor
        self.stdout.write('\n[7/7] Criando gestor...')
        inicio = time.time()
        gestor_user, created = User.objects.get_or_create(username='gestor', defaults={'email': 'gestor@example.com'})
        if created:
            gestor_user.set_password('senha123')
            gestor_user.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Usuário gestor criado'))
        else:
            self.stdout.write(f'  → Usuário gestor já existe')
        
        gestor_user.groups.add(grupos['Gestor'])
        self.stdout.write(self.style.SUCCESS(f'  ✓ Gestor configurado em {time.time()-inicio:.2f}s'))
        
        # Resumo final
        tempo_total = time.time() - tempo_inicio
        minutos = int(tempo_total // 60)
        segundos = tempo_total % 60
        
        self.stdout.write(self.style.SUCCESS(f'\n{'='*60}'))
        self.stdout.write(self.style.SUCCESS(f'✓ DADOS INICIAIS POPULADOS COM SUCESSO!'))
        self.stdout.write(self.style.SUCCESS(f'{'='*60}'))
        self.stdout.write(self.style.SUCCESS(f'  → Semestres: {len(semestres)}'))
        self.stdout.write(self.style.SUCCESS(f'  → Cursos: {len(cursos)}'))
        self.stdout.write(self.style.SUCCESS(f'  → Categorias: {len(categorias)}'))
        self.stdout.write(self.style.SUCCESS(f'  → Associações: {CategoriaCurso.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  → Coordenadores: {coords_criados}'))
        self.stdout.write(self.style.SUCCESS(f'  → Tempo total: {minutos}min {segundos:.1f}s'))
        self.stdout.write(self.style.SUCCESS(f'{'='*60}'))
