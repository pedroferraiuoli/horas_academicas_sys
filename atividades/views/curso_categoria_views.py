import logging
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib import messages
from ..models import Curso, CategoriaCurso, Semestre
from ..forms import CategoriaCursoForm, CategoriaCursoDiretaForm
from ..selectors import CategoriaCursoSelectors, UserSelectors
from ..services import CategoriaCursoService
from ..filters import CategoriaCursoFilter
from ..mixins import GestorOuCoordenadorRequiredMixin, CoordenadorRequiredMixin

business_logger = logging.getLogger('atividades.business')
security_logger = logging.getLogger('atividades.security')


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
        self.categoria = get_object_or_404(CategoriaCurso, id=categoria_id)
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
        self.categoria = get_object_or_404(CategoriaCurso, id=categoria_id)
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
        base_qs = CategoriaCursoSelectors.get_categorias_curso_usuario(self.request.user)

        filtro = CategoriaCursoFilter(self.request.GET or None, queryset=base_qs)
        categorias = filtro.qs

        context['categorias'] = categorias
        context['filter'] = filtro
        return context


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
            CategoriaCursoService.create_categoria_curso(form=form, coordenador=coordenador)
            business_logger.warning(
                f"CURSO-CATEGORIA CRIADA DIRETAMENTE: {curso_categoria.categoria.nome} -> {curso_categoria.curso.nome} | "
                f"User: {request.user.username}"
            )
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
            adicionadas = CategoriaCursoService.associar_categorias(
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

        business_logger.warning(
            f"CURSO-CATEGORIAS ASSOCIADAS: {adicionadas} categoria(s) ao curso {self.curso.nome} "
            f"para o semestre {semestre.nome} | User: {request.user.username}"
        )
        messages.success(request, f'{adicionadas} categoria(s) associada(s) ao curso!')
        return redirect('dashboard')
    
    def get_context(self, curso=None, semestre=None):
        curso = curso or self.curso

        categorias = []
        if curso and semestre:
            categorias = CategoriaCursoSelectors.get_categorias_curso_disponiveis_para_associar(semestre=semestre, curso=curso)

        return {
            'categorias': categorias,
            'curso_nome': curso.nome if curso else '',
            'curso_selecionado': curso.id if curso else '',
            'curso_required': self.cursos is not None,
            'cursos': self.cursos,
            'semestres': self.semestres,
            'semestre_selecionado': semestre.id if semestre else '',
        }
