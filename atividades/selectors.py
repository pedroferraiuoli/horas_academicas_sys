from django.db.models import QuerySet, Prefetch, Q
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
        return Atividade.objects.filter(
            aluno=aluno
        ).select_related(
            'categoria__categoria',
            'categoria__curso',
            'categoria__semestre'
        ).order_by('-criado_em')
    
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
        ).order_by('criado_em')
    
    @staticmethod
    def get_atividades_by_coordenador(
        coordenador: Coordenador,
        aluno: Optional[Aluno] = None,
        apenas_pendentes: bool = False
    ) -> QuerySet[Atividade]:
        """
        Busca atividades que o coordenador pode visualizar
        """
        qs = Atividade.objects.filter(
            aluno__curso=coordenador.curso
        ).select_related(
            'aluno__user',
            'categoria__categoria'
        )
        
        if aluno:
            qs = qs.filter(aluno=aluno)
        
        if apenas_pendentes:
            qs = qs.filter(horas_aprovadas__isnull=True)
        
        return qs.order_by('-criado_em')
    
    @staticmethod
    def count_atividades_pendentes_curso(curso: Curso) -> int:
        """Conta atividades pendentes de um curso"""
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
    def get_curso_categorias_por_semestre(curso: Curso, semestre: Semestre) -> QuerySet['CursoCategoria']:
        """Busca categorias de um curso em um semestre específico"""
        return CursoCategoria.objects.filter(
            curso=curso,
            semestre=semestre
        ).select_related('categoria').order_by('categoria__nome')
    
    @staticmethod
    def categorias_disponiveis_para_associar(curso, semestre):
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