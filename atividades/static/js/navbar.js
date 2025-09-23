// JavaScript para navbar - redirecionamento ao clicar nas categorias
document.addEventListener('DOMContentLoaded', function() {
    const navbarRows = document.querySelectorAll('.navbar-row[data-url]');
    navbarRows.forEach(row => {
        row.addEventListener('click', function() {
            window.location.href = this.getAttribute('data-url');
        });
    });
});
