"""
Middleware completo para capturar TODOS os tipos de erros e exceções do sistema
"""

import logging
import sys
from django.utils.deprecation import MiddlewareMixin

# Logger para erros críticos
error_logger = logging.getLogger('django')


class ErrorLoggingMiddleware(MiddlewareMixin):
    """
    Middleware que captura TODOS os erros: exceções, erros 500, erros de template, timeouts, etc.
    """
    
    def process_exception(self, request, exception):
        """
        Captura exceções não tratadas nas views
        """
        user_info = f"User: {request.user.username}" if request.user.is_authenticated else "User: Anonymous"
        
        error_logger.error(
            f"ERRO: {exception.__class__.__name__} em {request.path} | "
            f"{user_info} | "
            f"Mensagem: {str(exception)}",
            exc_info=True
        )
        # Retorna None para que Django continue o tratamento normal
        return None
    
    def process_response(self, request, response):
        """
        Captura erros 500 que não passaram por process_exception
        (erros de template, rendering, outros middlewares, etc.)
        """
        if response.status_code == 500:
            user_info = f"User: {request.user.username}" if request.user.is_authenticated else "User: Anonymous"
            
            # Verifica se há informação de exceção no contexto
            exc_info = sys.exc_info()
            if exc_info[0] is not None:
                error_logger.error(
                    f"ERRO 500: {exc_info[0].__name__} em {request.path} | "
                    f"{user_info} | "
                    f"Mensagem: {str(exc_info[1])}",
                    exc_info=exc_info
                )
            else:
                # Erro 500 sem exceção específica capturada (erro de template, etc)
                error_logger.error(
                    f"ERRO 500: Erro não especificado em {request.path} | {user_info}"
                )
        
        return response
