document.body.addEventListener('htmx:afterSwap', (e) => {
  if (e.target.id === 'modal-container' && e.target.innerHTML.trim() !== '') {
    document.body.classList.add('modal-open')
  }
})

// Quando o modal for removido
document.body.addEventListener('htmx:beforeSwap', (e) => {
  if (
    (e.target.id === 'modal-container' && e.detail.xhr.response === '') || (e.target.id === 'aluno-container')
  ) {
    document.body.classList.remove('modal-open')
  }
})