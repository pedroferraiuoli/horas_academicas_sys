from django.views.decorators.http import require_POST
from .forms import AlterarEmailForm, CategoriaCursoForm
from .forms import CursoForm
from .forms import CategoriaAtividadeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, AtividadeForm
from .models import Aluno, Atividade, Curso, CategoriaAtividade, Coordenador, CursoCategoria
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group

@login_required
def criar_curso(request):
    if not request.user.groups.filter(name='Gestor').exists():
        return redirect('dashboard')
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Curso {form.instance.nome} criado com sucesso!')
            return redirect('dashboard')
    else:
        form = CursoForm()
    return render(request, 'atividades/form_curso.html', {'form': form})


@login_required
def editar_curso(request, curso_id):
    user = request.user
    curso = get_object_or_404(Curso, id=curso_id)
    if user.groups.filter(name='Gestor').exists():
        pode_editar = True
    elif user.groups.filter(name='Coordenador').exists():
        try:
            coordenador = Coordenador.objects.get(user=user)
            pode_editar = coordenador.curso.id == curso.id
        except Coordenador.DoesNotExist:
            pode_editar = False
    else:
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

@login_required
def excluir_curso(request, curso_id):
    if not request.user.groups.filter(name='Gestor').exists():
        return redirect('dashboard')
    curso = get_object_or_404(Curso, id=curso_id)
    if request.method == 'POST':
        curso.delete()
        messages.success(request, f'Curso {curso.nome} excluído com sucesso!')
        return redirect('listar_cursos')
    return render(request, 'atividades/excluir_curso.html', {'curso': curso})

@login_required
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
    else:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    return render(request, 'atividades/listar_cursos.html', {'cursos': cursos})

@login_required
def criar_categoria(request):
    user = request.user
    if not user.groups.filter(name='Gestor').exists():
        return redirect('dashboard')

    if request.method == 'POST':
        form = CategoriaAtividadeForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria {categoria.nome} criada com sucesso!')
            return redirect('dashboard')
    else:
        form = CategoriaAtividadeForm()
    return render(request, 'atividades/form_categoria.html', {'form': form})

@login_required
def editar_categoria(request, categoria_id):
    user = request.user
    categoria = get_object_or_404(CategoriaAtividade, id=categoria_id)
    if not user.groups.filter(name='Gestor').exists():
        return redirect('dashboard')
    if request.method == 'POST':
        form = CategoriaAtividadeForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoria {categoria.nome} atualizada com sucesso!')
            return redirect('listar_categorias')
    else:
        form = CategoriaAtividadeForm(instance=categoria)
    return render(request, 'atividades/form_categoria.html', {'form': form, 'categoria': categoria, 'edit': True})

@login_required
def excluir_categoria(request, categoria_id):
    if not request.user.groups.filter(name='Gestor').exists():
        return redirect('dashboard')
    categoria = get_object_or_404(CategoriaAtividade, id=categoria_id)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, f'Categoria {categoria.nome} excluída com sucesso!')
        return redirect('listar_categorias')
    return render(request, 'atividades/excluir_categoria.html', {'categoria': categoria})

@login_required
def listar_categorias(request):
    user = request.user
    if not user.groups.filter(name='Gestor').exists():
        return redirect('dashboard')
    categorias = CategoriaAtividade.objects.all()
    return render(request, 'atividades/listar_categorias.html', {'categorias': categorias})

@login_required
def criar_categoria_curso(request):
    user = request.user
    coordenador = getattr(request.user, 'coordenador', None)
    if not (user.groups.filter(name='Gestor').exists() or coordenador):
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    
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

@login_required
def editar_categoria_curso(request, categoria_id):
    user = request.user
    categoria = get_object_or_404(CursoCategoria, id=categoria_id)
    coordenador = getattr(request.user, 'coordenador', None)
    if not (user.groups.filter(name='Gestor').exists() or coordenador):
        return redirect('dashboard')
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

@login_required
def excluir_categoria_curso(request, categoria_id):
    user = request.user
    coordenador = getattr(request.user, 'coordenador', None)
    if not (user.groups.filter(name='Gestor').exists() or coordenador):
        return redirect('dashboard')
    categoria = get_object_or_404(CursoCategoria, id=categoria_id)
    if coordenador and coordenador.curso.id != categoria.curso.id:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, f'Categoria {categoria.categoria.nome} desassociada com sucesso!')
        return redirect('listar_categorias_curso')
    return render(request, 'atividades/excluir_categoria.html', {'categoria': categoria})

@login_required
def listar_categorias_curso(request):
    user = request.user
    coordenador = getattr(request.user, 'coordenador', None)
    if not (user.groups.filter(name='Gestor').exists() or coordenador):
        return redirect('dashboard')
    if coordenador:
        categorias = CursoCategoria.objects.filter(curso=coordenador.curso)
    else:
        categorias = CursoCategoria.objects.all()
    return render(request, 'atividades/listar_categorias_curso.html', {'categorias': categorias})

@login_required
def cadastrar_atividade(request):
    aluno = getattr(request.user, 'aluno', None)
    if not aluno:
        messages.error(request, 'Usuário não possui perfil de aluno.')
        return redirect('dashboard')
    categoria_id = request.GET.get('categoria')
    initial = {}
    if categoria_id:
        try:
            categoria = CategoriaAtividade.objects.get(id=categoria_id)
            initial['categoria'] = categoria
        except CategoriaAtividade.DoesNotExist:
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


@login_required
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

@login_required
def excluir_atividade(request, atividade_id):
    aluno = getattr(request.user, 'aluno', None)
    atividade = get_object_or_404(Atividade, id=atividade_id, aluno=aluno)
    if request.method == 'POST':
        atividade.delete()
        messages.success(request, f'Atividade {atividade.nome} excluída com sucesso!')
        return redirect('listar_atividades')
    return render(request, 'atividades/excluir_atividade.html', {'atividade': atividade})

@login_required
def listar_atividades(request):
    aluno = getattr(request.user, 'aluno', None)
    if not aluno:
        return redirect('dashboard')
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
        atividades = aluno.atividade_set.all()
        total_horas = aluno.horas_complementares_validas()
        horas_requeridas = aluno.curso.horas_requeridas if aluno.curso else 0
        if horas_requeridas > 0:
            progresso_percentual = min(100, round((float(total_horas) / float(horas_requeridas)) * 100))
        atividades_recentes = atividades.order_by('-criado_em')[:5]

        categorias = aluno.curso.curso_categorias.all() if aluno.curso else []
        for categoria in categorias:
            if categoria.ultrapassou_limite_pelo_aluno(aluno):
                ultrapassou_limite = True
                break

    return render(request, 'atividades/dashboard.html', {
        'aluno': aluno,
        'total_horas': total_horas,
        'progresso_percentual': progresso_percentual,
        'atividades_recentes': atividades_recentes,
        'ultrapassou_limite': ultrapassou_limite
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            curso = form.cleaned_data['curso']
            Aluno.objects.create(user=user, curso=curso)
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

@login_required
def criar_usuario_admin(request):
    if not request.user.groups.filter(name='Gestor').exists():
        return redirect('dashboard')
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

@login_required
def listar_usuarios_admin(request):
    if not request.user.groups.filter(name='Gestor').exists():
        return redirect('dashboard')
    from django.contrib.auth.models import User
    gestores = User.objects.filter(groups__name='Gestor')
    coordenadores = User.objects.filter(groups__name='Coordenador')
    return render(request, 'atividades/listar_usuarios_admin.html', {
        'gestores': gestores,
        'coordenadores': coordenadores
    })

@login_required
@require_POST
def ativar_desativar_usuario(request, user_id):
    if not request.user.groups.filter(name='Gestor').exists():
        return redirect('dashboard')
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
    if coordenador:
        curso = coordenador.curso
    elif user.groups.filter(name='Gestor').exists():
        cursos = Curso.objects.all()
        if request.method == 'POST':
            curso_id = request.POST.get('curso_id')
            try:
                curso = Curso.objects.get(id=curso_id)
            except Curso.DoesNotExist:
                curso = None
    else:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')

    categorias_vinculadas = CursoCategoria.objects.filter(curso=curso).values_list('categoria_id', flat=True) if curso else []
    categorias_disponiveis = CategoriaAtividade.objects.exclude(id__in=categorias_vinculadas) if curso else []

    if request.method == 'POST' and curso:
        # Verifica se o POST tem apenas curso selecionado (sem categorias)
        tem_categoria = any(request.POST.get(f'cat_{categoria.id}') for categoria in categorias_disponiveis)
        if not tem_categoria:
            # Apenas curso selecionado, renderiza novamente com as categorias
            return render(request, 'atividades/form_associar_categorias.html', {
                'categorias': categorias_disponiveis,
                'curso_nome': curso.nome if curso else '',
                'cursos': cursos,
                'curso_selecionado': curso.id if curso else '',
                'curso_required': True if user.groups.filter(name='Gestor').exists() else False
            })
        adicionadas = 0
        for categoria in categorias_disponiveis:
            if request.POST.get(f'cat_{categoria.id}'):
                limite = request.POST.get(f'horas_{categoria.id}') or 0
                try:
                    limite = float(limite)
                except ValueError:
                    limite = 0
                CursoCategoria.objects.create(
                    curso=curso,
                    categoria=categoria,
                    limite_horas=limite
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
        'curso_required': True if user.groups.filter(name='Gestor').exists() else False
    })
