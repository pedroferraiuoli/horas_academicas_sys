from django.db.models import QuerySet, OuterRef, Exists
from typing import Optional, List
from .models import Atividade, Aluno, CategoriaAtividade, Curso, Coordenador, CursoCategoria, Semestre
from django.utils import timezone

class AtividadeSelectors:
    
    @staticmethod
    def get_atividade_by_id(atividade_id: int) -> Optional[Atividade]:
        """Busca atividade por ID com relacionamentos"""
        try:
            return Atividade.objects.select_related(
                'aluno__user',
                'aluno__curso',
                'categoria__curso',
                'categoria__categoria',
                'categoria__semestre'
            ).get(id=atividade_id)
        except Atividade.DoesNotExist:
            return None
    
    @staticmethod
    def get_atividades_aluno(aluno: Aluno) -> QuerySet[Atividade]:
        """Busca todas atividades de um aluno"""
        return aluno.atividades.all().select_related(
            'categoria__categoria',
            'categoria__curso',
            'categoria__semestre'
        ).order_by('-created_at')
    
    @staticmethod
    def get_atividades_recentes_aluno(aluno: Aluno, limite: int = 5) -> List[Atividade]:
        """Busca atividades recentes de um aluno"""
        return list(
            AtividadeSelectors.get_atividades_aluno(aluno)[:limite]
        )
    
    @staticmethod
    def get_atividades_pendentes_curso(curso: Curso) -> QuerySet[Atividade]:
        """Busca atividades pendentes de aprovação de um curso"""
        return Atividade.objects.filter(
            aluno__curso=curso,
            horas_aprovadas__isnull=True
        ).select_related(
            'aluno__user',
            'categoria__categoria'
        ).order_by('created_at')
    
    @staticmethod
    def get_num_atividades_pendentes_curso(curso: Curso) -> int:
        """Conta atividades pendentes de aprovação de um curso"""
        return Atividade.objects.filter(
            aluno__curso=curso,
            horas_aprovadas__isnull=True
        ).count()
    
class SemestreSelectors:
    
    @staticmethod
    def get_semestre_atual() -> Optional['Semestre']:
        hoje = timezone.now().date()
        try:
            return Semestre.objects.get(
                data_inicio__lte=hoje,
                data_fim__gte=hoje
            )
        except Semestre.DoesNotExist:
            return None
        
class CursoCategoriaSelectors:
    
    @staticmethod
    def get_curso_categorias_por_semestre_curso(curso: Curso, semestre: Semestre) -> QuerySet['CursoCategoria']:
        """Busca categorias de um curso em um semestre específico"""
        return CursoCategoria.objects.filter(
            curso=curso,
            semestre=semestre
        ).select_related('categoria').order_by('categoria__nome')
    
    @staticmethod
    def get_curso_categorias_por_curso(curso) -> QuerySet['CursoCategoria']:
        """Busca todas as categorias de um curso"""
        return curso.curso_categorias.select_related('categoria').all()
    
    @staticmethod
    def get_curso_categorias_disponiveis_para_associar(curso, semestre):
        """Retorna categorias que ainda não estão associadas ao curso no semestre"""
        CursoCategoria_qs = CursoCategoria.objects.filter(curso=curso, semestre=semestre).values_list('categoria_id', flat=True)
        disponiveis = CategoriaAtividade.objects.exclude(id__in=CursoCategoria_qs)
        return disponiveis.order_by('nome')
    
    @staticmethod
    def get_curso_categorias_usuario(user) -> QuerySet['CursoCategoria']:
        """Retorna categorias de curso visíveis para o usuário"""
        if user.groups.filter(name='Gestor').exists():
            return CursoCategoria.objects.select_related('curso', 'categoria', 'semestre').all()
        elif user.groups.filter(name='Coordenador').exists():
            try:
                coordenador = Coordenador.objects.get(user=user)
                return CursoCategoria.objects.select_related('curso', 'categoria', 'semestre').filter(curso=coordenador.curso)
            except Coordenador.DoesNotExist:
                return CursoCategoria.objects.none()
        return CursoCategoria.objects.none()
    
class AlunoSelectors:

    @staticmethod
    def _with_pendencia_annotation(qs):
        pendencias_subquery = Atividade.objects.filter(
            aluno=OuterRef('pk'),
            horas_aprovadas__isnull=True,
        )
        return qs.annotate(
            tem_pendencia=Exists(pendencias_subquery)
        )

    @staticmethod
    def get_aluno_by_user(user) -> Optional[Aluno]:
        try:
            return Aluno.objects.select_related('curso', 'semestre_ingresso').get(user=user)
        except Aluno.DoesNotExist:
            return None
        
    @staticmethod
    def get_alunos_com_pendencias_por_curso(curso) -> QuerySet[Aluno]:
        qs = Aluno.objects.filter(curso=curso)
        return (
            AlunoSelectors._with_pendencia_annotation(qs)
            .filter(tem_pendencia=True)
        )
    
    @staticmethod
    def get_num_alunos_com_pendencias_por_curso(curso):
        return AlunoSelectors.get_alunos_com_pendencias_por_curso(curso).count()
    
    @staticmethod
    def get_num_alunos_por_curso(curso):
        return curso.alunos.all().count()
    
    @staticmethod
    def get_alunos_por_curso_order_by_pendencia(curso):
        qs = Aluno.objects.filter(curso=curso).select_related(
            'user', 'semestre_ingresso'
        )
        return (
            AlunoSelectors._with_pendencia_annotation(qs)
            .order_by('-tem_pendencia', 'user__first_name')
        )
    
class UserSelectors:

    @staticmethod
    def is_user_coordenador(user) -> bool:
        """Verifica se o usuário é um coordenador"""
        return user.groups.filter(name='Coordenador').exists()
    
    @staticmethod
    def is_user_gestor(user) -> bool:
        """Verifica se o usuário é um gestor"""
        return user.groups.filter(name='Gestor').exists()
    
    @staticmethod
    def is_user_aluno(user) -> bool:
        """Verifica se o usuário é um aluno"""
        return hasattr(user, 'aluno')
    
    @staticmethod
    def get_coordenador_by_user(user) -> Optional[Coordenador]:
        """Retorna o coordenador associado ao usuário, se existir"""
        try:
            return Coordenador.objects.select_related('curso').get(user=user)
        except Coordenador.DoesNotExist:
            return None
        
    @staticmethod
    def get_gestor_users() -> QuerySet:
        """Retorna todos os usuários que são gestores"""
        from django.contrib.auth.models import User, Group

        gestor_group = Group.objects.get(name='Gestor')
        return User.objects.filter(groups=gestor_group)
    
    @staticmethod
    def get_coordenador_users() -> QuerySet:
        """Retorna todos os usuários que são coordenadores"""
        from django.contrib.auth.models import User, Group

        coordenador_group = Group.objects.get(name='Coordenador')
        return User.objects.filter(groups=coordenador_group)
    
    @staticmethod
    def get_user_groups(user) -> List[str]:
        """Retorna os nomes dos grupos aos quais o usuário pertence"""
        if not user.is_authenticated:
            return []
        if hasattr(user, 'aluno'):
            return ['Aluno']
        return list(user.groups.values_list('name', flat=True))
    
    @staticmethod
    def get_user_primary_group(user) -> Optional[str]:
        """Retorna o nome do primeiro grupo do usuário, se existir"""
        groups = UserSelectors.get_user_groups(user)
        return groups[0] if groups else None