// associar_categorias.js - Funcionalidade para associar categorias a cursos

document.addEventListener('DOMContentLoaded', function() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const associationForm = document.getElementById('associationForm');
    
    // Funcionalidade de selecionar/desselecionar todas
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.categoria-checkbox');
            checkboxes.forEach(cb => cb.checked = this.checked);
        });
    }
    
    // Validação antes de submeter
    if (associationForm) {
        associationForm.addEventListener('submit', function(e) {
            const checkboxes = document.querySelectorAll('.categoria-checkbox:checked');
            
            if (checkboxes.length === 0) {
                e.preventDefault();
                alert('Selecione pelo menos uma categoria para associar.');
                return false;
            }
            
            // Validar que categorias marcadas têm limite preenchido
            let hasError = false;
            checkboxes.forEach(cb => {
                const id = cb.name.replace('cat_', '');
                const horasInput = document.getElementById('id_horas_' + id);
                if (!horasInput.value || parseInt(horasInput.value) <= 0) {
                    hasError = true;
                    horasInput.classList.add('is-invalid');
                } else {
                    horasInput.classList.remove('is-invalid');
                }
            });
            
            if (hasError) {
                e.preventDefault();
                alert('Informe o limite de horas (maior que zero) para todas as categorias selecionadas.');
                return false;
            }
        });
    }
});
