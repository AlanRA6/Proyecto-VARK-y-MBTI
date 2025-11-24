document.addEventListener('DOMContentLoaded', () => {
    const dashToggle = document.getElementById('dashToggle');
    const dashCollapse = document.getElementById('dashCollapse');

    if (dashToggle && dashCollapse) {
        dashToggle.addEventListener('click', () => {
            // Alternar visibilidad del menú
            dashCollapse.classList.toggle('show');
            
            // Opcional: Cambiar icono de hamburguesa a 'X'
            const icon = dashToggle.querySelector('i');
            if (dashCollapse.classList.contains('show')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-xmark');
            } else {
                icon.classList.remove('fa-xmark');
                icon.classList.add('fa-bars');
            }
        });
    }

    // Cerrar menú si se hace click fuera (UX mejorada)
    document.addEventListener('click', (e) => {
        if (!dashToggle.contains(e.target) && !dashCollapse.contains(e.target)) {
            dashCollapse.classList.remove('show');
            const icon = dashToggle.querySelector('i');
            if(icon) {
                icon.classList.remove('fa-xmark');
                icon.classList.add('fa-bars');
            }
        }
    });
});