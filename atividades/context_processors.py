from atividades.selectors import AlunoSelectors, CursoCategoriaSelectors

def categorias_do_usuario(request):

    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {}

    aluno = AlunoSelectors.get_aluno_by_user(user)
    if not aluno or not aluno.curso:
        return {}

    categorias_qs = CursoCategoriaSelectors.get_curso_categorias_por_semestre_curso(
        curso=aluno.curso,
        semestre=aluno.semestre_ingresso
    )
    
    return {'categorias_context': categorias_qs}