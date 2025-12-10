from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, AtividadeForm, SemestreForm, CategoriaAtividadeForm, CursoForm, AlterarEmailForm, CategoriaCursoForm
from .models import Aluno, Atividade, Curso, CategoriaAtividade, Coordenador, CursoCategoria, Semestre
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group
from .decorators import gestor_required, coordenador_required, aluno_required, gestor_ou_coordenador_required
from .filters import AlunosFilter, CursoCategoriaFilter
from django.db.models import Exists, OuterRef, Value, BooleanField


@gestor_required
def criar_semestre(request):
    if request.method == 'POST':
        form = SemestreForm(request.POST)
        if form.is_valid():
            semestre = form.save()
            copiar_de_id = request.POST.get('copiar_de')
            if copiar_de_id and copiar_de_id != 'Nenhum':
                source_semestre = Semestre.objects.filter(id=copiar_de_id).first()
                if source_semestre:
                    semestre.duplicate_categories_from(source_semestre)
            messages.success(request, f'Semestre {semestre.nome} criado com sucesso!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = SemestreForm()
    return render(request, 'atividades/form_semestre.html', {'form': form, 'semestres': Semestre.objects.all()})

@gestor_required
def editar_semestre(request, semestre_id):
    semestre = get_object_or_404(Semestre, id=semestre_id)
    if request.method == 'POST':
        form = SemestreForm(request.POST, instance=semestre)
        if form.is_valid():
            semestre = form.save()
            messages.success(request, f'Semestre {semestre.nome} atualizado com sucesso!')
            return redirect('listar_semestres')
    else:
        form = SemestreForm(instance=semestre)
    return render(request, 'atividades/form_semestre.html', {'form': form, 'semestre': semestre, 'edit': True})

@gestor_required
def excluir_semestre(request, semestre_id):
    semestre = get_object_or_404(Semestre, id=semestre_id)
    if request.method == 'POST':
        semestre.delete()
        messages.success(request, f'Semestre {semestre.nome} excluído com sucesso!')
        return redirect('listar_semestres')
    return render(request, 'atividades/excluir_semestre.html', {'semestre': semestre})

@gestor_required
def listar_semestres(request):
    semestres = Semestre.objects.all()
    return render(request, 'atividades/listar_semestres.html', {'semestres': semestres})

@gestor_required
def criar_curso(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Curso {form.instance.nome} criado com sucesso!')
            return redirect('dashboard')
    else:
        form = CursoForm()
    return render(request, 'atividades/form_curso.html', {'form': form})

@gestor_ou_coordenador_required
def editar_curso(request, curso_id):
    user = request.user
    curso = get_object_or_404(Curso, id=curso_id)
    pode_editar = True
    if user.groups.filter(name='Coordenador').exists():
        try:
            coordenador = Coordenador.objects.get(user=user)
            pode_editar = coordenador.curso.id == curso.id
        except Coordenador.DoesNotExist:
            pode_editar = False

    if not pode_editar:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(request, f'Curso {curso.nome} atualizado com sucesso!')
            return redirect('listar_cursos')
    else:
        form = CursoForm(instance=curso)
    return render(request, 'atividades/form_curso.html', {'form': form, 'curso': curso, 'edit': True})

@gestor_required
def excluir_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.method == 'POST':
        curso.delete()
        messages.success(request, f'Curso {curso.nome} excluído com sucesso!')
        return redirect('listar_cursos')
    return render(request, 'atividades/excluir_curso.html', {'curso': curso})

@gestor_ou_coordenador_required
def listar_cursos(request):
    user = request.user
    if user.groups.filter(name='Gestor').exists():
        cursos = Curso.objects.all()
    elif user.groups.filter(name='Coordenador').exists():
        try:
            coordenador = Coordenador.objects.get(user=user)
            cursos = Curso.objects.filter(id=coordenador.curso.id)
        except Coordenador.DoesNotExist:
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard')
    return render(request, 'atividades/listar_cursos.html', {'cursos': cursos})

@gestor_required
def criar_categoria(request):
    if request.method == 'POST':
        form = CategoriaAtividadeForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria {categoria.nome} criada com sucesso!')
            return redirect('dashboard')
    else:
        form = CategoriaAtividadeForm()
    return render(request, 'atividades/form_categoria.html', {'form': form})

@gestor_required
def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(CategoriaAtividade, id=categoria_id)
    if request.method == 'POST':
        form = CategoriaAtividadeForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoria {categoria.nome} atualizada com sucesso!')
            return redirect('listar_categorias')
    else:
        form = CategoriaAtividadeForm(instance=categoria)
    return render(request, 'atividades/form_categoria.html', {'form': form, 'categoria': categoria, 'edit': True})

@gestor_required
def excluir_categoria(request, categoria_id):
    categoria = get_object_or_404(CategoriaAtividade, id=categoria_id)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, f'Categoria {categoria.nome} excluída com sucesso!')
        return redirect('listar_categorias')
    return render(request, 'atividades/excluir_categoria.html', {'categoria': categoria})

@gestor_required
def listar_categorias(request):
    categorias = CategoriaAtividade.objects.all()
    return render(request, 'atividades/listar_categorias.html', {'categorias': categorias})

@gestor_ou_coordenador_required
def criar_categoria_curso(request):
    coordenador = getattr(request.user, 'coordenador', None)
    
    if request.method == 'POST':
        form = CategoriaCursoForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria {categoria.categoria.nome} associada a {categoria.curso.nome} com sucesso!')
            return redirect('dashboard')
        else:
            messages.warning(request, f'Erro ao associar categoria')
    else:
        form = CategoriaCursoForm()
    if coordenador:
        form.fields['curso'].queryset = Curso.objects.filter(id=coordenador.curso.id)
        form.fields['curso'].initial = coordenador.curso
        categorias_vinculadas = CursoCategoria.objects.filter(curso=coordenador.curso).values_list('categoria_id', flat=True)
        form.fields['categoria'].queryset = CategoriaAtividade.objects.exclude(id__in=categorias_vinculadas)
    return render(request, 'atividades/form_associar_categoria.html', {'form': form, 'coordenador': coordenador})

@gestor_ou_coordenador_required
def editar_categoria_curso(request, categoria_id):
    categoria = get_object_or_404(CursoCategoria, id=categoria_id)
    coordenador = getattr(request.user, 'coordenador', None)
    if coordenador and coordenador.curso.id != categoria.curso.id:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = CategoriaCursoForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoria {categoria.categoria.nome} atualizada com sucesso!')
            return redirect('listar_categorias')
    else:
        form = CategoriaCursoForm(instance=categoria)
    if coordenador:
        form.fields['curso'].queryset = Curso.objects.filter(id=coordenador.curso.id)
        form.fields['curso'].initial = coordenador.curso
    return render(request, 'atividades/form_associar_categoria.html', {'form': form, 'categoria': categoria, 'edit': True, 'coordenador': coordenador})

@gestor_ou_coordenador_required
def excluir_categoria_curso(request, categoria_id):
    coordenador = getattr(request.user, 'coordenador', None)
    categoria = get_object_or_404(CursoCategoria, id=categoria_id)
    if coordenador and coordenador.curso.id != categoria.curso.id:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, f'Categoria {categoria.categoria.nome} desassociada com sucesso!')
        return redirect('listar_categorias_curso')
    return render(request, 'atividades/excluir_categoria.html', {'categoria': categoria})

@gestor_ou_coordenador_required
def listar_categorias_curso(request):
    coordenador = getattr(request.user, 'coordenador', None)
    if coordenador:
        base_qs = CursoCategoria.objects.filter(curso=coordenador.curso)
    else:
        base_qs = CursoCategoria.objects.all()

    filtro = CursoCategoriaFilter(request.GET or None, queryset=base_qs)
    categorias = filtro.qs

    context = {
        'categorias': categorias,
        'filter': filtro,
    }
    return render(request, 'atividades/listar_categorias_curso.html', context)

@aluno_required
def cadastrar_atividade(request):
    aluno = getattr(request.user, 'aluno', None)
    categoria_id = request.GET.get('categoria')
    initial = {}
    if categoria_id:
        try:
            categoria = CursoCategoria.objects.get(id=categoria_id)
            initial['categoria'] = categoria
        except CursoCategoria.DoesNotExist:
            pass
    if request.method == 'POST':
        form = AtividadeForm(request.POST, request.FILES, aluno=aluno)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.aluno = aluno
            atividade.save()
            messages.success(request, f'Atividade {atividade.nome} cadastrada com sucesso!')
            return redirect('dashboard')
    else:
        form = AtividadeForm(aluno=aluno, initial=initial)
    return render(request, 'atividades/form_atividade.html', {'form': form})


@aluno_required
def editar_atividade(request, atividade_id):
    aluno = getattr(request.user, 'aluno', None)
    atividade = get_object_or_404(Atividade, id=atividade_id, aluno=aluno)
    if request.method == 'POST':
        form = AtividadeForm(request.POST, request.FILES, instance=atividade, aluno=aluno)
        if form.is_valid():
            form.save()
            messages.success(request, f'Atividade {atividade.nome} atualizada com sucesso!')
            return redirect('listar_atividades')
    else:
        form = AtividadeForm(instance=atividade, aluno=aluno)
    return render(request, 'atividades/form_atividade.html', {'form': form, 'atividade': atividade, 'edit': True})

@aluno_required
def excluir_atividade(request, atividade_id):
    aluno = getattr(request.user, 'aluno', None)
    atividade = get_object_or_404(Atividade, id=atividade_id, aluno=aluno)
    if request.method == 'POST':
        atividade.delete()
        messages.success(request, f'Atividade {atividade.nome} excluída com sucesso!')
        return redirect('listar_atividades')
    return render(request, 'atividades/excluir_atividade.html', {'atividade': atividade})

@aluno_required
def listar_atividades(request):
    aluno = getattr(request.user, 'aluno', None)
    atividades = Atividade.objects.filter(aluno=aluno)
    categoria_id = request.GET.get('categoria')
    categoria = None
    if categoria_id:
        try:
            categoria = CursoCategoria.objects.get(id=categoria_id)
            atividades = atividades.filter(categoria=categoria)
        except CursoCategoria.DoesNotExist:
            categoria = None
    return render(request, 'atividades/listar_atividades.html', {'atividades': atividades, 'categoria_filtrada': categoria})

@login_required
def dashboard(request):
    aluno = None
    total_horas = 0
    progresso_percentual = 0
    atividades_recentes = []
    ultrapassou_limite = False
    if hasattr(request.user, 'aluno'):
        aluno = request.user.aluno
        atividades = aluno.atividades.all()
        total_horas = aluno.horas_complementares_validas(apenas_aprovadas=True)
        horas_requeridas = aluno.curso.horas_requeridas if aluno.curso else 0
        if horas_requeridas > 0:
            progresso_percentual = min(100, round((float(total_horas) / float(horas_requeridas)) * 100))
        atividades_recentes = atividades.order_by('-criado_em')[:5]

        categorias = aluno.curso.get_categorias(semestre=aluno.semestre_ingresso) if aluno.curso else []
        for categoria in categorias:
            if categoria.ultrapassou_limite_pelo_aluno(aluno):
                ultrapassou_limite = True
                break

        return render(request, 'atividades/dashboard.html', {
            'aluno': aluno,
            'total_horas': total_horas if aluno else None,
            'progresso_percentual': progresso_percentual,
            'atividades_recentes': atividades_recentes,
            'ultrapassou_limite': ultrapassou_limite,
        })

    # Dashboard para gestor ou coordenador
    grupo = request.user.groups.all().first().name if request.user.groups.exists() else ''
    stats = {}
    semestre_atual = Semestre.get_semestre_atual()
    if grupo == 'Coordenador':
        coordenador = getattr(request.user, 'coordenador', None)
        if coordenador:
            curso = coordenador.curso
            alunos = curso.aluno_set.all()
            num_alunos = alunos.count()
            atividades_pendentes = Atividade.objects.filter(aluno__in=alunos, horas_aprovadas=None)
            atividades_pendentes_count = atividades_pendentes.count()
            alunos_com_pendencias = atividades_pendentes.values('aluno').distinct().count()  
            stats = {
                'num_alunos': num_alunos,
                'alunos_com_pendencias': alunos_com_pendencias,
                'atividades_pendentes': atividades_pendentes_count,
            }
    return render(request, 'atividades/dashboard_gestor.html', {
        'grupo': grupo,
        'stats': stats,
        'semestre_atual': semestre_atual,
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            curso = form.cleaned_data['curso']
            semestre = form.cleaned_data['semestre']
            Aluno.objects.create(user=user, curso=curso, semestre_ingresso=semestre)
            messages.success(request, 'Registro realizado com sucesso!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'atividades/register.html', {'form': form})

@login_required
def alterar_email(request):
    if request.method == 'POST':
        form = AlterarEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'E-mail alterado com sucesso!')
            return redirect('dashboard')
    else:
        form = AlterarEmailForm(instance=request.user)
    return render(request, 'atividades/alterar_email.html', {'form': form})

@gestor_required
def criar_usuario_admin(request):
    from .forms import AdminUserForm
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            tipo = form.cleaned_data['tipo']
            if tipo == 'gestor':
                grupo = Group.objects.get(name='Gestor')
                user.groups.add(grupo)
            elif tipo == 'coordenador':
                grupo = Group.objects.get(name='Coordenador')
                user.groups.add(grupo)
                curso = form.cleaned_data['curso']
                from .models import Coordenador
                Coordenador.objects.create(user=user, curso=curso)
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('dashboard')
    else:
        form = AdminUserForm()
    return render(request, 'atividades/criar_usuario_admin.html', {'form': form})

@gestor_required
def listar_usuarios_admin(request):
    from django.contrib.auth.models import User
    gestores = User.objects.filter(groups__name='Gestor')
    coordenadores = User.objects.filter(groups__name='Coordenador')
    return render(request, 'atividades/listar_usuarios_admin.html', {
        'gestores': gestores,
        'coordenadores': coordenadores
    })


@coordenador_required
def listar_alunos_coordenador(request):
    user = request.user
    try:
        coordenador = Coordenador.objects.get(user=user)
    except Coordenador.DoesNotExist:
        messages.error(request, 'Perfil de coordenador não encontrado.')
        return redirect('dashboard')

    curso = coordenador.curso

    pendencias_subquery = Atividade.objects.filter(
        aluno=OuterRef('pk'),
        horas_aprovadas__isnull=True,
    )

    alunos_base = (
        Aluno.objects.filter(curso=curso)
        .annotate(
            tem_pendencia=Exists(pendencias_subquery)
        )
        .select_related('user', 'semestre_ingresso')
        .order_by('-tem_pendencia', 'user__first_name')
    )

    filtro = AlunosFilter(request.GET, queryset=alunos_base)
    alunos_filtrados = filtro.qs

    alunos = []
    for aluno in alunos_filtrados:
        alunos.append({'aluno': aluno, 'horas_a_validar': aluno.tem_pendencia})

    return render(request, 'atividades/listar_alunos_coordenador.html', {
        'curso': curso,
        'alunos': alunos,
        'filter': filtro,
    })

@coordenador_required
def listar_atividades_coordenador(request):
    aluno_id = request.GET.get('aluno_id', None)
    user = request.user
    try:
        coordenador = Coordenador.objects.get(user=user)
    except Coordenador.DoesNotExist:
        messages.error(request, 'Perfil de coordenador não encontrado.')
        return redirect('dashboard')

    if aluno_id:
        aluno = get_object_or_404(Aluno, id=aluno_id, curso=coordenador.curso)
        atividades = Atividade.objects.filter(aluno=aluno)
    else: atividades = Atividade.objects.filter(horas_aprovadas__isnull=True, aluno__curso=coordenador.curso)

    return render(request, 'atividades/listar_atividades_coordenador.html', {
        'aluno': aluno if aluno_id else None,
        'atividades': atividades,
    })

@coordenador_required
def aprovar_horas_atividade(request, atividade_id):
    user = request.user
    try:
        coordenador = Coordenador.objects.get(user=user)
    except Coordenador.DoesNotExist:
        messages.error(request, 'Perfil de coordenador não encontrado.')
        return redirect('dashboard')

    atividade = get_object_or_404(Atividade, id=atividade_id)
    if atividade.aluno.curso != coordenador.curso:
        messages.error(request, 'Acesso negado à atividade deste aluno.')
        return redirect('dashboard')

    if request.method == 'POST':
        horas_aprovadas = request.POST.get('horas_aprovadas')
        try:
            horas_aprovadas = int(horas_aprovadas)
            if horas_aprovadas < 0 or horas_aprovadas > atividade.horas:
                raise ValueError
        except (ValueError, TypeError):
            messages.warning(request, 'Número inválido de horas aprovadas.')
            return redirect('listar_atividades_coordenador')

        atividade.horas_aprovadas = horas_aprovadas
        atividade.save()
        messages.success(request, f'Atividade {atividade.nome} aprovada com {horas_aprovadas} horas!')
        return redirect('listar_atividades_coordenador')

    return render(request, 'atividades/aprovar_atividade.html', {'atividade': atividade})

@gestor_required
@require_POST
def ativar_desativar_usuario(request, user_id):
    from django.contrib.auth.models import User
    user = User.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()
    if user.groups.filter(name='Coordenador').exists():
        return redirect('listar_usuarios_admin')
    return redirect('dashboard')

@login_required
def criar_categoria_curso_direta(request):
    user = request.user
    coordenador = getattr(user, 'coordenador', None)
    if not coordenador:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    from .forms import CategoriaCursoDiretaForm
    if request.method == 'POST':
        form = CategoriaCursoDiretaForm(request.POST)
        if form.is_valid():
            curso_categoria = form.save(coordenador)
            messages.success(request, f'Categoria {curso_categoria.categoria.nome} criada e vinculada ao curso {curso_categoria.curso.nome}!')
            return redirect('dashboard')
    else:
        form = CategoriaCursoDiretaForm()
    return render(request, 'atividades/form_categoria_curso_direta.html', {'form': form, 'curso_nome': coordenador.curso.nome})

@login_required
def associar_categorias_ao_curso(request):
    user = request.user
    coordenador = getattr(user, 'coordenador', None)
    curso = None
    cursos = None
    semestres = Semestre.objects.all()
    categorias_disponiveis = []
    
    if not user.groups.filter(name__in=['Coordenador', 'Gestor']).exists():
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
    if coordenador:
        curso = coordenador.curso
    elif user.groups.filter(name='Gestor').exists():
        cursos = Curso.objects.all()

    if request.method == 'POST' and not curso:
        curso_id = request.POST.get('curso_id')
        try:
            curso = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            curso = None
        semestre = get_object_or_404(Semestre, id=request.POST.get('semestre_id'))

    elif request.method == 'POST' and curso:

        semestre = get_object_or_404(Semestre, id=request.POST.get('semestre_id'))
        categorias_vinculadas = CursoCategoria.objects.filter(curso=curso, semestre=semestre).values_list('categoria_id', flat=True) if curso else []
        categorias_disponiveis = CategoriaAtividade.objects.exclude(id__in=categorias_vinculadas) if curso else []

        tem_categoria = any(request.POST.get(f'cat_{categoria.id}') for categoria in categorias_disponiveis)
        if not tem_categoria:

            return render(request, 'atividades/form_associar_categorias.html', {
                'categorias': categorias_disponiveis,
                'curso_nome': curso.nome if curso else '',
                'cursos': cursos,
                'curso_selecionado': curso.id if curso else '',
                'curso_required': True if user.groups.filter(name='Gestor').exists() else False,
                'semestres': semestres,
                'semestre_selecionado': request.POST.get('semestre_id', '')
            })
        adicionadas = 0
        for categoria in categorias_disponiveis:
            if request.POST.get(f'cat_{categoria.id}'):
                limite = request.POST.get(f'horas_{categoria.id}') or 0
                try:
                    limite = int(limite)
                except ValueError:
                    limite = 0
                
                if limite > 0:
                    CursoCategoria.objects.create(
                        curso=curso,
                        categoria=categoria,
                        limite_horas=limite,
                        semestre=semestre
                    )
                    adicionadas += 1
        if adicionadas:
            messages.success(request, f'{adicionadas} categoria(s) associada(s) ao curso!')
        else:
            messages.warning(request, 'Nenhuma categoria selecionada.')
        return redirect('dashboard')

    return render(request, 'atividades/form_associar_categorias.html', {
        'categorias': categorias_disponiveis,
        'curso_nome': curso.nome if curso else '',
        'cursos': cursos,
        'curso_selecionado': curso.id if curso else '',
        'curso_required': True if user.groups.filter(name='Gestor').exists() else False,
        'semestres': semestres,
    })
