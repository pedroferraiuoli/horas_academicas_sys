
const form = document.getElementById('register-form');
const semestreField = document.querySelector('select[name="semestre"]');
const modal = document.getElementById('semestre-modal');
const semestreTextoEl = document.getElementById('semestre-selecionado-texto');
const btnConfirmar = document.getElementById('btn-confirmar-semestre');
const btnCancelar = document.getElementById('btn-cancelar-semestre');

let semestreConfirmado = false;
let ultimoSemestreSelecionado = null;

// Quando o usuário selecionar um semestre
semestreField.addEventListener('change', function() {
  const opcaoSelecionada = this.options[this.selectedIndex];
  const semestreTexto = opcaoSelecionada.text;
  semestreTextoEl.textContent = semestreTexto;
  modal.style.display = 'flex';
  semestreConfirmado = false;
});

// Botão confirmar
btnConfirmar.addEventListener('click', function() {
  semestreConfirmado = true;
  ultimoSemestreSelecionado = semestreField.value;
  semestreField.classList.add('semestre-confirmado');
  modal.style.display = 'none';
});

// Botão cancelar
btnCancelar.addEventListener('click', function() {
  semestreField.value = '';
  semestreField.classList.remove('semestre-confirmado');
  semestreConfirmado = false;
  ultimoSemestreSelecionado = null;
  modal.style.display = 'none';
});

// Fechar modal clicando no overlay
modal.addEventListener('click', function(e) {
  if (e.target === modal || e.target.classList.contains('semestre-modal-overlay')) {
    btnCancelar.click();
  }
});

// Validação no submit do formulário
form.addEventListener('submit', function(e) {
  if (semestreField.value && !semestreConfirmado) {
    e.preventDefault();
    semestreTextoEl.textContent = semestreField.options[semestreField.selectedIndex].text;
    modal.style.display = 'flex';
    return false;
  }
});
