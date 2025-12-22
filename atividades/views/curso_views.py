import logging
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib import messages

from atividades.filters import CursoFilter
from ..utils import paginate_queryset

from atividades.selectors import CursoSelectors, SemestreSelectors

from ..models import Curso
from ..forms import CursoForm
from ..mixins import GestorRequiredMixin

business_logger = logging.getLogger('atividades.business')


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
    htmx_template_name = 'listas/htmx/cursos_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cursos = CursoSelectors.listar_cursos_com_categorias_semestre_atual()
  
        filter = CursoFilter(self.request.GET, queryset=cursos, user=self.request.user)
        cursos = filter.qs

        cursos_paginados = paginate_queryset(qs=cursos, page=self.request.GET.get('page'), per_page=15)

        context['cursos'] = cursos_paginados
        context['semestre_atual'] = SemestreSelectors.get_semestre_atual()
        context['filter'] = filter
        
        return context
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return [self.htmx_template_name]
        return [self.template_name]
