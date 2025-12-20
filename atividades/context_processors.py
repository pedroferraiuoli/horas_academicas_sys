from django.core.cache import cache
from atividades.selectors import AlunoSelectors, CategoriaCursoSelectors

def categorias_do_usuario(request):
    """
    Context processor com cache para otimizar carregamento.
    Cache expira em 10 minutos e é invalidado por aluno.
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {}

    aluno = AlunoSelectors.get_aluno_by_user(user)
    if not aluno or not aluno.curso:
        return {}

    # Cache por aluno - expira em 5 minutos
    cache_key = f'categorias_aluno_{aluno.id}'
    categorias = cache.get(cache_key)
    
    if categorias is None:
        categorias = list(
            CategoriaCursoSelectors.get_categorias_curso_com_horas_por_aluno(
                aluno=aluno
            )
        )
        # Cache de 10 minutos (600 segundos)
        cache.set(cache_key, categorias, 600)

    return {'categorias_context': categorias}
