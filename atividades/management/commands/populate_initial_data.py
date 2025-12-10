from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from atividades.models import Curso, CategoriaAtividade, CursoCategoria, Aluno, Coordenador

class Command(BaseCommand):
    help = 'Popula o sistema com dados iniciais: usuários, cursos, categorias e associações.'

    def handle(self, *args, **options):
        # Grupos
        grupos = {
            'Coordenador': Group.objects.get_or_create(name='Coordenador')[0],
            'Gestor': Group.objects.get_or_create(name='Gestor')[0],
        }

        # Semestres
        semestres_info = [
            {'nome': '2023.1', 'data_inicio': '2023-02-01', 'data_fim': '2023-07-31'},
            {'nome': '2023.2', 'data_inicio': '2023-08-01', 'data_fim': '2023-12-20'},
            {'nome': '2024.1', 'data_inicio': '2024-02-01', 'data_fim': '2024-07-31'},
            {'nome': '2024.2', 'data_inicio': '2024-08-01', 'data_fim': '2024-12-20'},
            {'nome': '2025.1', 'data_inicio': '2025-02-01', 'data_fim': '2025-07-31'},
            {'nome': '2025.2', 'data_inicio': '2025-08-01', 'data_fim': '2025-12-20'},
            {'nome': '2026.1', 'data_inicio': '2026-02-01', 'data_fim': '2026-07-31'},
            {'nome': '2026.2', 'data_inicio': '2026-08-01', 'data_fim': '2026-12-20'},
        ]
        for info in semestres_info:
            from atividades.models import Semestre
            Semestre.objects.get_or_create(nome=info['nome'], defaults={
                'data_inicio': info['data_inicio'],
                'data_fim': info['data_fim']
            })

        # Cursos
        cursos_info = [
            {'nome': 'Sistemas de Informação', 'horas_requeridas': 600},
            {'nome': 'Design Gráfico', 'horas_requeridas': 400},
            {'nome': 'Engenharia da Computação', 'horas_requeridas': 500},
            {'nome': 'Arquitetura e Urbanismo', 'horas_requeridas': 450},
            {'nome': 'Engenharia Ambiental', 'horas_requeridas': 250},
            {'nome': 'Engenharia Elétrica', 'horas_requeridas': 350},
            {'nome': 'Engenharia Mecânica', 'horas_requeridas': 400},
            {'nome': 'Administração', 'horas_requeridas': 200},        
        ]
        cursos = []
        for info in cursos_info:
            curso, _ = Curso.objects.get_or_create(nome=info['nome'], defaults={'horas_requeridas': info['horas_requeridas']})
            cursos.append(curso)

        # Categorias
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
        categorias = []
        for nome in categorias_nomes:
            categoria, _ = CategoriaAtividade.objects.get_or_create(nome=nome)
            categorias.append(categoria)

        # CursoCategoria (associação)
        import random
        for curso in cursos:
            for categoria in categorias:
                for semestre in Semestre.objects.all():
                    print('Associando', curso.nome, '->', categoria.nome, 'no semestre', semestre.nome)
                    limite_horas = random.randint(10, 60)
                    CursoCategoria.objects.get_or_create(
                        curso=curso,
                        categoria=categoria,
                        limite_horas=limite_horas,
                        equivalencia_horas= '1h = 1h',
                        semestre=semestre
                    )

        # Usuários e perfis
        # Aluno
        aluno_curso = cursos[0]
        for semestre in Semestre.objects.all():
            aux = 0 
            while aux < 30:
                print('Criando aluno para semestre', semestre.nome, 'número', aux+1)
                user_name = f'aluno{aux+1}_{semestre.nome.replace(".", "_")}'
                aluno_user, created = User.objects.get_or_create(username=user_name, defaults={'email': f'{user_name}@example.com'})
                if created:
                    aluno_user.set_password('senha123')
                    aluno_user.save()
                aluno_obj, _ = Aluno.objects.get_or_create(user=aluno_user, curso=aluno_curso, semestre_ingresso=semestre)
                aux += 1

        # Coordenador
        for curso in cursos:
            coord_user, created = User.objects.get_or_create(username=f'coord_{curso.nome.replace(" ", "_").lower()}', defaults={'email': f'coord_{curso.nome.replace(" ", "_").lower()}@example.com'})
            if created:
                coord_user.set_password('senha123')
                coord_user.save()
            coord_user.groups.add(grupos['Coordenador'])
            coord_obj, _ = Coordenador.objects.get_or_create(user=coord_user, curso=curso)
            
        # Gestor
        gestor_user, created = User.objects.get_or_create(username='gestor', defaults={'email': 'gestor@example.com'})
        if created:
            gestor_user.set_password('senha123')
            gestor_user.save()
        gestor_user.groups.add(grupos['Gestor'])
        # Não há modelo Gestor, apenas grupo

        self.stdout.write(self.style.SUCCESS('Dados iniciais populados com sucesso!'))
