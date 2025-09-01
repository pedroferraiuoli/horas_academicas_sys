from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView, DetailView, ListView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from .forms import (
    AlterarEmailForm, CategoriaCursoForm, CursoForm, CategoriaAtividadeForm,
    UserRegistrationForm, AtividadeForm, AdminUserForm, CategoriaCursoDiretaForm
)
from .models import Aluno, Atividade, Curso, CategoriaAtividade, Coordenador, CursoCategoria


# Mixins personalizados
class GestorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Gestor').exists()


class CoordenadorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'coordenador')


class AlunoRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'aluno')


# Views principais
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'atividades/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        aluno = None
        total_horas = 0
        progresso_percentual = 0
        atividades_recentes = []
        ultrapassou_limite = False
        
        if hasattr(self.request.user, 'aluno'):
            aluno = self.request.user.aluno
            atividades = aluno.atividade_set.all()
            total_horas = aluno.horas_complementares_validas()
            total_horas_formatado = aluno.horas_complementares_validas_formatado()
            horas_requeridas = aluno.curso.horas_requeridas if aluno.curso else 0
            if horas_requeridas > 0:
                progresso_percentual = min(100, round((float(total_horas) / float(horas_requeridas)) * 100))
            atividades_recentes = atividades.order_by('-criado_em')[:5]

            categorias = aluno.curso.curso_categorias.all() if aluno.curso else []
            for categoria in categorias:
                if categoria.ultrapassou_limite_pelo_aluno(aluno):
                    ultrapassou_limite = True
                    break
            
            # Adiciona os dados ao contexto
            context.update({
                'aluno': aluno,
                'total_horas': total_horas_formatado if aluno else None,
                'progresso_percentual': progresso_percentual,
                'atividades_recentes': atividades_recentes,
                'ultrapassou_limite': ultrapassou_limite
            })
        
        return context


class RegisterView(FormView):
    template_name = 'atividades/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        curso = form.cleaned_data['curso']
        Aluno.objects.create(user=user, curso=curso)
        messages.success(self.request, 'Registro realizado com sucesso!')
        return super().form_valid(form)


class AlterarEmailView(LoginRequiredMixin, FormView):
    template_name = 'atividades/alterar_email.html'
    form_class = AlterarEmailForm
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'E-mail alterado com sucesso!')
        return super().form_valid(form)


# Views de Curso
class CriarCursoView(LoginRequiredMixin, GestorRequiredMixin, FormView):
    template_name = 'atividades/form_curso.html'
    form_class = CursoForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f'Curso {form.instance.nome} criado com sucesso!')
        return super().form_valid(form)


class EditarCursoView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'atividades/form_curso.html'
    form_class = CursoForm
    success_url = reverse_lazy('listar_cursos')

    def test_func(self):
        user = self.request.user
        curso = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        
        if user.groups.filter(name='Gestor').exists():
            return True
        elif user.groups.filter(name='Coordenador').exists():
            try:
                coordenador = Coordenador.objects.get(user=user)
                return coordenador.curso.id == curso.id
            except Coordenador.DoesNotExist:
                return False
        else:
            return False

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado.')
        return redirect('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['curso'] = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        context['edit'] = True
        return context

    def form_valid(self, form):
        curso = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        form.save()
        messages.success(self.request, f'Curso {curso.nome} atualizado com sucesso!')
        return super().form_valid(form)


class ExcluirCursoView(LoginRequiredMixin, GestorRequiredMixin, TemplateView):
    template_name = 'atividades/excluir_curso.html'

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado.')
        return redirect('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['curso'] = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        return context

    def post(self, request, *args, **kwargs):
        curso = get_object_or_404(Curso, id=self.kwargs['curso_id'])
        curso_nome = curso.nome
        curso.delete()
        messages.success(request, f'Curso {curso_nome} excluído com sucesso!')
        return redirect('listar_cursos')


class ListarCursosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'atividades/listar_cursos.html'
    context_object_name = 'cursos'

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='Gestor').exists() or user.groups.filter(name='Coordenador').exists()

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Gestor').exists():
            return Curso.objects.all()
        elif user.groups.filter(name='Coordenador').exists():
            try:
                coordenador = Coordenador.objects.get(user=user)
                return Curso.objects.filter(id=coordenador.curso.id)
            except Coordenador.DoesNotExist:
                return Curso.objects.none()
        else:
            return Curso.objects.none()

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado.')
        return redirect('dashboard')


# Views de Categoria
class CriarCategoriaView(LoginRequiredMixin, GestorRequiredMixin, FormView):
    template_name = 'atividades/form_categoria.html'
    form_class = CategoriaAtividadeForm
    success_url = reverse_lazy('dashboard')

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado.')
        return redirect('dashboard')

    def form_valid(self, form):
        categoria = form.save()
        messages.success(self.request, f'Categoria {categoria.nome} criada com sucesso!')
        return super().form_valid(form)


class EditarCategoriaView(LoginRequiredMixin, GestorRequiredMixin, FormView):
    template_name = 'atividades/form_categoria.html'
    form_class = CategoriaAtividadeForm
    success_url = reverse_lazy('listar_categorias')

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado.')
        return redirect('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = get_object_or_404(CategoriaAtividade, id=self.kwargs['categoria_id'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = get_object_or_404(CategoriaAtividade, id=self.kwargs['categoria_id'])
        context['edit'] = True
        return context

    def form_valid(self, form):
        categoria = get_object_or_404(CategoriaAtividade, id=self.kwargs['categoria_id'])
        form.save()
        messages.success(self.request, f'Categoria {categoria.nome} atualizada com sucesso!')
        return super().form_valid(form)


class ExcluirCategoriaView(LoginRequiredMixin, GestorRequiredMixin, TemplateView):
    template_name = 'atividades/excluir_categoria.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = get_object_or_404(CategoriaAtividade, id=self.kwargs['categoria_id'])
        return context

    def post(self, request, *args, **kwargs):
        categoria = get_object_or_404(CategoriaAtividade, id=self.kwargs['categoria_id'])
        categoria_nome = categoria.nome
        categoria.delete()
        messages.success(request, f'Categoria {categoria_nome} excluída com sucesso!')
        return redirect('listar_categorias')


class ListarCategoriasView(LoginRequiredMixin, GestorRequiredMixin, ListView):
    template_name = 'atividades/listar_categorias.html'
    context_object_name = 'categorias'

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado.')
        return redirect('dashboard')

    def get_queryset(self):
        return CategoriaAtividade.objects.all()


# Views de CategoriaCurso
class CriarCategoriaCursoView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'atividades/form_associar_categoria.html'
    form_class = CategoriaCursoForm
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        user = self.request.user
        coordenador = getattr(user, 'coordenador', None)
        return user.groups.filter(name='Gestor').exists() or coordenador

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado.')
        return redirect('dashboard')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        coordenador = getattr(user, 'coordenador', None)
        
        if coordenador:
            form.fields['curso'].queryset = Curso.objects.filter(id=coordenador.curso.id)
            form.fields['curso'].initial = coordenador.curso
            categorias_vinculadas = CursoCategoria.objects.filter(curso=coordenador.curso).values_list('categoria_id', flat=True)
            form.fields['categoria'].queryset = CategoriaAtividade.objects.exclude(id__in=categorias_vinculadas)
        
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['coordenador'] = getattr(self.request.user, 'coordenador', None)
        return context

    def form_valid(self, form):
        categoria = form.save()
        messages.success(self.request, f'Categoria {categoria.categoria.nome} associada a {categoria.curso.nome} com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, 'Erro ao associar categoria')
        return super().form_invalid(form)


class EditarCategoriaCursoView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'atividades/form_associar_categoria.html'
    form_class = CategoriaCursoForm
    success_url = reverse_lazy('listar_categorias')

    def test_func(self):
        user = self.request.user
        coordenador = getattr(user, 'coordenador', None)
        categoria = get_object_or_404(CursoCategoria, id=self.kwargs['categoria_id'])
        
        if user.groups.filter(name='Gestor').exists():
            return True
        elif coordenador:
            return coordenador.curso.id == categoria.curso.id
        else:
            return False

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado.')
        return redirect('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = get_object_or_404(CursoCategoria, id=self.kwargs['categoria_id'])
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        coordenador = getattr(user, 'coordenador', None)
        
        if coordenador:
            form.fields['curso'].queryset = Curso.objects.filter(id=coordenador.curso.id)
            form.fields['curso'].initial = coordenador.curso
        
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = get_object_or_404(CursoCategoria, id=self.kwargs['categoria_id'])
        context['edit'] = True
        context['coordenador'] = getattr(self.request.user, 'coordenador', None)
        return context

    def form_valid(self, form):
        categoria = get_object_or_404(CursoCategoria, id=self.kwargs['categoria_id'])
        form.save()
        messages.success(self.request, f'Categoria {categoria.categoria.nome} atualizada com sucesso!')
        return super().form_valid(form)


class ExcluirCategoriaCursoView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'atividades/excluir_categoria.html'

    def test_func(self):
        user = self.request.user
        coordenador = getattr(user, 'coordenador', None)
        categoria = get_object_or_404(CursoCategoria, id=self.kwargs['categoria_id'])
        
        if user.groups.filter(name='Gestor').exists():
            return True
        elif coordenador:
            return coordenador.curso.id == categoria.curso.id
        else:
            return False

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado.')
        return redirect('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = get_object_or_404(CursoCategoria, id=self.kwargs['categoria_id'])
        return context

    def post(self, request, *args, **kwargs):
        categoria = get_object_or_404(CursoCategoria, id=self.kwargs['categoria_id'])
        categoria_nome = categoria.categoria.nome
        categoria.delete()
        messages.success(request, f'Categoria {categoria_nome} desassociada com sucesso!')
        return redirect('listar_categorias_curso')


class ListarCategoriasCursoView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'atividades/listar_categorias_curso.html'
    context_object_name = 'categorias'

    def test_func(self):
        user = self.request.user
        coordenador = getattr(user, 'coordenador', None)
        return user.groups.filter(name='Gestor').exists() or coordenador

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado.')
        return redirect('dashboard')

    def get_queryset(self):
        user = self.request.user
        coordenador = getattr(user, 'coordenador', None)
        
        if coordenador:
            return CursoCategoria.objects.filter(curso=coordenador.curso)
        else:
            return CursoCategoria.objects.all()


# Views de Atividade
class CadastrarAtividadeView(LoginRequiredMixin, AlunoRequiredMixin, FormView):
    template_name = 'atividades/form_atividade.html'
    form_class = AtividadeForm

    def get_success_url(self):
        return reverse('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['aluno'] = self.request.user.aluno
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            try:
                categoria = CategoriaAtividade.objects.get(id=categoria_id)
                initial['categoria'] = categoria
            except CategoriaAtividade.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        atividade = form.save(commit=False)
        atividade.aluno = self.request.user.aluno
        atividade.save()
        messages.success(self.request, f'Atividade {atividade.nome} cadastrada com sucesso!')
        return super().form_valid(form)


class EditarAtividadeView(LoginRequiredMixin, AlunoRequiredMixin, FormView):
    template_name = 'atividades/form_atividade.html'
    form_class = AtividadeForm

    def get_success_url(self):
        return reverse('listar_atividades')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['aluno'] = self.request.user.aluno
        kwargs['instance'] = get_object_or_404(Atividade, id=self.kwargs['atividade_id'], aluno=self.request.user.aluno)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['atividade'] = get_object_or_404(Atividade, id=self.kwargs['atividade_id'], aluno=self.request.user.aluno)
        context['edit'] = True
        return context

    def form_valid(self, form):
        atividade = get_object_or_404(Atividade, id=self.kwargs['atividade_id'], aluno=self.request.user.aluno)
        form.save()
        messages.success(self.request, f'Atividade {atividade.nome} atualizada com sucesso!')
        return super().form_valid(form)


class ExcluirAtividadeView(LoginRequiredMixin, AlunoRequiredMixin, TemplateView):
    template_name = 'atividades/excluir_atividade.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['atividade'] = get_object_or_404(Atividade, id=self.kwargs['atividade_id'], aluno=self.request.user.aluno)
        return context

    def post(self, request, *args, **kwargs):
        atividade = get_object_or_404(Atividade, id=self.kwargs['atividade_id'], aluno=self.request.user.aluno)
        atividade_nome = atividade.nome
        atividade.delete()
        messages.success(request, f'Atividade {atividade_nome} excluída com sucesso!')
        return redirect('listar_atividades')


class ListarAtividadesView(LoginRequiredMixin, AlunoRequiredMixin, ListView):
    template_name = 'atividades/listar_atividades.html'
    context_object_name = 'atividades'

    def get_queryset(self):
        aluno = self.request.user.aluno
        queryset = Atividade.objects.filter(aluno=aluno)
        
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            try:
                categoria = CursoCategoria.objects.get(id=categoria_id)
                queryset = queryset.filter(categoria=categoria)
            except CursoCategoria.DoesNotExist:
                pass
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categoria_id = self.request.GET.get('categoria')
        categoria = None
        if categoria_id:
            try:
                categoria = CursoCategoria.objects.get(id=categoria_id)
            except CursoCategoria.DoesNotExist:
                pass
        context['categoria_filtrada'] = categoria
        return context


# Views de Usuário Admin
class CriarUsuarioAdminView(LoginRequiredMixin, GestorRequiredMixin, FormView):
    template_name = 'atividades/criar_usuario_admin.html'
    form_class = AdminUserForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
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
            Coordenador.objects.create(user=user, curso=curso)
        
        messages.success(self.request, 'Usuário criado com sucesso!')
        return super().form_valid(form)


class ListarUsuariosAdminView(LoginRequiredMixin, GestorRequiredMixin, TemplateView):
    template_name = 'atividades/listar_usuarios_admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gestores'] = User.objects.filter(groups__name='Gestor')
        context['coordenadores'] = User.objects.filter(groups__name='Coordenador')
        return context


# Esta view precisa continuar como função devido ao decorator @require_POST
@login_required
@require_POST
def ativar_desativar_usuario(request, user_id):
    if not request.user.groups.filter(name='Gestor').exists():
        return redirect('dashboard')
    
    user = User.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    if user.groups.filter(name='Coordenador').exists():
        return redirect('listar_usuarios_admin')
    return redirect('dashboard')


class CriarCategoriaCursoDiretaView(LoginRequiredMixin, CoordenadorRequiredMixin, FormView):
    template_name = 'atividades/form_categoria_curso_direta.html'
    form_class = CategoriaCursoDiretaForm
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['curso_nome'] = self.request.user.coordenador.curso.nome
        return context

    def form_valid(self, form):
        coordenador = self.request.user.coordenador
        curso_categoria = form.save(coordenador)
        messages.success(self.request, f'Categoria {curso_categoria.categoria.nome} criada e vinculada ao curso {curso_categoria.curso.nome}!')
        return super().form_valid(form)


class AssociarCategoriasAoCursoView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'atividades/form_associar_categorias.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        user = self.request.user
        coordenador = getattr(user, 'coordenador', None)
        return coordenador or user.groups.filter(name='Gestor').exists()

    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado.')
        return redirect('dashboard')

    def get_context_data(self, **kwargs):
        user = self.request.user
        coordenador = getattr(user, 'coordenador', None)
        
        curso = None
        cursos = None
        
        if coordenador:
            curso = coordenador.curso
        elif user.groups.filter(name='Gestor').exists():
            cursos = Curso.objects.all()
            if self.request.method == 'POST':
                curso_id = self.request.POST.get('curso_id')
                try:
                    curso = Curso.objects.get(id=curso_id)
                except Curso.DoesNotExist:
                    curso = None

        categorias_vinculadas = CursoCategoria.objects.filter(curso=curso).values_list('categoria_id', flat=True) if curso else []
        categorias_disponiveis = CategoriaAtividade.objects.exclude(id__in=categorias_vinculadas) if curso else []
        
        context = {
            'categorias': categorias_disponiveis,
            'curso_nome': curso.nome if curso else '',
            'cursos': cursos,
            'curso_selecionado': curso.id if curso else '',
            'curso_required': True if user.groups.filter(name='Gestor').exists() else False
        }
        
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        coordenador = getattr(user, 'coordenador', None)
        
        curso = None
        if coordenador:
            curso = coordenador.curso
        elif user.groups.filter(name='Gestor').exists():
            curso_id = request.POST.get('curso_id')
            try:
                curso = Curso.objects.get(id=curso_id)
            except Curso.DoesNotExist:
                curso = None
        else:
            messages.error(request, 'Acesso negado.')
            return redirect('dashboard')

        if not curso:
            messages.error(request, 'Curso não encontrado.')
            return redirect('dashboard')

        categorias_vinculadas = CursoCategoria.objects.filter(curso=curso).values_list('categoria_id', flat=True)
        categorias_disponiveis = CategoriaAtividade.objects.exclude(id__in=categorias_vinculadas)

        # Verifica se o POST tem apenas curso selecionado (sem categorias)
        tem_categoria = any(request.POST.get(f'cat_{categoria.id}') for categoria in categorias_disponiveis)
        if not tem_categoria:
            # Apenas curso selecionado, renderiza novamente com as categorias
            context = self.get_context_data()
            return self.render_to_response(context)

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