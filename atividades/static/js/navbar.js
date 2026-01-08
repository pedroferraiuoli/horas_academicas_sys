// JavaScript para navbar - redirecionamento ao clicar nas categorias

function initializeSidebar() {

    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.addEventListener('click', () => {
            document
                .querySelectorAll('.sidebar-item.active')
                .forEach(i => i.classList.remove('active'))

            item.classList.add('active')
        })
    })

    window.addEventListener('popstate', () => {
        document
            .querySelectorAll('.sidebar-item.active')
            .forEach(i => i.classList.remove('active'))
    })
    

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
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            toggleSidebar();
        });
    }

    const sidebarClose = document.getElementById('sidebar-close');
    if (sidebarClose) {
        sidebarClose.addEventListener('click', function() {
            closeSidebar();
        });
    }
}

document.addEventListener('DOMContentLoaded', initializeSidebar);

document.body.addEventListener('htmx:historyRestore', initializeSidebar);

function toggleSidebar() {
    const sidebar = document.getElementById('sidebarMenu');
    sidebar.classList.toggle('active');
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebarMenu');
    sidebar.classList.remove('active');

}