from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.http import HttpResponse
from atividades.mixins import AlunoRequiredMixin
from atividades.models import Notificacao
from atividades.selectors import NotificationSelectors


class ListarNotificacoesDropdownView(LoginRequiredMixin, TemplateView):
    """
    Retorna as últimas 8 notificações para o dropdown HTMX
    """
    template_name = 'atividades/notificacoes_dropdown.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todas_notificacoes = NotificationSelectors.get_notificacoes_nao_lidas(self.request.user)

        notificacoes_count = todas_notificacoes.count()
        limitado = False
        if self.request.GET.get('todas') != 'true':
            todas_notificacoes = todas_notificacoes[:15]
            limitado = True

        context['notificacoes'] = todas_notificacoes
        context['total_notificacoes'] = notificacoes_count
        context['tem_mais'] = notificacoes_count > 15 and limitado
        return context

class MarcarNotificacaoLidaView(LoginRequiredMixin, View):

    def post(self, request, notificacao_id):
        notificacao = get_object_or_404(
            Notificacao,
            id=notificacao_id,
            user=request.user
        )
        notificacao.lida = True
        notificacao.save()
        return HttpResponse("", headers={"HX-Trigger": "notificacaoLida"})



class MarcarTodasLidasView(LoginRequiredMixin, View):
    """
    Marca todas as notificações como lidas
    """
    def post(self, request):
        notificacoes = NotificationSelectors.get_notificacoes_nao_lidas(request.user)
        notificacoes.update(lida=True)
        
        # Retorna badge vazio
        return HttpResponse("", headers={"HX-Trigger": "notificacaoLida"})
    
class CountNotificacoesNaoLidas(AlunoRequiredMixin, View):
        def get(self, request):
            total_nao_lidas = NotificationSelectors.count_notificacoes_nao_lidas(request.user)
            
            if total_nao_lidas > 0:
                return HttpResponse(f'<span class="notif-badge">{total_nao_lidas}</span>')
            return HttpResponse('')
