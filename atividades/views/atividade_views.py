from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from ..models import Atividade, Aluno
from ..forms import AtividadeForm
from ..selectors import AlunoSelectors, AtividadeSelectors, UserSelectors
from ..services import AtividadeService
from ..filters import AtividadesCoordenadorFilter, AtividadesFilter
from ..mixins import AlunoRequiredMixin, CoordenadorRequiredMixin


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

        paginator = Paginator(atividades_filtradas, 10)  # 10 atividades por página
        page = self.request.GET.get('page')

        try:
            atividades_paginadas = paginator.page(page)
        except PageNotAnInteger:
            atividades_paginadas = paginator.page(1)
        except EmptyPage:
            atividades_paginadas = paginator.page(paginator.num_pages)

        context['atividades'] = atividades_paginadas
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
            show_status_filter = True
        else: 
            atividades = AtividadeSelectors.get_atividades_pendentes(curso=curso)
            show_status_filter = False

        filtro = AtividadesCoordenadorFilter(self.request.GET, queryset=atividades, show_status=show_status_filter)
        atividades_filtradas = filtro.qs

         # Paginação
        paginator = Paginator(atividades_filtradas, 20)  # 20 alunos por página
        page = self.request.GET.get('page')
        
        try:
            atividades_paginadas = paginator.page(page)
        except PageNotAnInteger:
            atividades_paginadas = paginator.page(1)
        except EmptyPage:
            atividades_paginadas = paginator.page(paginator.num_pages)

        context['aluno'] = aluno if aluno_id else None
        context['atividades'] = atividades_paginadas
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
