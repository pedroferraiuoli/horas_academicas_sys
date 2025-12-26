// JavaScript para navbar - redirecionamento ao clicar nas categorias
document.addEventListener('DOMContentLoaded', function() {
    const navbarRows = document.querySelectorAll('.sidebar-item');
    navbarRows.forEach(row => {
        row.addEventListener('click', function() {
            window.location.href = this.getAttribute('data-url');
        });
    });
    
    // Rolar até o item ativo quando a página carregar
    const activeItem = document.querySelector('.sidebar-item.active');
    if (activeItem) {
        activeItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Fechar sidebar ao clicar em um item (mobile)
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    sidebarItems.forEach(item => {
        item.addEventListener('click', function() {
            if (window.innerWidth < 992) {
                closeSidebar();
            }
        });
    });

    const sidebarToggle = document.getElementById('sidebar-toggle');
    sidebarToggle.addEventListener('click', function() {
        toggleSidebar();
    });

    const sidebarClose = document.getElementById('sidebar-close');
    sidebarClose.addEventListener('click', function() {
        closeSidebar();
    });
});

// Funções para controle do sidebar mobile
function toggleSidebar() {
    const sidebar = document.getElementById('sidebarMenu');
    const overlay = document.querySelector('.sidebar-overlay');
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
    document.body.style.overflow = sidebar.classList.contains('active') ? 'hidden' : '';
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebarMenu');
    const overlay = document.querySelector('.sidebar-overlay');
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
}