import logging
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from atividades.selectors import UserSelectors

security_logger = logging.getLogger('atividades.security')

class GestorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return UserSelectors.is_user_gestor(self.request.user)
    
    def handle_no_permission(self):
        user = self.request.user
        view_name = self.request.resolver_match.view_name
        create_log(user=user, route=view_name)
        messages.warning(self.request, 'Acesso negado.')
        return redirect('dashboard')

class GestorOuCoordenadorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return UserSelectors.is_user_gestor(user) or UserSelectors.is_user_coordenador(user)
    
    def handle_no_permission(self):
        user = self.request.user
        view_name = self.request.resolver_match.view_name
        create_log(user=user, route=view_name)
        messages.warning(self.request, 'Acesso negado.')
        return redirect('dashboard')
    
class CoordenadorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return UserSelectors.is_user_coordenador(self.request.user)
    
    def handle_no_permission(self):
        user = self.request.user
        view_name = self.request.resolver_match.view_name
        create_log(user=user, route=view_name)
        messages.warning(self.request, 'Acesso negado.')
        return redirect('dashboard')
    
class AlunoRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return UserSelectors.is_user_aluno(self.request.user)
    
    def handle_no_permission(self):
        user = self.request.user
        view_name = self.request.resolver_match.view_name
        create_log(user=user, route=view_name)
        messages.warning(self.request, 'Acesso negado.')
        return redirect('dashboard')
    
class LoginRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated
    
    def handle_no_permission(self):
        messages.warning(self.request, 'Por favor, faça login para continuar.')
        return redirect('login')
    
def create_log(*, user, route):
    if not user.is_authenticated:
        security_logger.warning(
                    f"ACESSO NEGADO: Usuário anônimo tentou acessar a rota '{route}' sem permissão."
                    )
    else:
        group = user.groups.first().name if user.groups.exists() else "Aluno"
        security_logger.warning(
                        f"ACESSO NEGADO: Usuário {user.username} ({group})"
                        f" tentou acessar a rota '{route}' sem permissão."
                        )
