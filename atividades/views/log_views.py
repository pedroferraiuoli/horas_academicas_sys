from pathlib import Path
from django.views.generic import TemplateView
from django.conf import settings

from ..mixins import GestorRequiredMixin


class VisualizarLogsView(GestorRequiredMixin, TemplateView):
    template_name = "atividades/visualizar_logs.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Define qual arquivo de log visualizar
        log_type = self.request.GET.get("tipo", "errors")
        num_lines = int(self.request.GET.get("linhas", 100))
        
        # Mapeia tipos para arquivos
        log_files = {
            "errors": "errors.log",
            "business": "business.log",
            "security": "security.log",
        }
        
        log_filename = log_files.get(log_type, "errors.log")
        log_path = Path(settings.BASE_DIR) / "logs" / log_filename
        
        log_content = []
        file_exists = False
        
        if log_path.exists():
            file_exists = True
            try:
                # Lê as últimas N linhas do arquivo
                with open(log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    # Pega as últimas N linhas
                    log_content = lines[-num_lines:] if len(lines) > num_lines else lines
                    # Inverte para mostrar as mais recentes primeiro
                    log_content.reverse()
            except Exception as e:
                log_content = [f"Erro ao ler arquivo de log: {str(e)}"]
        
        # Informações do arquivo
        file_size = 0
        if file_exists:
            file_size = log_path.stat().st_size / 1024  # KB
        
        context.update({
            "log_type": log_type,
            "log_content": log_content,
            "file_exists": file_exists,
            "file_size": round(file_size, 2),
            "num_lines": num_lines,
            "log_types": [
                {"value": "errors", "label": "Erros do Sistema"},
                {"value": "business", "label": "Operações Críticas"},
                {"value": "security", "label": "Segurança"},
            ],
        })
        
        return context
