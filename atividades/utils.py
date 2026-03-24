from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.cache import cache


def paginate_queryset(qs, *, page, per_page=15):
    paginator = Paginator(qs, per_page)

    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)

class CacheKeys:
    """Centraliza todas as chaves de cache"""
    ALUNO_CATEGORIAS = 'categorias_aluno_{}'
    COORDENADOR_STATS = 'coordenador_{}_dashboard_stats'
    GESTOR_STATS = 'gestor_dashboard_stats'


class CacheService:
    """Serviço genérico de cache - operações puras"""
    
    TTL_ALUNO = 600
    TTL_COORDENADOR = 600
    TTL_GESTOR = 600
    
    @staticmethod
    def invalidar_aluno(aluno_id: int) -> None:
        """Invalida cache de um aluno específico"""
        cache_key = CacheKeys.ALUNO_CATEGORIAS.format(aluno_id)
        cache.delete(cache_key)
    
    @staticmethod
    def invalidar_coordenador(curso_id: int) -> None:
        """Invalida cache de um coordenador específico"""
        cache_key = CacheKeys.COORDENADOR_STATS.format(curso_id)
        cache.delete(cache_key)
    
    @staticmethod
    def invalidar_gestor() -> None:
        """Invalida cache do gestor"""
        cache.delete(CacheKeys.GESTOR_STATS)
