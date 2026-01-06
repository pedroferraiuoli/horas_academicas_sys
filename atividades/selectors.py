from django.db.models import QuerySet, OuterRef, Exists, Prefetch, Sum, Q
from django.db.models.functions import Coalesce
from typing import Optional, List
from .models import Atividade, Aluno, Categoria, Curso, Coordenador, CategoriaCurso, CursoPorSemestre, Semestre
from django.utils import timezone

class AtividadeSelectors:
    
    @staticmethod
    def get_atividade_by_id(atividade_id: int) -> Optional[Atividade]:
        """Busca atividade por ID com relacionamentos"""
        try:
            return Atividade.objects.select_related(
                'aluno__user',
                'aluno__curso',
                'categoria__curso_semestre',
                'categoria__categoria',
            ).get(id=atividade_id)
        except Atividade.DoesNotExist:
            return None
    
    @staticmethod
    def get_atividades_aluno(aluno: Aluno, curso_categoria=None, pendente=False, limite_atingido=False, aprovadas=True) -> QuerySet[Atividade]:
        """Busca todas atividades de um aluno"""
        atividades = aluno.atividades
        if curso_categoria:
            atividades = atividades.filter(categoria=curso_categoria)
        if pendente:
            atividades = atividades.filter(status='Pendente')
        if limite_atingido:
            atividades = atividades.filter(status='Limite Atingido')
        if not aprovadas:
            atividades = atividades.exclude(status='Aprovada')
        return atividades.select_related(
            'categoria__categoria',
            'categoria__curso_semestre',
        ).order_by('horas_aprovadas', '-created_at')
    
    @staticmethod
    def get_atividades_recentes_aluno(aluno: Aluno, limite: int = 5) -> List[Atividade]:
        """Busca atividades recentes de um aluno"""
        return list(
            AtividadeSelectors.get_atividades_aluno(aluno)[:limite]
        )
    
    @staticmethod
    def get_atividades_pendentes(curso=None):
        atividades = Atividade.objects.filter(status='Pendente')
        if curso:
            atividades = atividades.filter(aluno__curso=curso)
        return atividades.select_related(
            'aluno__user',
            'aluno__curso',
            'categoria__categoria'
        ).order_by('created_at')
    
    @staticmethod
    def get_num_atividades_pendentes(*, curso=None, aluno=None) -> int:
        return 500
        atividades = Atividade.objects.filter(status='Pendente')
        if curso:
            atividades = atividades.filter(aluno__curso=curso)
        if aluno:
            atividades = atividades.filter(aluno=aluno)
        return atividades.count()

    @staticmethod
    def get_total_horas_aluno(
        *,
        aluno: Aluno,
        categoria: Optional[CategoriaCurso] = None,
        apenas_aprovadas: bool = False,
        apenas_pendentes: bool = False
    ) -> int:
        qs = aluno.atividades

        if categoria:
            qs = qs.filter(categoria=categoria)
        if apenas_pendentes:
            qs = qs.filter(status='Pendente')

        campo = 'horas_aprovadas' if apenas_aprovadas else 'horas'

        return qs.aggregate(
            total=Sum(campo)
        )['total'] or 0
    
    
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
    
    @staticmethod
    def get_ultimos_semestres_com_alunos(limite: int = 5, *, curso=None) -> List[dict]:
        """Retorna os últimos semestres com contagem de alunos ingressantes"""
        from django.db.models import Count, Q
        
        if curso:
            semestres = Semestre.objects.annotate(
                num_alunos=Count('aluno', filter=Q(aluno__curso=curso))
            ).order_by('-data_inicio')[:limite]
        else:
            semestres = Semestre.objects.annotate(
                num_alunos=Count('aluno')
            ).order_by('-data_inicio')[:limite]
        
        return [
            {
                'semestre': s,
                'num_alunos': s.num_alunos
            }
            for s in semestres
        ]
        
class CategoriaCursoSelectors:
    
    @staticmethod
    def get_categorias_curso(*, curso=None, semestre=None) -> QuerySet['CategoriaCurso']:
        """Busca categorias"""

        cat = CategoriaCurso.objects.all()
        if curso:
            cat = cat.filter(curso_semestre__curso=curso)
        if semestre:
            cat = cat.filter(curso_semestre__semestre=semestre)
        return cat.select_related('categoria').order_by('categoria__nome')
    
    @staticmethod
    def get_categorias_curso_disponiveis_para_associar(curso, semestre):
        """Retorna categorias que ainda não estão associadas ao curso no semestre
        
        Regras:
        - Categorias gerais (especifica=False): disponíveis para todos os cursos
        - Categorias específicas (especifica=True): apenas se já foram associadas ao mesmo curso em outro semestre
        """
        # IDs já associados neste curso+semestre
        CategoriaCurso_qs = CategoriaCurso.objects.filter(curso_semestre__curso=curso, curso_semestre__semestre=semestre).values_list('categoria_id', flat=True)
        
        # IDs de categorias específicas já usadas neste curso (em qualquer semestre)
        categorias_especificas_do_curso = CategoriaCurso.objects.filter(
            curso_semestre__curso=curso,
            categoria__especifica=True
        ).values_list('categoria_id', flat=True).distinct()
        
        # Disponíveis = (gerais OU específicas já usadas neste curso) E não associadas neste semestre
        disponiveis = Categoria.objects.filter(
            Q(especifica=False) | Q(id__in=categorias_especificas_do_curso)
        ).exclude(id__in=CategoriaCurso_qs)
        
        return disponiveis.order_by('nome')
    
    @staticmethod
    def get_categorias_curso_usuario(user) -> QuerySet['CategoriaCurso']:
        """Retorna categorias de curso visíveis para o usuário"""
        if user.groups.filter(name='Gestor').exists():
            return CategoriaCurso.objects.select_related('curso_semestre', 'categoria').all()
        elif user.groups.filter(name='Coordenador').exists():
            try:
                coordenador = Coordenador.objects.get(user=user)
                return CategoriaCurso.objects.select_related('curso_semestre', 'categoria').filter(curso_semestre__curso=coordenador.curso)
            except Coordenador.DoesNotExist:
                return CategoriaCurso.objects.none()
        return CategoriaCurso.objects.none()
    
    @staticmethod
    def get_categorias_curso_com_horas_por_aluno(*, aluno):
        return (
            CategoriaCurso.objects
            .filter(
                curso_semestre__curso_id=aluno.curso_id, 
                curso_semestre__semestre_id=aluno.semestre_ingresso_id,
            )
            .annotate(
                horas_aprovadas_total=Coalesce(
                    Sum(
                        'atividade__horas_aprovadas',
                        filter=Q(
                            atividade__aluno_id=aluno.id,
                            atividade__horas_aprovadas__isnull=False
                        )
                    ),
                    0
                )
            )
            .select_related('categoria')
            .only(
                'id', 
                'limite_horas', 
                'equivalencia_horas',
                'categoria__nome'
            )
            .order_by('categoria__nome')
        )
    
class AlunoSelectors:

    def _with_pendencia_annotation(queryset: QuerySet[Aluno]) -> QuerySet[Aluno]:
        pendentes = Atividade.objects.filter(
            aluno=OuterRef('pk'),
            status='Pendente'
        )
        return queryset.annotate(
            tem_pendencia=Exists(pendentes)
        )

    @staticmethod
    def get_aluno_by_user(user) -> Optional[Aluno]:
        try:
            return Aluno.objects.select_related('curso', 'semestre_ingresso').get(user=user)
        except Aluno.DoesNotExist:
            return None
        
    @staticmethod
    def get_alunos_com_pendencias(*, curso=None) -> QuerySet[Aluno]:
        alunos = Aluno.objects
        if curso:
            alunos = alunos.filter(curso=curso)
        return AlunoSelectors._with_pendencia_annotation(alunos).filter(
            tem_pendencia=True
        ).select_related('user', 'curso')

    @staticmethod
    def get_num_alunos_com_pendencias(*, curso=None) -> int:
        alunos = Aluno.objects
        if curso:
            alunos = alunos.filter(curso=curso)
        return AlunoSelectors._with_pendencia_annotation(alunos).filter(
            tem_pendencia=True
        ).count()
    
    @staticmethod
    def get_num_alunos(*, curso=None) -> int:
        if curso:
            return curso.alunos.count()
        return Aluno.objects.count()
    
    @staticmethod
    def get_alunos_por_curso_order_by_pendencia(curso):
        pendentes = Atividade.objects.filter(
            aluno=OuterRef('pk'),
            status='Pendente'
        )

        alunos = Aluno.objects.filter(curso=curso)

        alunos = (
            alunos
            .annotate(tem_pendencia=Exists(pendentes))
            .select_related('user', 'curso')
        )
        return alunos.order_by('-tem_pendencia', 'user__first_name', 'user__last_name')
    
    @staticmethod
    def get_horas_necessarias_para_conclusao(aluno: Aluno) -> int:
        return aluno.curso.configuracoes_semestre.filter(
            semestre=aluno.semestre_ingresso
        ).first().horas_requeridas
    
class UserSelectors:

    @staticmethod
    def is_user_coordenador(user) -> bool:
        """Verifica se o usuário é um coordenador"""
        if user is None:
            return False
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

class CursoSelectors:

    @staticmethod
    def listar_cursos_com_categorias_semestre_atual():
        semestre_atual = SemestreSelectors.get_semestre_atual()

        # Prefetch das configurações do semestre atual
        config_semestre_atual = Prefetch(
            'configuracoes_semestre',
            queryset=CursoPorSemestre.objects.filter(semestre=semestre_atual),
            to_attr='config_semestre_atual_list'
        )
        
        # Prefetch das categorias dentro das configurações
        categorias_prefetch = Prefetch(
            'config_semestre_atual_list__categorias_curso',
            queryset=(
                CategoriaCurso.objects
                .select_related('categoria')
                .order_by('categoria__nome')
            ),
            to_attr='categorias_semestre_atual'
        )

        return (
            Curso.objects
            .prefetch_related(config_semestre_atual, categorias_prefetch)
            .distinct()
        )
   
class CategoriaSelectors:

    @staticmethod
    def listar_categorias_geral_com_cursos_semestre_atual():
        semestre_atual = SemestreSelectors.get_semestre_atual()

        return (
            Categoria.objects
            .filter(especifica=False)
            .distinct()
            .prefetch_related(
                Prefetch(
                    'categorias_curso',
                    queryset=(
                        CategoriaCurso.objects
                        .filter(curso_semestre__semestre=semestre_atual)
                        .select_related('curso_semestre__curso')
                    ),
                    to_attr='cursos_no_semestre_atual'
                )
            )
        )
    
class CursoPorSemestreSelectors:

    @staticmethod
    def get_curso_por_semestre(curso: Curso, semestre: Semestre) -> Optional[CursoPorSemestre]:
        try:
            return CursoPorSemestre.objects.get(curso=curso, semestre=semestre)
        except CursoPorSemestre.DoesNotExist:
            return None

    