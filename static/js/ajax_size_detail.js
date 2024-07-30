document.addEventListener('DOMContentLoaded', function() {
    const productId = document.getElementById('productId').dataset.productId;

    const sizeSelect = document.getElementById('sizeSelect');

    // Récupérer les tailles disponibles à partir de l'API
    axios.get(`/store/available-sizes/${productId}/`)
        .then(response => {
            const sizes = response.data.sizes;

            // Remplir le champ select avec les tailles disponibles
            sizes.forEach(size => {
                const option = document.createElement('option');
                option.value = size.id;
                option.textContent = size.taille;
                sizeSelect.appendChild(option);
            });

            // Activer le bouton d'ajout au panier
            document.getElementById('addToCartButton').disabled = false;
            document.getElementById('addToCartButton').style.opacity = '100%';
        })
        .catch(error => {
            console.error(error);
        });
});
