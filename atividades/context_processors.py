from atividades.selectors import CursoCategoriaSelectors

def categorias_do_usuario(request):

    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {}

    aluno = getattr(user, 'aluno', None)
    if not aluno or not aluno.curso:
        return {}

    categorias_qs = CursoCategoriaSelectors.get_curso_categorias_por_semestre(
        curso=aluno.curso,
        semestre=aluno.semestre_ingresso
    ).select_related('categoria')

    return {'categorias_context': categorias_qs}