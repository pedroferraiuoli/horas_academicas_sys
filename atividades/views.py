import logging
import os
from pathlib import Path
from django.views import View
from django.shortcuts import render, redirect
from atividades.selectors import AlunoSelectors, AtividadeSelectors, CursoCategoriaSelectors, SemestreSelectors, UserSelectors
from .forms import AdminUserForm, CategoriaCursoDiretaForm, UserRegistrationForm, AtividadeForm, SemestreForm, CategoriaAtividadeForm, CursoForm, AlterarEmailForm, CategoriaCursoForm
from .models import Aluno, Atividade, Curso, CategoriaAtividade, CursoCategoria, Semestre
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .filters import AlunosFilter, AtividadesFilter, CursoCategoriaFilter
from django.views.generic import TemplateView
from .services import AtividadeService, CursoCategoriaService, UserService, SemestreService
from .mixins import AlunoRequiredMixin, CoordenadorRequiredMixin, GestorRequiredMixin, GestorOuCoordenadorRequiredMixin, LoginRequiredMixin
from django.conf import settings

# Loggers para operações críticas
business_logger = logging.getLogger('atividades.business')
security_logger = logging.getLogger('atividades.security')

class CriarCursoView(GestorRequiredMixin, View):
    template_name = 'forms/form_curso.html'

    def get(self, request):
        form = CursoForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CursoForm(request.POST)
        if form.is_valid():
            curso_instance = form.save()
            business_logger.warning(f"CURSO CRIADO: {curso_instance.nome} | User: {request.user.username}")
            messages.success(request, f'Curso {curso_instance.nome} criado com sucesso!')
            return redirect('dashboard')
        
        return render(request, self.template_name, {'form': form})

class EditarCursoView(GestorRequiredMixin, View):
    template_name = 'forms/form_curso.html'

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
            business_logger.warning(f"CURSO EDITADO: {self.curso.nome} | User: {request.user.username}")
            messages.success(request, f'Curso {self.curso.nome} atualizado com sucesso!')
            return redirect('listar_cursos')
            
        return render(request, self.template_name, {'form': form, 'curso': self.curso, 'edit': True})

class ExcluirCursoView(GestorRequiredMixin, View):
    template_name = 'excluir/excluir_curso.html'

    def dispatch(self, request, curso_id, *args, **kwargs):
        self.curso = get_object_or_404(Curso, id=curso_id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'curso': self.curso})

    def post(self, request):
        curso_nome = self.curso.nome
        self.curso.delete()
        business_logger.warning(f"CURSO EXCLUÍDO: {curso_nome} | User: {request.user.username}")
        messages.success(request, f'Curso {curso_nome} excluído com sucesso!')
        return redirect('listar_cursos')

class ListarCursosView(GestorRequiredMixin, TemplateView):
    template_name = 'listas/listar_cursos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cursos'] = Curso.objects.all()
        return context

class CriarSemestreView(GestorRequiredMixin, View):
    template_name = 'forms/form_semestre.html'

    def get(self, request):
        form = SemestreForm()
        semestres = Semestre.objects.all()
        return render(request, self.template_name, {'form': form, 'semestres': semestres})

    def post(self, request):
        form = SemestreForm(request.POST)
        if form.is_valid():
            semestre = form.save()
            SemestreService.criar_semestre_com_copia(form=semestre, copiar_de_id=request.POST.get('copiar_de'))
            business_logger.warning(f"SEMESTRE CRIADO: {semestre.nome} | User: {request.user.username}")
            messages.success(request, f'Semestre {semestre.nome} criado com sucesso!')
            return redirect('dashboard')
        
        messages.warning(request, 'Por favor, corrija os erros abaixo.')
        semestres = Semestre.objects.all()
        return render(request, self.template_name, {'form': form, 'semestres': semestres})

class EditarSemestreView(GestorRequiredMixin, View):
    template_name = 'forms/form_semestre.html'

    def get(self, request, semestre_id):
        semestre = get_object_or_404(Semestre, id=semestre_id)
        form = SemestreForm(instance=semestre)
        return render(request, self.template_name, {'form': form, 'semestre': semestre, 'edit': True})

    def post(self, request, semestre_id):
        semestre = get_object_or_404(Semestre, id=semestre_id)
        form = SemestreForm(request.POST, instance=semestre)
        if form.is_valid():
            semestre = form.save()
            business_logger.warning(f"SEMESTRE EDITADO: {semestre.nome} | User: {request.user.username}")
            messages.success(request, f'Semestre {semestre.nome} atualizado com sucesso!')
            return redirect('listar_semestres')
        
        return render(request, self.template_name, {'form': form, 'semestre': semestre, 'edit': True})
    
class ExcluirSemestreView(GestorRequiredMixin, View):
    template_name = 'excluir/excluir_semestre.html'

    def dispatch(self, request, semestre_id, *args, **kwargs):
        self.semestre = get_object_or_404(Semestre, id=semestre_id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'semestre': self.semestre})

    def post(self, request):
        semestre_nome = self.semestre.nome
        self.semestre.delete()
        business_logger.warning(f"SEMESTRE EXCLUÍDO: {semestre_nome} | User: {request.user.username}")
        messages.success(request, f'Semestre {semestre_nome} excluído com sucesso!')
        return redirect('listar_semestres')
    
class ListarSemestresView(GestorRequiredMixin, TemplateView):
    template_name = 'listas/listar_semestres.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['semestres'] = Semestre.objects.all()
        return context

class CriarCategoriaView(GestorRequiredMixin, View):
    template_name = 'forms/form_categoria.html'

    def get(self, request):
        form = CategoriaAtividadeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CategoriaAtividadeForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            business_logger.warning(f"CATEGORIA CRIADA: {categoria.nome} | User: {request.user.username}")
            messages.success(request, f'Categoria {categoria.nome} criada com sucesso!')
            return redirect('dashboard')
        
        return render(request, self.template_name, {'form': form})

class EditarCategoriaView(GestorRequiredMixin, View):
    template_name = 'forms/form_categoria.html'

    def get(self, request, categoria_id):
        categoria = get_object_or_404(CategoriaAtividade, id=categoria_id)
        form = CategoriaAtividadeForm(instance=categoria)
        return render(request, self.template_name, {'form': form, 'categoria': categoria, 'edit': True})

    def post(self, request, categoria_id):
        categoria = get_object_or_404(CategoriaAtividade, id=categoria_id)
        form = CategoriaAtividadeForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            business_logger.warning(f"CATEGORIA EDITADA: {categoria.nome} | User: {request.user.username}")
            messages.success(request, f'Categoria {categoria.nome} atualizada com sucesso!')
            return redirect('listar_categorias')
        
        return render(request, self.template_name, {'form': form, 'categoria': categoria, 'edit': True})
    
class ExcluirCategoriaView(GestorRequiredMixin, View):
    template_name = 'excluir/excluir_categoria.html'

    def dispatch(self, request, categoria_id, *args, **kwargs):
        self.categoria = get_object_or_404(CategoriaAtividade, id=categoria_id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'categoria': self.categoria})

    def post(self, request):
        categoria_nome = self.categoria.nome
        self.categoria.delete()
        business_logger.warning(f"CATEGORIA EXCLUÍDA: {categoria_nome} | User: {request.user.username}")
        messages.success(request, f'Categoria {categoria_nome} excluída com sucesso!')
        return redirect('listar_categorias')

class ListarCategoriasView(GestorRequiredMixin, TemplateView):
    template_name = 'listas/listar_categorias.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaAtividade.objects.all()
        return context
    
class CriarCategoriaCursoView(GestorOuCoordenadorRequiredMixin, View):
    template_name = 'forms/form_associar_categoria.html'

    def get(self, request):
        coordenador = UserSelectors.get_coordenador_by_user(request.user)
        form = CategoriaCursoForm(user=request.user)
        return render(request, self.template_name, {'form': form, 'coordenador': coordenador})

    def post(self, request):
        coordenador = UserSelectors.get_coordenador_by_user(request.user)
        form = CategoriaCursoForm(request.POST, user=request.user)
        if form.is_valid():
            categoria = form.save()
            business_logger.warning(
                f"CURSO-CATEGORIA CRIADA: {categoria.categoria.nome} -> {categoria.curso.nome} | "
                f"User: {request.user.username}"
            )
            messages.success(request, f'Categoria {categoria.categoria.nome} associada a {categoria.curso.nome} com sucesso!')
            return redirect('dashboard')

        return render(request, self.template_name, {'form': form, 'coordenador': coordenador})
    
class EditarCategoriaCursoView(GestorOuCoordenadorRequiredMixin, View):
    template_name = 'forms/form_associar_categoria.html'

    def dispatch(self, request, categoria_id, *args, **kwargs):
        self.categoria = get_object_or_404(CursoCategoria, id=categoria_id)
        self.coordenador = UserSelectors.get_coordenador_by_user(request.user)
        if self.coordenador and self.coordenador.curso.id != self.categoria.curso.id:
            security_logger.warning(
                f"ACESSO NEGADO: Coordenador {request.user.username} ({self.coordenador.curso.nome}) "
                f"tentou editar categoria do curso {self.categoria.curso.nome}"
            )
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
            business_logger.warning(
                f"CURSO-CATEGORIA EDITADA: {self.categoria.categoria.nome} -> {self.categoria.curso.nome} | "
                f"User: {request.user.username}"
            )
            messages.success(request, f'Categoria {self.categoria.categoria.nome} atualizada com sucesso!')
            return redirect('listar_categorias')
        
        return render(request, self.template_name, {'form': form, 'categoria': self.categoria, 'edit': True, 'coordenador': self.coordenador})

class ExcluirCategoriaCursoView(GestorOuCoordenadorRequiredMixin, View):
    template_name = 'excluir/excluir_categoria.html'

    def dispatch(self, request, categoria_id, *args, **kwargs):
        self.categoria = get_object_or_404(CursoCategoria, id=categoria_id)
        self.coordenador = UserSelectors.get_coordenador_by_user(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        if self.coordenador and self.coordenador.curso.id != self.categoria.curso.id:
            security_logger.warning(
                f"ACESSO NEGADO: Coordenador {request.user.username} ({self.coordenador.curso.nome}) "
                f"tentou acessar categoria do curso {self.categoria.curso.nome}"
            )
            messages.warning(request, 'Acesso negado.')
            return redirect('dashboard')
        return render(request, self.template_name, {'categoria': self.categoria})

    def post(self, request):
        if self.coordenador and self.coordenador.curso.id != self.categoria.curso.id:
            security_logger.warning(
                f"ACESSO NEGADO: Coordenador {request.user.username} ({self.coordenador.curso.nome}) "
                f"tentou excluir categoria do curso {self.categoria.curso.nome}"
            )
            messages.warning(request, 'Acesso negado.')
            return redirect('dashboard')
        
        cat_nome = self.categoria.categoria.nome
        curso_nome = self.categoria.curso.nome
        self.categoria.delete()
        business_logger.warning(
            f"CURSO-CATEGORIA EXCLUÍDA: {cat_nome} -> {curso_nome} | User: {request.user.username}"
        )
        messages.success(request, f'Categoria {cat_nome} desassociada com sucesso!')
        return redirect('listar_categorias_curso')

class ListarCategoriasCursoView(GestorOuCoordenadorRequiredMixin, TemplateView):
    template_name = 'listas/listar_categorias_curso.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_qs = CursoCategoriaSelectors.get_curso_categorias_usuario(self.request.user)

        filtro = CursoCategoriaFilter(self.request.GET or None, queryset=base_qs)
        categorias = filtro.qs

        context['categorias'] = categorias
        context['filter'] = filtro
        return context

class CadastrarAtividadeView(AlunoRequiredMixin, View):
    template_name = 'forms/form_atividade.html'

    def dispatch(self, request, *args, **kwargs):
        self.aluno = AlunoSelectors.get_aluno_by_user(request.user)
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
    template_name = 'forms/form_atividade.html'

    def dispatch(self, request, atividade_id, *args, **kwargs):
        self.aluno = AlunoSelectors.get_aluno_by_user(request.user)
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
    template_name = 'excluir/excluir_atividade.html'

    def dispatch(self, request, atividade_id, *args, **kwargs):
        self.aluno = AlunoSelectors.get_aluno_by_user(request.user)
        self.atividade = get_object_or_404(Atividade, id=atividade_id, aluno=self.aluno)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'atividade': self.atividade})

    def post(self, request):
        self.atividade.delete()
        messages.success(request, f'Atividade {self.atividade.nome} excluída com sucesso!')
        return redirect('listar_atividades')

class ListarAtividadesView(AlunoRequiredMixin, TemplateView):
    template_name = 'listas/listar_atividades.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aluno = AlunoSelectors.get_aluno_by_user(self.request.user)
        atividades = AtividadeSelectors.get_atividades_aluno(aluno)
        filtro = AtividadesFilter(self.request.GET or None, queryset=atividades, request=self.request)
        atividades_filtradas = filtro.qs
        context['atividades'] = atividades_filtradas
        context['filter'] = filtro
        return context

class DashboardView(LoginRequiredMixin, TemplateView):

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if UserSelectors.is_user_aluno(user):
            self.dashboard_type = 'aluno'
            self.template_name = 'dashboards/dashboard.html'
        elif UserSelectors.is_user_coordenador(user):
            self.dashboard_type = 'coordenador'
            self.template_name = 'dashboards/dashboard_gestor.html'
        elif UserSelectors.is_user_gestor(user):
            self.dashboard_type = 'gestor'
            self.template_name = 'dashboards/dashboard_gestor.html'

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

        total_horas = aluno.horas_complementares_validas(apenas_aprovadas=True)
        horas_requeridas = aluno.curso.horas_requeridas if aluno.curso else 0

        progresso = 0
        if horas_requeridas > 0:
            progresso = min(100, round((total_horas / horas_requeridas) * 100))

        atividades_recentes = AtividadeSelectors.get_atividades_recentes_aluno(aluno, limite=5)

        ultrapassou_limite = False
        if aluno.curso:
            categorias = CursoCategoriaSelectors.get_curso_categorias_por_curso(aluno.curso)
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
        grupo = UserSelectors.get_user_primary_group(user)
        semestre_atual = SemestreSelectors.get_semestre_atual()

        stats = {}

        if grupo == 'Coordenador':
            coordenador = getattr(user, 'coordenador', None)
            if coordenador:
                curso = coordenador.curso
                alunos = AlunoSelectors.get_num_alunos_por_curso(curso)
                alunos_com_pendencias = AlunoSelectors.get_num_alunos_com_pendencias_por_curso(curso)
                atividades_pendentes = AtividadeSelectors.get_num_atividades_pendentes_curso(curso)
                stats = {
                    'num_alunos': alunos,
                    'alunos_com_pendencias':alunos_com_pendencias,
                    'atividades_pendentes': atividades_pendentes,
                }

        return {
            'grupo': grupo,
            'stats': stats,
            'semestre_atual': semestre_atual,
        }
    
class RegisterView(View):
    template_name = 'auth/register.html'

    def get(self, request):
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            UserService.register_user_with_aluno(form=form)
            messages.success(request, 'Registro realizado com sucesso!')
            return redirect('login')
        return render(request, self.template_name, {'form': form})
    
class AlterarEmailView(LoginRequiredMixin, View):
    template_name = 'auth/alterar_email.html'

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
    template_name = 'auth/criar_usuario_admin.html'

    def get(self, request):
        form = AdminUserForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AdminUserForm(request.POST)
        if form.is_valid():
            UserService.criar_usuario_admin(form=form)
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})
    
class ListarUsuariosAdminView(GestorRequiredMixin, TemplateView):
    template_name = 'listas/listar_usuarios_admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gestores = UserSelectors.get_gestor_users()
        coordenadores = UserSelectors.get_coordenador_users()
        context['gestores'] = gestores
        context['coordenadores'] = coordenadores
        return context
    
class ListarAlunosCoordenadorView(CoordenadorRequiredMixin, TemplateView):
    template_name = 'listas/listar_alunos_coordenador.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        coordenador = UserSelectors.get_coordenador_by_user(user)
        curso = coordenador.curso

        alunos_base = AlunoSelectors.get_alunos_por_curso_order_by_pendencia(curso)

        filtro = AlunosFilter(self.request.GET, queryset=alunos_base)
        alunos_filtrados = filtro.qs

        context['curso'] = curso
        context['alunos'] = alunos_filtrados
        context['filter'] = filtro
        return context
    
class ListarAtividadesCoordenadorView(CoordenadorRequiredMixin, TemplateView):
    template_name = 'listas/listar_atividades_coordenador.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        coordenador = UserSelectors.get_coordenador_by_user(user)
        curso = coordenador.curso
        aluno_id = self.request.GET.get('aluno_id', None)

        if aluno_id:
            aluno = get_object_or_404(Aluno, id=aluno_id, curso=coordenador.curso)
            atividades = AtividadeSelectors.get_atividades_aluno(aluno)
        else: 
            atividades = AtividadeSelectors.get_atividades_pendentes_curso(curso)

        filtro = AtividadesFilter(self.request.GET, queryset=atividades, request=self.request)
        atividades_filtradas = filtro.qs

        context['aluno'] = aluno if aluno_id else None
        context['atividades'] = atividades_filtradas
        context['filter'] = filtro
        return context
    
class AprovarHorasAtividadeView(CoordenadorRequiredMixin, View):
    def dispatch(self, request, atividade_id, *args, **kwargs):
        self.coordenador = UserSelectors.get_coordenador_by_user(request.user)
        self.atividade = get_object_or_404(Atividade, id=atividade_id)
        if self.atividade.aluno.curso != self.coordenador.curso:
            messages.warning(request, 'Acesso negado à atividade deste aluno.')
            return redirect('dashboard')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'atividade': self.atividade})

    def post(self, request):
        horas_aprovadas = request.POST.get('horas_aprovadas')
        try:
            horas_aprovadas = int(horas_aprovadas)
            AtividadeService.aprovar_horas(atividade=self.atividade, horas_aprovadas=horas_aprovadas)
        except ValueError as e:
            messages.warning(request, str(e))
            return redirect('listar_atividades_coordenador')

        messages.success(request, f'Atividade {self.atividade.nome} aprovada com {horas_aprovadas} horas!')
        return redirect('listar_atividades_coordenador')

def ativar_desativar_usuario(request, user_id):
    if not UserSelectors.is_user_gestor(request.user):
        messages.warning(request, 'Acesso negado.')
        return redirect('login')
    UserService.toggle_user_active_status(user_id=user_id)
    return redirect('listar_usuarios_admin')

class CriarCategoriaCursoDiretaView(CoordenadorRequiredMixin, View):
    template_name = 'forms/form_categoria_curso_direta.html'

    def get(self, request):
        coordenador = UserSelectors.get_coordenador_by_user(request.user)
        form = CategoriaCursoDiretaForm()
        return render(request, self.template_name, {'form': form, 'curso_nome': coordenador.curso.nome})

    def post(self, request):
        coordenador = UserSelectors.get_coordenador_by_user(request.user)
        form = CategoriaCursoDiretaForm(request.POST)
        if form.is_valid():
            curso_categoria = form.save()
            CursoCategoriaService.create_categoria_curso(form=form, coordenador=coordenador)
            messages.success(request, f'Categoria {curso_categoria.categoria.nome} criada e vinculada ao curso {curso_categoria.curso.nome}!')
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form, 'curso_nome': coordenador.curso.nome})
    
class AssociarCategoriasCursoView(GestorOuCoordenadorRequiredMixin, View):
    template_name = 'forms/form_associar_categorias.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        self.coordenador = UserSelectors.get_coordenador_by_user(user)
        self.cursos = Curso.objects.all() if UserSelectors.is_user_gestor(user) else None
        self.curso = self.coordenador.curso if self.coordenador else None
        self.semestres = Semestre.objects.all()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, self.get_context())

    def post(self, request):
        if not self.curso:
            self.curso = get_object_or_404(Curso, id=request.POST.get('curso_id'))

        semestre = get_object_or_404(Semestre, id=request.POST.get('semestre_id'))

        try:
            adicionadas = CursoCategoriaService.associar_categorias(
                curso=self.curso,
                semestre=semestre,
                dados_post=request.POST
            )
        except ValueError as e:
            messages.warning(request, str(e))
            return render(request, self.template_name, self.get_context(
                curso=self.curso,
                semestre=semestre
            ))

        messages.success(request, f'{adicionadas} categoria(s) associada(s) ao curso!')
        return redirect('dashboard')
    
    def get_context(self, curso=None, semestre=None):
        curso = curso or self.curso

        categorias = []
        if curso and semestre:
            categorias = CursoCategoriaSelectors.get_curso_categorias_disponiveis_para_associar(semestre=semestre, curso=curso)

        return {
            'categorias': categorias,
            'curso_nome': curso.nome if curso else '',
            'curso_selecionado': curso.id if curso else '',
            'curso_required': self.cursos is not None,
            'cursos': self.cursos,
            'semestres': self.semestres,
            'semestre_selecionado': semestre.id if semestre else '',
        }
    
class VisualizarLogsView(GestorRequiredMixin, TemplateView):
    template_name = "atividades/visualizar_logs.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Define qual arquivo de log visualizar
        log_type = self.request.GET.get("tipo", "errors")
        num_lines = int(self.request.GET.get("linhas", 100))
        
        # Mapeia tipos para arquivos
        log_files = {
            "errors": "errors.log",
            "business": "business.log",
            "security": "security.log",
        }
        
        log_filename = log_files.get(log_type, "errors.log")
        log_path = Path(settings.BASE_DIR) / "logs" / log_filename
        
        log_content = []
        file_exists = False
        
        if log_path.exists():
            file_exists = True
            try:
                # Lê as últimas N linhas do arquivo
                with open(log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    # Pega as últimas N linhas
                    log_content = lines[-num_lines:] if len(lines) > num_lines else lines
                    # Inverte para mostrar as mais recentes primeiro
                    log_content.reverse()
            except Exception as e:
                log_content = [f"Erro ao ler arquivo de log: {str(e)}"]
        
        # Informações do arquivo
        file_size = 0
        if file_exists:
            file_size = log_path.stat().st_size / 1024  # KB
        
        context.update({
            "log_type": log_type,
            "log_content": log_content,
            "file_exists": file_exists,
            "file_size": round(file_size, 2),
            "num_lines": num_lines,
            "log_types": [
                {"value": "errors", "label": "Erros do Sistema"},
                {"value": "business", "label": "Operações Críticas"},
                {"value": "security", "label": "Segurança"},
            ],
        })
        
        return context