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
from ..mixins import GestorOuCoordenadorRequiredMixin
from ..utils import paginate_queryset

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
                f"CURSO-CATEGORIA CRIADA: {categoria.categoria.nome} -> {categoria.curso_semestre.curso.nome} | "
                f"User: {request.user.username}"
            )
            messages.success(request, f'Categoria {categoria.categoria.nome} associada a {categoria.curso_semestre.curso.nome} com sucesso!')
            return redirect('dashboard')

        return render(request, self.template_name, {'form': form, 'coordenador': coordenador})


class EditarCategoriaCursoView(GestorOuCoordenadorRequiredMixin, View):
    template_name = 'forms/form_associar_categoria.html'

    def dispatch(self, request, categoria_id, *args, **kwargs):
        self.categoria = get_object_or_404(CategoriaCurso, id=categoria_id)
        self.coordenador = UserSelectors.get_coordenador_by_user(request.user)
        if self.coordenador and self.coordenador.curso.id != self.categoria.curso_semestre.curso.id:
            security_logger.warning(
                f"ACESSO NEGADO: Coordenador {request.user.username} ({self.coordenador.curso.nome}) "
                f"tentou editar categoria do curso {self.categoria.curso_semestre.curso.nome}"
            )
            messages.warning(request, 'Acesso negado.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = CategoriaCursoForm(instance=self.categoria)
        return render(request, self.template_name, {'form': form, 'categoria': self.categoria, 'edit': True, 'coordenador': self.coordenador})
    
    def post(self, request):
        next_url = request.GET.get('next') or request.META.get('PATH_INFO')
        form = CategoriaCursoForm(request.POST, instance=self.categoria)
        if form.is_valid():
            form.save()
            business_logger.warning(
                f"CURSO-CATEGORIA EDITADA: {self.categoria.categoria.nome} -> {self.categoria.curso_semestre.curso.nome} | "
                f"User: {request.user.username}"
            )
            messages.success(request, f'Categoria {self.categoria.categoria.nome} atualizada com sucesso!')
            return redirect(next_url, 'listar_categorias_curso')
        
        return render(request, self.template_name, {'form': form, 'categoria': self.categoria, 'edit': True, 'coordenador': self.coordenador})


class ExcluirCategoriaCursoView(GestorOuCoordenadorRequiredMixin, View):
    template_name = 'excluir/excluir_generic.html'

    def dispatch(self, request, categoria_id, *args, **kwargs):
        self.categoria = get_object_or_404(CategoriaCurso, id=categoria_id)
        self.coordenador = UserSelectors.get_coordenador_by_user(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        if self.coordenador and self.coordenador.curso.id != self.categoria.curso_semestre.curso.id:
            security_logger.warning(
                f"ACESSO NEGADO: Coordenador {request.user.username} ({self.coordenador.curso.nome}) "
                f"tentou acessar categoria do curso {self.categoria.curso_semestre.curso.nome}"
            )
            messages.warning(request, 'Acesso negado.')
            return redirect('dashboard')
        tipo_exclusao = "Categoria do Curso"
        nome_exclusao = f"{self.categoria.categoria.nome} -> {self.categoria.curso_semestre.curso.nome} ({self.categoria.curso_semestre.semestre.nome})"
        return render(request, self.template_name, {'tipo_exclusao': tipo_exclusao, 'nome_exclusao': nome_exclusao})

    def post(self, request):
        if self.coordenador and self.coordenador.curso.id != self.categoria.curso_semestre.curso.id:
            security_logger.warning(
                f"ACESSO NEGADO: Coordenador {request.user.username} ({self.coordenador.curso.nome}) "
                f"tentou excluir categoria do curso {self.categoria.curso_semestre .curso.nome}"
            )
            messages.warning(request, 'Acesso negado.')
            return redirect('dashboard')
        
        cat_nome = self.categoria.categoria.nome
        curso_nome = self.categoria.curso_semestre.curso.nome
        self.categoria.delete()
        business_logger.warning(
            f"CURSO-CATEGORIA EXCLUÍDA: {cat_nome} -> {curso_nome} | User: {request.user.username}"
        )
        messages.success(request, f'Categoria {cat_nome} desassociada com sucesso!')
        return redirect('listar_categorias_curso')


class ListarCategoriasCursoView(GestorOuCoordenadorRequiredMixin, TemplateView):
    template_name = 'listas/listar_categorias_curso.html'
    htmx_template_name = 'listas/htmx/categorias_curso_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_qs = CategoriaCursoSelectors.get_categorias_curso_usuario(self.request.user)

        filtro = CategoriaCursoFilter(self.request.GET or None, queryset=base_qs, user=self.request.user)
        categorias = filtro.qs

        context['categorias'] = paginate_queryset(qs=categorias, page=self.request.GET.get('page'), per_page=15)
        context['filter'] = filtro
        return context
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return [self.htmx_template_name]
        return [self.template_name]


class CriarCategoriaCursoDiretaView(GestorOuCoordenadorRequiredMixin, View):
    template_name = 'forms/form_categoria_curso_direta.html'

    def get(self, request):
        form = CategoriaCursoDiretaForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CategoriaCursoDiretaForm(request.POST, user=request.user)
        if form.is_valid():
            categoria_curso = CategoriaCursoService.create_categoria_curso_especifica(form=form, user=request.user)
            business_logger.warning(
                f"CURSO-CATEGORIA CRIADA ESPECIFICAMENTE: {categoria_curso.categoria.nome} -> {categoria_curso.curso_semestre.curso.nome} | "
                f"User: {request.user.username}"
            )
            messages.success(request, f'Categoria {categoria_curso.categoria.nome} criada e vinculada ao curso {categoria_curso.curso_semestre.curso.nome}!')
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})


class AssociarCategoriasCursoView(GestorOuCoordenadorRequiredMixin, View):
    template_name = 'forms/form_associar_categorias.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        self.coordenador = UserSelectors.get_coordenador_by_user(user)
        self.is_gestor = UserSelectors.is_user_gestor(user)
        
        # Gestor pode escolher qualquer curso; Coordenador tem curso fixo
        if self.is_gestor:
            self.cursos = Curso.objects.all().order_by('nome')
            self.curso_fixo = None
        else:
            self.cursos = None
            self.curso_fixo = self.coordenador.curso if self.coordenador else None
        
        self.semestres = Semestre.objects.all().order_by('-data_inicio')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # Pegar curso e semestre da query string (para atualização dinâmica)
        curso_id = request.GET.get('curso_id')
        semestre_id = request.GET.get('semestre_id')
        
        curso_selecionado = None
        semestre_selecionado = None
        
        if curso_id:
            curso_selecionado = get_object_or_404(Curso, id=curso_id)
            # Se é coordenador, validar que é o curso dele
            if self.coordenador and curso_selecionado != self.coordenador.curso:
                curso_selecionado = self.coordenador.curso
        elif self.curso_fixo:
            curso_selecionado = self.curso_fixo
            
        if semestre_id:
            semestre_selecionado = get_object_or_404(Semestre, id=semestre_id)
        
        return render(request, self.template_name, self.get_context(
            curso=curso_selecionado,
            semestre=semestre_selecionado
        ))

    def post(self, request):
        # Determinar o curso
        if self.curso_fixo:
            curso = self.curso_fixo
        else:
            curso_id = request.POST.get('curso_id')
            if not curso_id:
                messages.error(request, 'Selecione um curso.')
                return render(request, self.template_name, self.get_context())
            try:
                curso = Curso.objects.get(id=curso_id)
            except Curso.DoesNotExist:
                messages.error(request, 'Curso inválido.')
                return render(request, self.template_name, self.get_context())
        
        # Determinar o semestre
        semestre_id = request.POST.get('semestre_id')
        if not semestre_id:
            messages.error(request, 'Selecione um semestre.')
            return render(request, self.template_name, self.get_context(curso=curso))
        
        try:
            semestre = Semestre.objects.get(id=semestre_id)
        except Semestre.DoesNotExist:
            messages.error(request, 'Semestre inválido.')
            return render(request, self.template_name, self.get_context(curso=curso))

        # Tentar associar as categorias
        try:
            adicionadas = CategoriaCursoService.associar_categorias(
                curso=curso,
                semestre=semestre,
                dados_post=request.POST
            )
            
            business_logger.warning(
                f"CURSO-CATEGORIAS ASSOCIADAS: {adicionadas} categoria(s) ao curso {curso.nome} "
                f"para o semestre {semestre.nome} | User: {request.user.username}"
            )
            messages.success(request, f'{adicionadas} categoria(s) associada(s) ao curso com sucesso!')
            return redirect('listar_categorias_curso')
            
        except ValueError as e:
            messages.warning(request, str(e))
            return render(request, self.template_name, self.get_context(
                curso=curso,
                semestre=semestre
            ))
    
    def get_context(self, curso=None, semestre=None):
        categorias = []
        
        # Buscar categorias disponíveis apenas se curso E semestre estiverem selecionados
        if curso and semestre:
            categorias = CategoriaCursoSelectors.get_categorias_curso_disponiveis_para_associar(
                curso=curso, 
                semestre=semestre
            )

        return {
            'categorias': categorias,
            'curso_nome': curso.nome if curso else '',
            'curso_selecionado': curso.id if curso else '',
            'semestre_selecionado': semestre.id if semestre else '',
            'cursos': self.cursos,
            'semestres': self.semestres,
            'is_gestor': self.is_gestor,
        }
