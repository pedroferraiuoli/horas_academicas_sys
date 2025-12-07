from .models import CursoCategoria

def categorias_do_usuario(request):

    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {}

    aluno = getattr(user, 'aluno', None)
    if not aluno or not aluno.curso:
        return {}

    categorias_qs = aluno.curso.get_categorias(semestre=aluno.semestre_ingresso)
    categorias_qs = categorias_qs.select_related('categoria')

    return {'categorias': categorias_qs}