import logging
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib import messages
from ..utils import paginate_queryset

from ..models import Semestre
from ..forms import SemestreForm
from ..services import SemestreService
from ..mixins import GestorRequiredMixin

business_logger = logging.getLogger('atividades.business')


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
    template_name = 'excluir/excluir_generic.html'

    def dispatch(self, request, semestre_id, *args, **kwargs):
        self.semestre = get_object_or_404(Semestre, id=semestre_id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        nome_exclusao = self.semestre.nome
        tipo_exclusao = "Semestre"
        return render(request, self.template_name, {'tipo_exclusao': tipo_exclusao, 'nome_exclusao': nome_exclusao})
    
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
        semestres = Semestre.objects.all()

        semestres_paginados = paginate_queryset(qs=semestres, page=self.request.GET.get('page'), per_page=15)

        context['semestres'] = semestres_paginados
        return context
