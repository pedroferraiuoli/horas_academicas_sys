/**
 * Sistema Universal de Filtros com Auto-Submit via AJAX
 * Atualiza a listagem dinamicamente sem recarregar a página
 * Suporta paginação via AJAX
 */

document.addEventListener('DOMContentLoaded', function() {
    // Seleciona todos os formulários com a classe 'filtros-atividades'
    const filtroForms = document.querySelectorAll('.filtros-atividades');
    
    filtroForms.forEach(form => {
        // Encontra todos os campos de input, select e checkbox dentro do formulário
        const campos = form.querySelectorAll('input, select, textarea');
        
        // Função para fazer a requisição AJAX
        function atualizarListagem(url = null) {
            const formData = new FormData(form);
            const params = new URLSearchParams(formData);
            
            // Se não foi passada uma URL (ex: paginação), usa a URL atual com os parâmetros do form
            if (!url) {
                url = `${window.location.pathname}?${params.toString()}`;
            }
            
            // Atualiza a URL do navegador sem recarregar
            window.history.pushState({}, '', url);
            
            // Faz a requisição
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                // Cria um elemento temporário para parsear o HTML
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                
                // Atualiza apenas a lista de atividades/itens
                const novaLista = doc.querySelector('.atividades-list');
                const listaAtual = document.querySelector('.atividades-list');
                
                if (novaLista && listaAtual) {
                    listaAtual.innerHTML = novaLista.innerHTML;
                    
                    // Re-inicializa o script de collapse para os novos elementos
                    if (typeof initializeCollapseToggle === 'function') {
                        initializeCollapseToggle();
                    }
                }
                
                // Atualiza a paginação se existir
                const novaPaginacao = doc.querySelector('.pagination');
                const paginacaoAtual = document.querySelector('.pagination');
                
                if (novaPaginacao && paginacaoAtual) {
                    paginacaoAtual.parentElement.innerHTML = novaPaginacao.parentElement.innerHTML;
                    interceptarPaginacao();
                } else if (!novaPaginacao && paginacaoAtual) {
                    // Remove paginação se não houver mais
                    paginacaoAtual.parentElement.remove();
                }
            })
            .catch(error => {
                console.error('Erro ao atualizar listagem:', error);
            });
        }
        
        // Função para interceptar cliques nos links de paginação
        function interceptarPaginacao() {
            const linksPaginacao = document.querySelectorAll('.pagination a');
            
            linksPaginacao.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const url = this.getAttribute('href');
                    if (url && url !== '#') {
                        atualizarListagem(url);
                        // Scroll suave para o topo da lista
                        const listaElement = document.querySelector('.atividades-list');
                        if (listaElement) {
                            listaElement.scrollIntoView({ 
                                behavior: 'smooth', 
                                block: 'start' 
                            });
                        }
                    }
                });
            });
        }
        
        // Inicializa a interceptação de paginação
        interceptarPaginacao();
        
        // Adiciona evento de mudança em cada campo
        campos.forEach(campo => {
            // Para selects, usa 'change'
            if (campo.tagName === 'SELECT') {
                campo.addEventListener('change', function() {
                    atualizarListagem();
                });
            }
            
            // Para checkboxes e radio buttons, usa 'change'
            else if (campo.type === 'checkbox' || campo.type === 'radio') {
                campo.addEventListener('change', function() {
                    atualizarListagem();
                });
            }
            
            // Para inputs de texto, usa debounce para evitar muitas requisições
            else if (campo.type === 'text' || campo.type === 'search' || campo.tagName === 'TEXTAREA') {
                let debounceTimer;
                campo.addEventListener('input', function() {
                    clearTimeout(debounceTimer);
                    debounceTimer = setTimeout(() => {
                        atualizarListagem();
                    }, 200); // Aguarda 500ms após parar de digitar
                });
            }
            
            // Para inputs de data, número, email, etc., usa 'change'
            else {
                campo.addEventListener('change', function() {
                    atualizarListagem();
                });
            }
        });
        
        // Previne o submit padrão do formulário
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            atualizarListagem();
        });
        
        // Suporte ao botão voltar/avançar do navegador
        window.addEventListener('popstate', function() {
            location.reload();
        });
    });
});