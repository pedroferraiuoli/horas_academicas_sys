import logging
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib import messages

from atividades.filters import CategoriaFilter
from ..utils import paginate_queryset

from atividades.selectors import CategoriaSelectors, SemestreSelectors

from ..models import Categoria
from ..forms import CategoriaForm
from ..mixins import GestorRequiredMixin

business_logger = logging.getLogger('atividades.business')


class CriarCategoriaView(GestorRequiredMixin, View):
    template_name = 'forms/form_categoria.html'

    def get(self, request):
        form = CategoriaForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            business_logger.warning(f"CATEGORIA CRIADA: {categoria.nome} | User: {request.user.username}")
            messages.success(request, f'Categoria {categoria.nome} criada com sucesso!')
            return redirect('dashboard')
        
        return render(request, self.template_name, {'form': form})


class EditarCategoriaView(GestorRequiredMixin, View):
    template_name = 'forms/form_categoria.html'

    def get(self, request, categoria_id):
        categoria = get_object_or_404(Categoria, id=categoria_id)
        form = CategoriaForm(instance=categoria)
        return render(request, self.template_name, {'form': form, 'categoria': categoria, 'edit': True})

    def post(self, request, categoria_id):
        categoria = get_object_or_404(Categoria, id=categoria_id)
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            business_logger.warning(f"CATEGORIA EDITADA: {categoria.nome} | User: {request.user.username}")
            messages.success(request, f'Categoria {categoria.nome} atualizada com sucesso!')
            return redirect('listar_categorias')
        
        return render(request, self.template_name, {'form': form, 'categoria': categoria, 'edit': True})


class ExcluirCategoriaView(GestorRequiredMixin, View):
    template_name = 'excluir/excluir_categoria.html'

    def dispatch(self, request, categoria_id, *args, **kwargs):
        self.categoria = get_object_or_404(Categoria, id=categoria_id)
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
        
        categorias = CategoriaSelectors.listar_categorias_geral_com_cursos_semestre_atual()
        filter = CategoriaFilter(self.request.GET, queryset=categorias)
        categorias = filter.qs

        categorias_paginados = paginate_queryset(qs=categorias, page=self.request.GET.get('page'), per_page=15)
    
        context['categorias'] = categorias_paginados
        context['semestre_atual'] = SemestreSelectors.get_semestre_atual()
        context['filter'] = filter
        return context
