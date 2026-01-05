from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib import messages
from ..utils import paginate_queryset
from ..models import Atividade, Aluno
from ..forms import AtividadeForm
from ..selectors import AlunoSelectors, AtividadeSelectors, UserSelectors
from ..services import AtividadeService
from ..filters import AtividadesCoordenadorFilter, AtividadesFilter
from ..mixins import AlunoRequiredMixin, CoordenadorRequiredMixin


class CadastrarAtividadeView(AlunoRequiredMixin, View):
    template_name = 'forms/form_atividade.html'
    htmx_template_name = 'forms/htmx/atividade_modal.html'
    htmx_atividades_list_template = 'listas/htmx/atividades_list.html'

    def dispatch(self, request, *args, **kwargs):
        self.aluno = AlunoSelectors.get_aluno_by_user(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        categoria_id = request.GET.get('categoria', None)
        form = AtividadeForm(aluno=self.aluno, categoria_id=categoria_id)

        if request.headers.get('HX-Request'):
            save_url = request.path
            context = {'form': form, 'save_url': save_url}
            return render(request, self.htmx_template_name, context)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = AtividadeForm(request.POST, request.FILES, aluno=self.aluno)
        url = request.META.get('HTTP_REFERER', 'dashboard')
        
        if form.is_valid():
            atividade = AtividadeService.cadastrar_atividade(form=form, aluno=self.aluno)
            messages.success(request, f'Atividade {atividade.nome} cadastrada com sucesso!')
            
            if request.headers.get('HX-Request'):
                response = render(request, self.htmx_atividades_list_template, {'atividades': AtividadeSelectors.get_atividades_recentes_aluno(self.aluno)})
                response['HX-Trigger'] = 'atividadeCriada'
                return response
            return redirect(url)
        
        # Se houver erros no formulário
        if request.headers.get('HX-Request'):
            save_url = request.path
            context = {'form': form, 'save_url': save_url}
            response = render(request, self.htmx_template_name, context)
            response['HX-Retarget'] = '#modal-container'
            return response
        return render(request, self.template_name, {'form': form})


class EditarAtividadeView(AlunoRequiredMixin, View):
    template_name = 'forms/form_atividade.html'
    htmx_template_name = 'forms/htmx/atividade_modal.html'

    def dispatch(self, request, atividade_id, *args, **kwargs):
        self.aluno = AlunoSelectors.get_aluno_by_user(request.user)
        self.atividade = get_object_or_404(Atividade, id=atividade_id, aluno=self.aluno)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = AtividadeForm(instance=self.atividade, aluno=self.aluno)
        if request.headers.get('HX-Request'):
            save_url = request.path
            context = {'form': form, 'atividade': self.atividade, 'save_url': save_url, 'edit': True}
            return render(request, self.htmx_template_name, context)
        return render(request, self.template_name, {'form': form, 'atividade': self.atividade, 'edit': True})

    def post(self, request):
        url = request.META.get('HTTP_REFERER', 'dashboard')
        form = AtividadeForm(request.POST, request.FILES, instance=self.atividade, aluno=self.aluno)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Atividade {self.atividade.nome} atualizada com sucesso!')
            
            if request.headers.get('HX-Request'):
                # Busca todas as atividades para o contexto correto
                atividades = AtividadeSelectors.get_atividades_recentes_aluno(self.aluno)
                response = render(request, 'listas/htmx/atividades_list.html', {'atividades': atividades})
                response['HX-Trigger'] = 'atividadeCriada'
                return response
            return redirect(url)
        
        # Se houver erros no formulário
        if request.headers.get('HX-Request'):
            save_url = request.path
            context = {'form': form, 'atividade': self.atividade, 'save_url': save_url, 'edit': True}
            response = render(request, self.htmx_template_name, context)
            response['HX-Retarget'] = '#modal-container'
            return response
        return render(request, self.template_name, {'form': form, 'atividade': self.atividade, 'edit': True})


class ExcluirAtividadeView(AlunoRequiredMixin, View):
    template_name = 'excluir/excluir_generic.html'
    htmx_template_name = 'excluir/htmx/confirmar_exclusao_modal.html'
    htmx_atividades_list_template = 'listas/htmx/atividades_list.html'

    def dispatch(self, request, atividade_id, *args, **kwargs):
        self.aluno = AlunoSelectors.get_aluno_by_user(request.user)
        self.atividade = get_object_or_404(Atividade, id=atividade_id, aluno=self.aluno)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        tipo_exclusao = "Atividade"
        nome_exclusao = self.atividade.nome

        context = {
            'tipo_exclusao': tipo_exclusao,
            'nome_exclusao': nome_exclusao,
            'delete_url': f'/atividades/{self.atividade.id}/excluir/',
            'object_id': self.atividade.id
        }
        
        if request.headers.get('HX-Request'):
            return render(request, self.htmx_template_name, context)
        return render(request, self.template_name, context)

    def post(self, request):
        atividade_nome = self.atividade.nome
        AtividadeService.exluir_atividade(atividade=self.atividade)

        messages.success(request, f'Atividade {atividade_nome} excluída com sucesso!')
        
        return redirect(request.META.get('HTTP_REFERER', 'listar_atividades'))


class ListarAtividadesView(AlunoRequiredMixin, TemplateView):
    template_name = 'listas/listar_atividades.html'
    htmx_template_name = 'listas/htmx/atividades_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aluno = AlunoSelectors.get_aluno_by_user(self.request.user)
        atividades = AtividadeSelectors.get_atividades_aluno(aluno)
        filtro = AtividadesFilter(self.request.GET or None, queryset=atividades, request=self.request)
        atividades_filtradas = filtro.qs

        atividades_paginadas = paginate_queryset(qs=atividades_filtradas, page=self.request.GET.get('page'), per_page=10)
        context['atividades'] = atividades_paginadas
        context['filter'] = filtro
        return context
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return [self.htmx_template_name]
        return [self.template_name]


class ListarAtividadesCoordenadorView(CoordenadorRequiredMixin, TemplateView):
    template_name = 'listas/listar_atividades_coordenador.html'
    htmx_template_name = 'listas/htmx/atividades_coord_list.html'

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
            atividades = AtividadeSelectors.get_atividades_pendentes(curso=curso)

        filtro = AtividadesCoordenadorFilter(self.request.GET, queryset=atividades, aluno_id=aluno_id)
        atividades_filtradas = filtro.qs

        atividades_paginadas = paginate_queryset(qs=atividades_filtradas, page=self.request.GET.get('page'), per_page=10)

        context['aluno'] = aluno if aluno_id else None
        context['atividades'] = atividades_paginadas
        context['filter'] = filtro
        return context
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return [self.htmx_template_name]
        return [self.template_name]


class AprovarHorasAtividadeView(CoordenadorRequiredMixin, View):
    def dispatch(self, request, atividade_id, *args, **kwargs):
        self.coordenador = UserSelectors.get_coordenador_by_user(request.user)
        self.atividade = get_object_or_404(Atividade, id=atividade_id)
        if self.atividade.aluno.curso != self.coordenador.curso:
            messages.warning(request, 'Acesso negado à atividade deste aluno.')
            return redirect(request.META.get('HTTP_REFERER', 'listar_atividades_coordenador'))

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
            return redirect(request.META.get('HTTP_REFERER', 'listar_atividades_coordenador'))

        messages.success(request, f'Atividade {self.atividade.nome} aprovada com {horas_aprovadas} horas!')
        return redirect(request.META.get('HTTP_REFERER', 'listar_atividades_coordenador'))
