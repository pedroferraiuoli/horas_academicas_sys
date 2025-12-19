# Importa todas as views dos módulos especializados para manter compatibilidade
from .curso_views import (
    CriarCursoView,
    EditarCursoView,
    ExcluirCursoView,
    ListarCursosView,
)

from .semestre_views import (
    CriarSemestreView,
    EditarSemestreView,
    ExcluirSemestreView,
    ListarSemestresView,
)

from .categoria_views import (
    CriarCategoriaView,
    EditarCategoriaView,
    ExcluirCategoriaView,
    ListarCategoriasView,
)

from .curso_categoria_views import (
    CriarCategoriaCursoView,
    EditarCategoriaCursoView,
    ExcluirCategoriaCursoView,
    ListarCategoriasCursoView,
    CriarCategoriaCursoDiretaView,
    AssociarCategoriasCursoView,
)

from .atividade_views import (
    CadastrarAtividadeView,
    EditarAtividadeView,
    ExcluirAtividadeView,
    ListarAtividadesView,
    ListarAtividadesCoordenadorView,
    AprovarHorasAtividadeView,
)

from .user_views import (
    RegisterView,
    AlterarEmailView,
    CriarUsuarioAdminView,
    ListarUsuariosAdminView,
    ListarAlunosCoordenadorView,
    ativar_desativar_usuario,
)

from .dashboard_views import DashboardView

from .log_views import VisualizarLogsView

from .error_handlers import (
    custom_404,
    custom_500,
    custom_403,
    custom_400,
)

__all__ = [
    # Curso
    'CriarCursoView',
    'EditarCursoView',
    'ExcluirCursoView',
    'ListarCursosView',
    
    # Semestre
    'CriarSemestreView',
    'EditarSemestreView',
    'ExcluirSemestreView',
    'ListarSemestresView',
    
    # Categoria
    'CriarCategoriaView',
    'EditarCategoriaView',
    'ExcluirCategoriaView',
    'ListarCategoriasView',
    
    # CursoCategoria
    'CriarCategoriaCursoView',
    'EditarCategoriaCursoView',
    'ExcluirCategoriaCursoView',
    'ListarCategoriasCursoView',
    'CriarCategoriaCursoDiretaView',
    'AssociarCategoriasCursoView',
    
    # Atividade
    'CadastrarAtividadeView',
    'EditarAtividadeView',
    'ExcluirAtividadeView',
    'ListarAtividadesView',
    'ListarAtividadesCoordenadorView',
    'AprovarHorasAtividadeView',
    
    # User
    'RegisterView',
    'AlterarEmailView',
    'CriarUsuarioAdminView',
    'ListarUsuariosAdminView',
    'ListarAlunosCoordenadorView',
    'ativar_desativar_usuario',
    
    # Dashboard
    'DashboardView',
    
    # Logs
    'VisualizarLogsView',
    
    # Error Handlers
    'custom_404',
    'custom_500',
    'custom_403',
    'custom_400',
]
