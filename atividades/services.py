from atividades.selectors import CursoCategoriaSelectors
from .models import Aluno, Atividade, CategoriaAtividade, Curso, Coordenador, CursoCategoria, Semestre
from django.db import transaction
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

    
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
            origem_qs = CursoCategoria.objects.filter(semestre=source_semestre).select_related('categoria', 'curso')
            cursos_por_id = {}
            for cc in origem_qs:
                cursos_por_id.setdefault(cc.curso_id, []).append(cc)

            for curso_id, curso_categorias in cursos_por_id.items():
                # ids já existentes no semestre destino para este curso
                existing_cat_ids = set(
                    CursoCategoria.objects.filter(curso_id=curso_id, semestre=semestre_novo).values_list('categoria_id', flat=True)
                )
                for cc in curso_categorias:
                    if cc.categoria_id in existing_cat_ids:
                        continue
                    to_create.append(CursoCategoria(
                        curso_id=curso_id,
                        categoria_id=cc.categoria_id,
                        limite_horas=cc.limite_horas,
                        equivalencia_horas=cc.equivalencia_horas,
                        semestre=semestre_novo
                    ))

            if to_create:
                CursoCategoria.objects.bulk_create(to_create)
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
    def aprovar_horas(*, atividade: Atividade, horas_aprovadas: int):
        if horas_aprovadas is None:
            raise ValueError('Informe a quantidade de horas.')
        
        if horas_aprovadas < 0:
            raise ValueError('Horas negativas não são permitidas')

        if horas_aprovadas > atividade.horas:
            raise ValueError('Horas aprovadas não podem exceder as horas da atividade')

        atividade.horas_aprovadas = horas_aprovadas
        atividade.save(update_fields=['horas_aprovadas'])

class CursoCategoriaService:
   
   @staticmethod
   def create_categoria_curso(*, form, coordenador: Coordenador):
        categoria = CategoriaAtividade.objects.create(nome=form.cleaned_data['nome'])
        curso_categoria = CursoCategoria.objects.create(
            curso=coordenador.curso,
            categoria=categoria,
            limite_horas=form.cleaned_data['limite_horas'],
            semestre=form.cleaned_data['semestre']
        )
        return curso_categoria
   
   @staticmethod
   def associar_categorias(*, curso, semestre, dados_post):
        categorias_disponiveis = CursoCategoriaSelectors.get_curso_categorias_disponiveis_para_associar(
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
                    CursoCategoria.objects.create(
                        curso=curso,
                        categoria=categoria,
                        limite_horas=limite,
                        semestre=semestre
                    )
                    adicionadas += 1

        if adicionadas == 0:
            raise ValueError('Nenhuma categoria válida foi selecionada.')

        return adicionadas

