from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from atividades.models import Curso, CategoriaAtividade, CursoCategoria

class Command(BaseCommand):
    help = 'Popula o sistema com dados iniciais: usuários, cursos, categorias e associações.'

    def handle(self, *args, **options):
        # Grupos
        grupos = {
            'Coordenador': Group.objects.get_or_create(name='Coordenador')[0],
            'Gestor': Group.objects.get_or_create(name='Gestor')[0],
        }

        # Cursos
        cursos_info = [
            {'nome': 'Sistemas de Informação', 'horas_requeridas': 600},
            {'nome': 'Design Gráfico', 'horas_requeridas': 400},
            {'nome': 'Engenharia da Computação', 'horas_requeridas': 500},
            {'nome': 'Educação Física', 'horas_requeridas': 250},
        ]
        cursos = []
        for info in cursos_info:
            curso, _ = Curso.objects.get_or_create(nome=info['nome'], defaults={'horas_requeridas': info['horas_requeridas']})
            cursos.append(curso)

        # Categorias
        categorias_nomes = ['Extensão', 'Pesquisa', 'Ensino', 'Cultura']
        categorias = []
        for nome in categorias_nomes:
            categoria, _ = CategoriaAtividade.objects.get_or_create(nome=nome)
            categorias.append(categoria)

        # CursoCategoria (associação)
        import random
        for curso in cursos:
            for categoria in categorias:
                limite_horas = random.randint(10, 60)
                CursoCategoria.objects.get_or_create(
                    curso=curso,
                    categoria=categoria,
                    defaults={
                        'limite_horas': limite_horas,
                        'carga_horaria': '1h = 1h'
                    }
                )

        # Usuários e perfis
        # Aluno
        aluno_user, created = User.objects.get_or_create(username='aluno', defaults={'email': 'aluno@example.com'})
        if created:
            aluno_user.set_password('senha123')
            aluno_user.save()
        aluno_curso = cursos[0]  # Sistemas de Informação
        from atividades.models import Aluno, Coordenador
        aluno_obj, _ = Aluno.objects.get_or_create(user=aluno_user, curso=aluno_curso)

        # Coordenador
        coord_user, created = User.objects.get_or_create(username='coordenador', defaults={'email': 'coordenador@example.com'})
        if created:
            coord_user.set_password('senha123')
            coord_user.save()
        coord_user.groups.add(grupos['Coordenador'])
        coord_curso = cursos[0]  # Sistemas de Informação
        coord_obj, _ = Coordenador.objects.get_or_create(user=coord_user, curso=coord_curso)

        # Gestor
        gestor_user, created = User.objects.get_or_create(username='gestor', defaults={'email': 'gestor@example.com'})
        if created:
            gestor_user.set_password('senha123')
            gestor_user.save()
        gestor_user.groups.add(grupos['Gestor'])
        # Não há modelo Gestor, apenas grupo

        self.stdout.write(self.style.SUCCESS('Dados iniciais populados com sucesso!'))
