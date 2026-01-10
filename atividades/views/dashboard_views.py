from django.views.generic import TemplateView

from atividades.services import AlunoService, StatsService

from ..selectors import AlunoSelectors, AtividadeSelectors, CategoriaCursoSelectors, SemestreSelectors, UserSelectors
from ..mixins import LoginRequiredMixin


class DashboardView(LoginRequiredMixin, TemplateView):

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if UserSelectors.is_user_aluno(user):
            self.dashboard_type = 'aluno'
            self.template_name = 'dashboards/dashboard.html'
            if request.headers.get('HX-Request'):
                self.template_name = 'dashboards/contents/dashboard_partial.html'
        elif UserSelectors.is_user_coordenador(user):
            self.dashboard_type = 'coordenador'
            self.template_name = 'dashboards/dashboard_coord.html'
        elif UserSelectors.is_user_gestor(user):
            self.dashboard_type = 'gestor'
            self.template_name = 'dashboards/dashboard_gestor.html'

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.dashboard_type == 'aluno':
            context.update(self.get_aluno_context())
        else:
            context.update(self.get_gestor_context())

        return context
    
    def get_aluno_context(self):
        aluno = AlunoSelectors.get_aluno_by_user(self.request.user)

        total_horas = AlunoService.calcular_horas_complementares_validas(aluno=aluno, apenas_aprovadas=True)
        horas_requeridas = AlunoSelectors.get_horas_necessarias_para_conclusao(aluno=aluno)

        progresso = 0
        if horas_requeridas > 0:
            progresso = min(100, round((total_horas / horas_requeridas) * 100))

        atividades_recentes = AtividadeSelectors.get_atividades_recentes_aluno(aluno, limite=5)

        ultrapassou_limite = False
        if aluno.curso:
            categorias = CategoriaCursoSelectors.get_categorias_curso(curso=aluno.curso, semestre=aluno.semestre_ingresso)
            ultrapassou_limite = any(
                c.ultrapassou_limite_pelo_aluno(aluno)
                for c in categorias
            )

        horas_pendentes = AtividadeSelectors.get_total_horas_aluno(
            aluno=aluno,
            apenas_pendentes=True
        )

        return {
            'aluno': aluno,
            'total_horas': total_horas,
            'progresso_percentual': progresso,
            'atividades_recentes': atividades_recentes,
            'ultrapassou_limite': ultrapassou_limite,
            'horas_requeridas': horas_requeridas,
            'horas_pendentes': horas_pendentes,
            'horas_totais': horas_pendentes + total_horas,
        }

    def get_gestor_context(self):
        user = self.request.user
        grupo = UserSelectors.get_user_primary_group(user)
        semestre_atual = SemestreSelectors.get_semestre_atual()

        stats = {}
        curso = None

        if grupo == 'Coordenador':
            coordenador = getattr(user, 'coordenador', None)
            if coordenador:
                curso = coordenador.curso
                stats = StatsService.get_stats_coordenador(curso=curso)
        elif grupo == 'Gestor':
            stats = StatsService.get_stats_gestor()

        context = {
            'grupo': grupo,
            'stats': stats,
            'semestre_atual': semestre_atual,
        }

        if grupo == 'Gestor':
            context['ultimos_semestres'] = SemestreSelectors.get_ultimos_semestres_com_alunos(5)
        elif grupo == 'Coordenador' and curso:
            context['ultimos_semestres'] = SemestreSelectors.get_ultimos_semestres_com_alunos(5, curso=curso)

        return context
