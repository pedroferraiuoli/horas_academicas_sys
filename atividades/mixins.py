from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin

class GestorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Gestor').exists()
    
    def handle_no_permission(self):
        messages.warning(self.request, 'Acesso negado.')
        return redirect('dashboard')

class GestorOuCoordenadorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.groups.filter(name='Gestor').exists() or user.groups.filter(name='Coordenador').exists()
    
    def handle_no_permission(self):
        messages.warning(self.request, 'Acesso negado.')
        return redirect('dashboard')
    
class CoordenadorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Coordenador').exists()
    
    def handle_no_permission(self):
        messages.warning(self.request, 'Acesso negado.')
        return redirect('dashboard')
    
class AlunoRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return getattr(self.request.user, 'aluno', None) is not None
    
    def handle_no_permission(self):
        messages.warning(self.request, 'Acesso negado.')
        return redirect('dashboard')
