from atividades.selectors import AlunoSelectors, CategoriaCursoSelectors

def categorias_do_usuario(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {}

    aluno = AlunoSelectors.get_aluno_by_user(user)
    if not aluno or not aluno.curso:
        return {}

    categorias = CategoriaCursoSelectors.get_categorias_curso_com_horas_por_aluno(
        aluno=aluno
    )

    return {'categorias_context': categorias}
