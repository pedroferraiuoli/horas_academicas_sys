from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib import messages
from ..utils import paginate_queryset

from ..forms import UserRegistrationForm, AlterarEmailForm, AdminUserForm
from ..selectors import AlunoSelectors, UserSelectors
from ..services import UserService
from ..filters import AlunosFilter, UsuarioFilter
from ..mixins import LoginRequiredMixin, GestorRequiredMixin, CoordenadorRequiredMixin


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

        filter_coord = UsuarioFilter(self.request.GET, queryset=coordenadores)
        coordenadores = filter_coord.qs

        coordenadores = paginate_queryset(qs=coordenadores, page=self.request.GET.get('page'), per_page=10)
        context['gestores'] = gestores
        context['coordenadores'] = coordenadores
        context['filter'] = filter_coord
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

        # Paginação
        paginator = Paginator(alunos_filtrados, 20)  # 20 alunos por página
        page = self.request.GET.get('page')
        
        try:
            alunos_paginados = paginator.page(page)
        except PageNotAnInteger:
            alunos_paginados = paginator.page(1)
        except EmptyPage:
            alunos_paginados = paginator.page(paginator.num_pages)

        context['curso'] = curso
        context['alunos'] = alunos_paginados
        context['filter'] = filtro
        return context


def ativar_desativar_usuario(request, user_id):
    if not UserSelectors.is_user_gestor(request.user):
        messages.warning(request, 'Acesso negado.')
        return redirect('login')
    UserService.toggle_user_active_status(user_id=user_id)
    return redirect('listar_usuarios_admin')
