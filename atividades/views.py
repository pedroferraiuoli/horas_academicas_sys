from django.views import View
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from atividades.selectors import AlunoSelectors, AtividadeSelectors, CursoCategoriaSelectors, CursoSelectors, SemestreSelectors
from .forms import UserRegistrationForm, AtividadeForm, SemestreForm, CategoriaAtividadeForm, CursoForm, AlterarEmailForm, CategoriaCursoForm
from .models import Aluno, Atividade, Curso, CategoriaAtividade, Coordenador, CursoCategoria, Semestre
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group
from .decorators import gestor_required, coordenador_required
from .filters import AlunosFilter, AtividadesFilter, CursoCategoriaFilter
from django.db.models import Exists, OuterRef
from django.views.generic import TemplateView
from .services import RegisterService, SemestreService
from .mixins import AlunoRequiredMixin, GestorRequiredMixin, GestorOuCoordenadorRequiredMixin, LoginRequiredMixin


class CriarCursoView(GestorRequiredMixin, View):
    template_name = 'atividades/form_curso.html'

    def get(self, request):
        form = CursoForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CursoForm(request.POST)
        if form.is_valid():
            curso_instance = form.save() 
            messages.success(request, f'Curso {curso_instance.nome} criado com sucesso!')
            return redirect('dashboard')
        
        return render(request, self.template_name, {'form': form})

class EditarCursoView(GestorRequiredMixin, View):
    template_name = 'atividades/form_curso.html'

    def dispatch(self, request, curso_id, *args, **kwargs):
        self.curso = get_object_or_404(Curso, id=curso_id)       
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = CursoForm(instance=self.curso)
        return render(request, self.template_name, {'form': form, 'curso': self.curso, 'edit': True})

    def post(self, request):
        form = CursoForm(request.POST, instance=self.curso)
        if form.is_valid():
            form.save()
            messages.success(request, f'Curso {self.curso.nome} atualizado com sucesso!')
            return redirect('listar_cursos')
            
        return render(request, self.template_name, {'form': form, 'curso': self.curso, 'edit': True})

class ExcluirCursoView(GestorRequiredMixin, View):
    template_name = 'atividades/excluir_curso.html'

    def dispatch(self, request, curso_id, *args, **kwargs):
        self.curso = get_object_or_404(Curso, id=curso_id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'curso': self.curso})

    def post(self, request):
        self.curso.delete()
        messages.success(request, f'Curso {self.curso.nome} excluído com sucesso!')
        return redirect('listar_cursos')

class ListarCursosView(GestorRequiredMixin, TemplateView):
    template_name = 'atividades/listar_cursos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cursos'] = Curso.objects.all()
        return context

class CriarSemestreView(GestorRequiredMixin, View):
    template_name = 'atividades/form_semestre.html'

    def get(self, request):
        form = SemestreForm()
        semestres = Semestre.objects.all()
        return render(request, self.template_name, {'form': form, 'semestres': semestres})

    def post(self, request):
        form = SemestreForm(request.POST)
        if form.is_valid():
            form.save()
            semestre = SemestreService.criar_semestre_com_copia(form, request.POST.get('copiar_de'))
            messages.success(request, f'Semestre {semestre.nome} criado com sucesso!')
            return redirect('dashboard')
        
        messages.warning(request, 'Por favor, corrija os erros abaixo.')
        semestres = Semestre.objects.all()
        return render(request, self.template_name, {'form': form, 'semestres': semestres})

class EditarSemestreView(GestorRequiredMixin, View):
    template_name = 'atividades/form_semestre.html'

    def get(self, request, semestre_id):
        semestre = get_object_or_404(Semestre, id=semestre_id)
        form = SemestreForm(instance=semestre)
        return render(request, self.template_name, {'form': form, 'semestre': semestre, 'edit': True})

    def post(self, request, semestre_id):
        semestre = get_object_or_404(Semestre, id=semestre_id)
        form = SemestreForm(request.POST, instance=semestre)
        if form.is_valid():
            semestre = form.save()
            messages.success(request, f'Semestre {semestre.nome} atualizado com sucesso!')
            return redirect('listar_semestres')
        
        return render(request, self.template_name, {'form': form, 'semestre': semestre, 'edit': True})
    
class ExcluirSemestreView(GestorRequiredMixin, View):
    template_name = 'atividades/excluir_semestre.html'

    def dispatch(self, request, semestre_id, *args, **kwargs):
        self.semestre = get_object_or_404(Semestre, id=semestre_id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'semestre': self.semestre})

    def post(self, request):
        self.semestre.delete()
        messages.success(request, f'Semestre {self.semestre.nome} excluído com sucesso!')
        return redirect('listar_semestres')
    
class ListarSemestresView(GestorRequiredMixin, TemplateView):
    template_name = 'atividades/listar_semestres.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['semestres'] = Semestre.objects.all()
        return context

class CriarCategoriaView(GestorRequiredMixin, View):
    template_name = 'atividades/form_categoria.html'

    def get(self, request):
        form = CategoriaAtividadeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CategoriaAtividadeForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria {categoria.nome} criada com sucesso!')
            return redirect('dashboard')
        
        return render(request, self.template_name, {'form': form})

class EditarCategoriaView(GestorRequiredMixin, View):
    template_name = 'atividades/form_categoria.html'

    def get(self, request, categoria_id):
        categoria = get_object_or_404(CategoriaAtividade, id=categoria_id)
        form = CategoriaAtividadeForm(instance=categoria)
        return render(request, self.template_name, {'form': form, 'categoria': categoria, 'edit': True})

    def post(self, request, categoria_id):
        categoria = get_object_or_404(CategoriaAtividade, id=categoria_id)
        form = CategoriaAtividadeForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoria {categoria.nome} atualizada com sucesso!')
            return redirect('listar_categorias')
        
        return render(request, self.template_name, {'form': form, 'categoria': categoria, 'edit': True})
    
class ExcluirCategoriaView(GestorRequiredMixin, View):
    template_name = 'atividades/excluir_categoria.html'

    def dispatch(self, request, *args, **kwargs):
        self.categoria = get_object_or_404(CategoriaAtividade, id=kwargs['categoria_id'])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'categoria': self.categoria})

    def post(self, request):
        self.categoria.delete()
        messages.success(request, f'Categoria {self.categoria.nome} excluída com sucesso!')
        return redirect('listar_categorias')

class ListarCategoriasView(GestorRequiredMixin, TemplateView):
    template_name = 'atividades/listar_categorias.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaAtividade.objects.all()
        return context
    
class CriarCategoriaCursoView(GestorOuCoordenadorRequiredMixin, View):
    template_name = 'atividades/form_associar_categoria.html'

    def get(self, request):
        coordenador = getattr(request.user, 'coordenador', None)
        form = CategoriaCursoForm(user=request.user)
        return render(request, self.template_name, {'form': form, 'coordenador': coordenador})

    def post(self, request):
        coordenador = getattr(request.user, 'coordenador', None)
        form = CategoriaCursoForm(request.POST, user=request.user)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria {categoria.categoria.nome} associada a {categoria.curso.nome} com sucesso!')
            return redirect('dashboard')

        return render(request, self.template_name, {'form': form, 'coordenador': coordenador})
    
class EditarCategoriaCursoView(GestorOuCoordenadorRequiredMixin, View):
    template_name = 'atividades/form_associar_categoria.html'

    def dispatch(self, request, *args, **kwargs):
        self.categoria = get_object_or_404(CursoCategoria, id=kwargs['categoria_id'])
        self.coordenador = getattr(request.user, 'coordenador', None)
        if self.coordenador and self.coordenador.curso.id != self.categoria.curso.id:
            messages.warning(request, 'Acesso negado.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = CategoriaCursoForm(instance=self.categoria, user=request.user)
        return render(request, self.template_name, {'form': form, 'categoria': self.categoria, 'edit': True, 'coordenador': self.coordenador})
    
    def post(self, request):
        form = CategoriaCursoForm(request.POST, instance=self.categoria, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoria {self.categoria.categoria.nome} atualizada com sucesso!')
            return redirect('listar_categorias')
        
        return render(request, self.template_name, {'form': form, 'categoria': self.categoria, 'edit': True, 'coordenador': self.coordenador})

class ExcluirCategoriaCursoView(GestorOuCoordenadorRequiredMixin, View):
    template_name = 'atividades/excluir_categoria.html'

    def get(self, request, categoria_id):
        coordenador = getattr(request.user, 'coordenador', None)
        categoria = get_object_or_404(CursoCategoria, id=categoria_id)
        if coordenador and coordenador.curso.id != categoria.curso.id:
            messages.warning(request, 'Acesso negado.')
            return redirect('dashboard')
        return render(request, self.template_name, {'categoria': categoria})

    def post(self, request, categoria_id):
        coordenador = getattr(request.user, 'coordenador', None)
        categoria = get_object_or_404(CursoCategoria, id=categoria_id)
        if coordenador and coordenador.curso.id != categoria.curso.id:
            messages.warning(request, 'Acesso negado.')
            return redirect('dashboard')
        categoria.delete()
        messages.success(request, f'Categoria {categoria.categoria.nome} desassociada com sucesso!')
        return redirect('listar_categorias_curso')

class ListarCategoriasCursoView(GestorOuCoordenadorRequiredMixin, TemplateView):
    template_name = 'atividades/listar_categorias_curso.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_qs = CursoCategoriaSelectors.get_curso_categorias_usuario(self.request.user)

        filtro = CursoCategoriaFilter(self.request.GET or None, queryset=base_qs)
        categorias = filtro.qs

        context['categorias'] = categorias
        context['filter'] = filtro
        return context

class CadastrarAtividadeView(AlunoRequiredMixin, View):
    template_name = 'atividades/form_atividade.html'

    def dispatch(self, request, *args, **kwargs):
        self.aluno = getattr(request.user, 'aluno', None)
        if not self.aluno:
            messages.warning(request, 'Acesso negado.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        categoria_id = request.GET.get('categoria')
        form = AtividadeForm(aluno=self.aluno, categoria_id=categoria_id)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = AtividadeForm(request.POST, request.FILES, aluno=self.aluno)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.aluno = self.aluno
            atividade.save()
            messages.success(request, f'Atividade {atividade.nome} cadastrada com sucesso!')
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})
    
class EditarAtividadeView(AlunoRequiredMixin, View):
    template_name = 'atividades/form_atividade.html'

    def dispatch(self, request, atividade_id, *args, **kwargs):
        self.aluno = getattr(request.user, 'aluno', None)
        if not self.aluno:
            messages.warning(request, 'Acesso negado.')
            return redirect('dashboard')
        self.atividade = get_object_or_404(Atividade, id=atividade_id, aluno=self.aluno)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = AtividadeForm(instance=self.atividade, aluno=self.aluno)
        return render(request, self.template_name, {'form': form, 'atividade': self.atividade, 'edit': True})

    def post(self, request):
        form = AtividadeForm(request.POST, request.FILES, instance=self.atividade, aluno=self.aluno)
        if form.is_valid():
            form.save()
            messages.success(request, f'Atividade {self.atividade.nome} atualizada com sucesso!')
            return redirect('listar_atividades')
        return render(request, self.template_name, {'form': form, 'atividade': self.atividade, 'edit': True})
    
class ExcluirAtividadeView(AlunoRequiredMixin, View):
    template_name = 'atividades/excluir_atividade.html'

    def dispatch(self, request, atividade_id, *args, **kwargs):
        self.aluno = getattr(request.user, 'aluno', None)
        if not self.aluno:
            messages.warning(request, 'Acesso negado.')
            return redirect('dashboard')
        self.atividade = get_object_or_404(Atividade, id=atividade_id, aluno=self.aluno)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'atividade': self.atividade})

    def post(self, request):
        self.atividade.delete()
        messages.success(request, f'Atividade {self.atividade.nome} excluída com sucesso!')
        return redirect('listar_atividades')

class ListarAtividadesView(AlunoRequiredMixin, TemplateView):
    template_name = 'atividades/listar_atividades.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aluno = getattr(self.request.user, 'aluno', None)
        atividades = AtividadeSelectors.get_atividades_aluno(aluno)
        filtro = AtividadesFilter(self.request.GET or None, queryset=atividades, request=self.request)
        atividades_filtradas = filtro.qs
        context['atividades'] = atividades_filtradas
        context['filter'] = filtro
        return context

class DashboardView(LoginRequiredMixin, TemplateView):

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if hasattr(user, 'aluno'):
            self.dashboard_type = 'aluno'
            self.template_name = 'atividades/dashboard.html'
        elif user.groups.filter(name='Coordenador').exists():
            self.dashboard_type = 'coordenador'
            self.template_name = 'atividades/dashboard_gestor.html'
        else:
            self.dashboard_type = 'gestor'
            self.template_name = 'atividades/dashboard_gestor.html'

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.dashboard_type == 'aluno':
            context.update(self.get_aluno_context())
        else:
            context.update(self.get_gestor_context())

        return context
    
    def get_aluno_context(self):
        aluno = AlunoSelectors.get_aluno_by_user(self.request.user)

        total_horas = AlunoSelectors.horas_complementares_validas(aluno, apenas_aprovadas=True)
        horas_requeridas = aluno.curso.horas_requeridas if aluno.curso else 0

        progresso = 0
        if horas_requeridas > 0:
            progresso = min(100, round((total_horas / horas_requeridas) * 100))

        atividades_recentes = AtividadeSelectors.get_atividades_recentes_aluno(aluno, limite=5)

        ultrapassou_limite = False
        if aluno.curso:
            categorias = CursoSelectors.get_categorias_do_curso(aluno.curso, semestre=aluno.semestre_ingresso)
            ultrapassou_limite = any(
                c.ultrapassou_limite_pelo_aluno(aluno)
                for c in categorias
            )

        return {
            'aluno': aluno,
            'total_horas': total_horas,
            'progresso_percentual': progresso,
            'atividades_recentes': atividades_recentes,
            'ultrapassou_limite': ultrapassou_limite,
        }


    def get_gestor_context(self):
        user = self.request.user
        grupo = user.groups.first().name if user.groups.exists() else ''
        semestre_atual = SemestreSelectors.get_semestre_atual()

        stats = {}

        if grupo == 'Coordenador':
            coordenador = getattr(user, 'coordenador', None)
            if coordenador:
                curso = coordenador.curso
                alunos = curso.alunos.all()
                alunos_com_pendencias = AlunoSelectors.get_alunos_com_pendencias(curso)
                atividades_pendentes = AtividadeSelectors.get_num_atividades_pendentes_curso(curso)
                stats = {
                    'num_alunos': alunos.count(),
                    'alunos_com_pendencias':alunos_com_pendencias,
                    'atividades_pendentes': atividades_pendentes,
                }

        return {
            'grupo': grupo,
            'stats': stats,
            'semestre_atual': semestre_atual,
        }
    
class RegisterView(View):
    template_name = 'atividades/register.html'

    def get(self, request):
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            RegisterService.register_user_with_aluno(form)
            messages.success(request, 'Registro realizado com sucesso!')
            return redirect('login')
        return render(request, self.template_name, {'form': form})
    
class AlterarEmailView(LoginRequiredMixin, View):
    template_name = 'atividades/alterar_email.html'

    def get(self, request):
        form = AlterarEmailForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AlterarEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'E-mail alterado com sucesso!')
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})

class CriarUsuarioAdminView(GestorRequiredMixin, View):
    template_name = 'atividades/criar_usuario_admin.html'

    def get(self, request):
        from .forms import AdminUserForm
        form = AdminUserForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        from .forms import AdminUserForm
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
        return render(request, self.template_name, {'form': form})
    
class ListarUsuariosAdminView(GestorRequiredMixin, TemplateView):
    template_name = 'atividades/listar_usuarios.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.auth.models import User
        gestores = User.objects.filter(groups__name='Gestor')
        coordenadores = User.objects.filter(groups__name='Coordenador')
        context['gestores'] = gestores
        context['coordenadores'] = coordenadores
        return context

@coordenador_required
def listar_alunos_coordenador(request):
    user = request.user
    try:
        coordenador = Coordenador.objects.get(user=user)
    except Coordenador.DoesNotExist:
        messages.warning(request, 'Perfil de coordenador não encontrado.')
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
        messages.warning(request, 'Perfil de coordenador não encontrado.')
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
        messages.warning(request, 'Perfil de coordenador não encontrado.')
        return redirect('dashboard')

    atividade = get_object_or_404(Atividade, id=atividade_id)
    if atividade.aluno.curso != coordenador.curso:
        messages.warning(request, 'Acesso negado à atividade deste aluno.')
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
        messages.warning(request, 'Acesso negado.')
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
        messages.warning(request, 'Acesso negado.')
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
