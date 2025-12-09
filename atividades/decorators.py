from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps

def deny_with_message(request, message, redirect_url='dashboard'):
    messages.warning(request, message)
    return redirect(redirect_url)

def gestor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name='Gestor').exists():
            return view_func(request, *args, **kwargs)

        return deny_with_message(
            request,
            "Você não tem permissão para acessar essa área (Gestor necessário)."
        )
    return wrapper


def coordenador_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'coordenador'):
            return view_func(request, *args, **kwargs)

        return deny_with_message(
            request,
            "Apenas coordenadores podem acessar essa área."
        )
    return wrapper


def aluno_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'aluno'):
            return view_func(request, *args, **kwargs)

        return deny_with_message(
            request,
            "Apenas alunos têm acesso a esta página."
        )
    return wrapper

def gestor_ou_coordenador_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        user = request.user

        permitido = (
            user.is_authenticated and (
                user.groups.filter(name='Gestor').exists()
                or hasattr(user, 'coordenador')
            )
        )

        if permitido:
            return view_func(request, *args, **kwargs)

        return deny_with_message(
            request,
            "Apenas Gestores ou Coordenadores podem acessar essa área."
        )

    return wrapper

