/**
 * Sistema Universal de Filtros com Auto-Submit
 * Aplica auto-submit em formulários de filtro quando há mudança nos campos
 */

document.addEventListener('DOMContentLoaded', function() {
    // Seleciona todos os formulários com a classe 'filtros-atividades'
    const filtroForms = document.querySelectorAll('.filtros-atividades');
    
    filtroForms.forEach(form => {
        // Encontra todos os campos de input, select e checkbox dentro do formulário
        const campos = form.querySelectorAll('input, select, textarea');
        
        // Adiciona evento de mudança em cada campo
        campos.forEach(campo => {
            // Para selects, usa 'change'
            if (campo.tagName === 'SELECT') {
                campo.addEventListener('change', function() {
                    form.submit();
                });
            }
            
            // Para checkboxes e radio buttons, usa 'change'
            else if (campo.type === 'checkbox' || campo.type === 'radio') {
                campo.addEventListener('change', function() {
                    form.submit();
                });
            }
            
            // Para inputs de texto, usa debounce para evitar muitos submits
            else if (campo.type === 'text' || campo.type === 'search' || campo.tagName === 'TEXTAREA') {
                let debounceTimer;
                campo.addEventListener('input', function() {
                    clearTimeout(debounceTimer);
                    debounceTimer = setTimeout(() => {
                        form.submit();
                    }, 800); // Aguarda 800ms após parar de digitar
                });
            }
            
            // Para inputs de data, número, email, etc., usa 'change'
            else {
                campo.addEventListener('change', function() {
                    form.submit();
                });
            }
        });
    });
});
