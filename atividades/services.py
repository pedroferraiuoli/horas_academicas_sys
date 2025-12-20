from atividades.selectors import CategoriaCursoSelectors
from .models import Aluno, Atividade, Categoria, Curso, Coordenador, CategoriaCurso, Semestre
from django.db import transaction
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.cache import cache

    
class SemestreService:

    @staticmethod
    def criar_semestre_com_copia(*, form, copiar_de_id):
        if copiar_de_id and copiar_de_id != 'Nenhum':
            source_semestre = Semestre.objects.filter(id=copiar_de_id).first()
            if source_semestre:           
                SemestreService.duplicate_categories_from(semestre_novo=form, source_semestre=source_semestre)
                return True          
        return False
    
    @staticmethod
    def duplicate_categories_from(*, semestre_novo, source_semestre):
        if source_semestre is None or source_semestre.id == semestre_novo.id:
            return False

        to_create = []
        with transaction.atomic():
            origem_qs = CategoriaCurso.objects.filter(semestre=source_semestre).select_related('categoria', 'curso')
            cursos_por_id = {}
            for cc in origem_qs:
                cursos_por_id.setdefault(cc.curso_id, []).append(cc)

            for curso_id, curso_categorias in cursos_por_id.items():
                # ids já existentes no semestre destino para este curso
                existing_cat_ids = set(
                    CategoriaCurso.objects.filter(curso_id=curso_id, semestre=semestre_novo).values_list('categoria_id', flat=True)
                )
                for cc in curso_categorias:
                    if cc.categoria_id in existing_cat_ids:
                        continue
                    to_create.append(CategoriaCurso(
                        curso_id=curso_id,
                        categoria_id=cc.categoria_id,
                        limite_horas=cc.limite_horas,
                        equivalencia_horas=cc.equivalencia_horas,
                        semestre=semestre_novo
                    ))

            if to_create:
                CategoriaCurso.objects.bulk_create(to_create)
                return True
        return False

class UserService:

    @staticmethod
    def register_user_with_aluno(*, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        Aluno.objects.create(
            user=user,
            curso=form.cleaned_data['curso'],
            semestre_ingresso=form.cleaned_data['semestre'],
        )

        return user

    @staticmethod
    def criar_usuario_admin(*, form):
        """
        Cria usuário gestor ou coordenador com base no formulário
        """
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        tipo = form.cleaned_data['tipo']

        if tipo == 'gestor':
            grupo = Group.objects.get(name='Gestor')
            user.groups.add(grupo)

        elif tipo == 'coordenador':
            grupo = Group.objects.get(name='Coordenador')
            user.groups.add(grupo)

            curso = form.cleaned_data['curso']
            Coordenador.objects.create(
                user=user,
                curso=curso
            )

        return user
    
    @staticmethod
    def toggle_user_active_status(*, user_id):
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return user
    
class AtividadeService:

    @staticmethod
    def invalidar_cache_aluno(aluno_id: int):
        """Invalida o cache de categorias para um aluno específico"""
        cache_key = f'categorias_aluno_{aluno_id}'
        cache.delete(cache_key)

    @staticmethod
    def aprovar_horas(*, atividade: Atividade, horas_aprovadas: int):
        if horas_aprovadas is None:
            raise ValueError('Informe a quantidade de horas.')
        
        if horas_aprovadas < 0:
            raise ValueError('Horas negativas não são permitidas')

        if horas_aprovadas > atividade.horas:
            raise ValueError('Horas aprovadas não podem exceder as horas da atividade')
        
        if atividade.status == 'Limite Atingido':
            raise ValueError('Não é possível aprovar horas para esta atividade, o limite da categoria já foi atingido.')
        
        if atividade.categoria.atingiu_limite_pelo_aluno(atividade.aluno):
            raise ValueError('Não é possível aprovar horas para esta atividade, o limite da categoria já foi atingido para este aluno.')

        atividade.horas_aprovadas = horas_aprovadas
        atividade.save()
        
        # Invalidar cache do aluno após aprovação
        AtividadeService.invalidar_cache_aluno(atividade.aluno_id)

class CategoriaCursoService:
   
   @staticmethod
   def create_categoria_curso(*, form, coordenador: Coordenador):
        categoria = Categoria.objects.create(nome=form.cleaned_data['nome'])
        curso_categoria = CategoriaCurso.objects.create(
            curso=coordenador.curso,
            categoria=categoria,
            limite_horas=form.cleaned_data['limite_horas'],
            semestre=form.cleaned_data['semestre']
        )
        return curso_categoria
   
   @staticmethod
   def associar_categorias(*, curso, semestre, dados_post):
        categorias_disponiveis = CategoriaCursoSelectors.get_categorias_curso_disponiveis_para_associar(
            curso,
            semestre
        )

        adicionadas = 0

        for categoria in categorias_disponiveis:
            if dados_post.get(f'cat_{categoria.id}'):
                limite = dados_post.get(f'horas_{categoria.id}') or 0
                try:
                    limite = int(limite)
                except ValueError:
                    limite = 0

                if limite > 0:
                    CategoriaCurso.objects.create(
                        curso=curso,
                        categoria=categoria,
                        limite_horas=limite,
                        semestre=semestre
                    )
                    adicionadas += 1

        if adicionadas == 0:
            raise ValueError('Nenhuma categoria válida foi selecionada.')

        return adicionadas
   
class AlunoService:

    @staticmethod
    def calcular_horas_complementares_validas(
        *,
        aluno: Aluno,
        apenas_aprovadas: bool = False
    ) -> int:
        if not aluno.curso:
            return 0

        categorias = CategoriaCursoSelectors.get_categorias_curso(
            curso=aluno.curso,
            semestre=aluno.semestre_ingresso
        )

        total = 0

        for curso_categoria in categorias:
            qs = aluno.atividades.filter(categoria=curso_categoria)

            if apenas_aprovadas:
                soma = qs.aggregate(
                    total=Sum('horas_aprovadas')
                )['total'] or 0
            else:
                soma = qs.aggregate(
                    total=Sum('horas')
                )['total'] or 0

            limite = curso_categoria.limite_horas or 0
            total += min(soma, limite) if limite > 0 else soma

        return total


