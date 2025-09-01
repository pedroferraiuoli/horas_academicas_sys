from django.conf import settings
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import EmailOrUsernameAuthenticationForm
from django.conf.urls.static import static

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='atividades/login.html',
        authentication_form=EmailOrUsernameAuthenticationForm
    ), name='login'),
    path('criar-usuario-admin/', views.CriarUsuarioAdminView.as_view(), name='criar_usuario_admin'),
    path('listar-usuarios-admin/', views.ListarUsuariosAdminView.as_view(), name='listar_usuarios_admin'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cadastrar-atividade/', views.CadastrarAtividadeView.as_view(), name='cadastrar_atividade'),
    path('criar-categoria/', views.CriarCategoriaView.as_view(), name='criar_categoria'),
    path('criar-categoria-curso/', views.CriarCategoriaCursoView.as_view(), name='criar_categoria_curso'),
    path('criar-categoria-curso-direta/', views.CriarCategoriaCursoDiretaView.as_view(), name='criar_categoria_curso_direta'),
    path('criar-curso/', views.CriarCursoView.as_view(), name='criar_curso'),
    path('cursos/', views.ListarCursosView.as_view(), name='listar_cursos'),
    path('cursos/<int:curso_id>/editar/', views.EditarCursoView.as_view(), name='editar_curso'),
    path('cursos/<int:curso_id>/excluir/', views.ExcluirCursoView.as_view(), name='excluir_curso'),
    path('categorias/', views.ListarCategoriasView.as_view(), name='listar_categorias'),
    path('categorias/<int:categoria_id>/editar/', views.EditarCategoriaView.as_view(), name='editar_categoria'),
    path('categorias/<int:categoria_id>/excluir/', views.ExcluirCategoriaView.as_view(), name='excluir_categoria'),
    path('categorias-curso/', views.ListarCategoriasCursoView.as_view(), name='listar_categorias_curso'),
    path('categorias-curso/<int:categoria_id>/editar/', views.EditarCategoriaCursoView.as_view(), name='editar_categoria_curso'),
    path('categorias-curso/<int:categoria_id>/excluir/', views.ExcluirCategoriaCursoView.as_view(), name='excluir_categoria_curso'),
    path('atividades/', views.ListarAtividadesView.as_view(), name='listar_atividades'),
    path('atividades/<int:atividade_id>/editar/', views.EditarAtividadeView.as_view(), name='editar_atividade'),
    path('atividades/<int:atividade_id>/excluir/', views.ExcluirAtividadeView.as_view(), name='excluir_atividade'),
    path('alterar-email/', views.AlterarEmailView.as_view(), name='alterar_email'),
    path('trocar-senha/', auth_views.PasswordChangeView.as_view(template_name='atividades/password_change_form.html', success_url='/'), name='password_change'),
    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='atividades/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='atividades/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='atividades/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='atividades/password_reset_complete.html'), name='password_reset_complete'),
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('usuarios/<int:user_id>/ativar-desativar/', views.ativar_desativar_usuario, name='ativar_desativar_usuario'),
    path('associar-categorias-ao-curso/', views.AssociarCategoriasAoCursoView.as_view(), name='associar_categorias_ao_curso'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)