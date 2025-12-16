from django.db.models import QuerySet, Prefetch, Q
from typing import Optional, List
from .models import Atividade, Aluno, Curso, Coordenador, Semestre
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