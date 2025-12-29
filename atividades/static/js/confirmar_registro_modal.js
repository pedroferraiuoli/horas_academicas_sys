/**
 * Modal de Confirmação de Registro
 * Gerencia a abertura e fechamento do modal de confirmação de semestre
 */

document.addEventListener('DOMContentLoaded', function() {
    // Função para fechar o modal
    window.fecharModalConfirmacao = function() {
        const modal = document.getElementById('modal-confirmacao');
        const backdrop = document.getElementById('modal-confirmacao-backdrop');
        
        if (modal) {
            modal.remove();
        }
        if (backdrop) {
            backdrop.remove();
        }
    };

    // Função para confirmar e submeter o formulário
    window.confirmarRegistro = function() {
        const form = document.querySelector('form[data-register-form]');
        
        if (form) {
            // Remove os atributos HTMX para fazer submit normal
            form.removeAttribute('hx-post');
            form.removeAttribute('hx-target');
            form.removeAttribute('hx-swap');
            
            // Define a action para a URL de registro
            form.method = 'post';
            
            // Submete o formulário
            form.submit();
        }
        
        // Fecha o modal
        fecharModalConfirmacao();
    };

    // Fechar modal com tecla ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('modal-confirmacao');
            if (modal) {
                fecharModalConfirmacao();
            }
        }
    });

    // Event delegation para botões que aparecem dinamicamente
    document.body.addEventListener('click', function(e) {
        // Fechar ao clicar no backdrop
        if (e.target && e.target.id === 'modal-confirmacao-backdrop') {
            fecharModalConfirmacao();
        }
        
        // Fechar ao clicar no botão close
        if (e.target && e.target.closest('.modal-confirmacao-close')) {
            e.preventDefault();
            fecharModalConfirmacao();
        }
        
        // Fechar ao clicar no botão cancelar
        if (e.target && e.target.closest('.modal-confirmacao-btn-cancel')) {
            e.preventDefault();
            fecharModalConfirmacao();
        }
        
        // Confirmar ao clicar no botão confirmar
        if (e.target && e.target.closest('.modal-confirmacao-btn-confirm')) {
            e.preventDefault();
            confirmarRegistro();
        }
    });
});
