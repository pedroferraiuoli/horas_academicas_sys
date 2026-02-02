from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from atividades.models import Atividade, Curso, Categoria, CategoriaCurso, Aluno, Coordenador, CursoPorSemestre, Semestre
import random
import time

class Command(BaseCommand):
    help = 'Popula o sistema com dados iniciais: usuários, cursos, categorias e associações.'

    def handle(self, *args, **options):
        aluno = Aluno.objects.filter(matricula='20221120025').first()
        if aluno:
            self.stdout.write(self.style.SUCCESS(f'Aluno encontrado: {aluno.nome} - {aluno.matricula}'))
            for i in range(100):
                nome_atividade = f'Atividade de Teste {i+1}'
                descricao_atividade = 'Descrição da atividade de teste.'
                horas_atividade = random.randint(1, 30)
                curso_semestre = CursoPorSemestre.objects.filter(curso=aluno.curso, semestre=aluno.semestre_ingresso).first()
                categoria = CategoriaCurso.objects.filter(curso_semestre=curso_semestre).order_by('?').first()

                atividade = Atividade(
                    aluno=aluno,
                    nome=nome_atividade,
                    descricao=descricao_atividade,
                    horas=horas_atividade,
                    data=time.strftime('%Y-%m-%d'),
                    categoria=categoria,
                )
                atividade.save()

            self.stdout.write(self.style.SUCCESS('100 atividades de teste criadas com sucesso para o aluno.'))
        else:
            self.stdout.write(self.style.ERROR('Aluno com matrícula 202221120025 não encontrado.'))