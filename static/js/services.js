document.addEventListener('DOMContentLoaded', () => {
    
    const pricingContainer = document.getElementById('pricing-container');
    const cards = document.querySelectorAll('.price-col');

    // Guardamos cuál era la tarjeta destacada original (la del medio)
    // Asumimos que es la segunda (índice 1) si no la buscamos por clase
    const originalFeaturedIndex = 1; 

    cards.forEach((card, index) => {
        card.addEventListener('mouseenter', () => {
            // 1. Quitar la clase featured de TODAS las tarjetas
            cards.forEach(c => c.classList.remove('featured'));
            
            // 2. Agregar la clase featured a la tarjeta ACTUAL (hover)
            card.classList.add('featured');
        });
    });

    // Efecto opcional: Resetear cuando el mouse sale de toda la tabla
    pricingContainer.addEventListener('mouseleave', () => {
        // 1. Quitar featured de todas
        cards.forEach(c => c.classList.remove('featured'));
        
        // 2. Devolver featured a la original (la del medio)
        cards[originalFeaturedIndex].classList.add('featured');
    });
});