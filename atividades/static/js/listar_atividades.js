function toggleCollapseByScreenSize() {
  const atividadeMainElements = document.querySelectorAll('.atividade-main');
  const isMobile = window.innerWidth <= 992;
  
  atividadeMainElements.forEach(element => {
    if (isMobile) {
      // Ativar collapse em mobile
      if (!element.hasAttribute('data-bs-toggle')) {
        const collapseId = element.closest('.atividade-item').querySelector('.atividade-details').id;
        element.setAttribute('data-bs-toggle', 'collapse');
        element.setAttribute('data-bs-target', `#${collapseId}`);
        element.style.cursor = 'pointer';
      }
    } else {
      // Desativar collapse em desktop
      element.removeAttribute('data-bs-toggle');
      element.removeAttribute('data-bs-target');
      element.style.cursor = 'default';
    }
  });
}

// Executar ao carregar a página
toggleCollapseByScreenSize();

// Executar ao redimensionar a janela
window.addEventListener('resize', toggleCollapseByScreenSize);

// Listener HTMX: fechar modal quando atividade for criada/editada
document.body.addEventListener('refresh', function() {
  const modalContainer = document.getElementById('modal-container');
  if (modalContainer) {
    modalContainer.innerHTML = '';
  }
});

