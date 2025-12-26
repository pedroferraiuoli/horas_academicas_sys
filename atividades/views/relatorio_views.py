from django.http import HttpResponse
from django.views import View
from datetime import datetime
from ..selectors import AlunoSelectors
from ..services import RelatorioAlunoService
from ..pdfBuilder.relatorio_aluno import RelatorioAlunoPdfBuilder
from ..mixins import AlunoRequiredMixin


class GerarRelatorioAlunoView(AlunoRequiredMixin, View):

    def get(self, request):
        aluno = AlunoSelectors.get_aluno_by_user(request.user)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="relatorio_{aluno.matricula}_{datetime.now():%Y%m%d}.pdf"'
        )

        dados = RelatorioAlunoService.gerar_dados_relatorio(aluno=aluno)

        RelatorioAlunoPdfBuilder(
            response=response,
            dados=dados
        ).build()

        return response
