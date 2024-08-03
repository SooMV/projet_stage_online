let breaks = false;

document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.button_quantity');
    buttons.forEach(button => {
        console.log('my breaks conditions : ', breaks);
        if (breaks) return;
        button.addEventListener('click', function(event) {
            event.preventDefault();
            console.log('Button clicked');

            const productId = this.dataset.productId;
            const quantityInput = document.getElementById(`quantity-${productId}`);
            let quantity = parseInt(quantityInput.value);

            if (this.classList.contains('increment')) {
                quantity += 1;
            } else if (this.classList.contains('decrement') && quantity > 1) {
                quantity -= 1;
            }

            quantityInput.value = quantity;

            console.log('1er print :', quantity);
            const data = {
                "item_id": productId,
                "quantity": quantity,
            };
            console.log("print data :", data.quantity);

            const config = {
                headers: {
                    "X-CSRFToken": document.querySelector('input[name="csrfmiddlewaretoken"]').value,
                }
            };
            axios.post('ajax_update_quantities', data, config)
            .then(response => {
                breaks = true;

                if (response.data) {
                    console.log('my response',response.data)
                    const productId = response.data.data.order_id;
                    const quantity = response.data.data.quantity;
                    const subtotal = response.data.data.subtotal;
                    const total = response.data.data.total;

                    console.log('my product id is :', productId);
                    console.log('my quantity is :', quantity);
                    console.log('my subtotal is :', subtotal);
                    console.log('my total is :', total);

                    // Mettre à jour la quantité affichée
                    document.getElementById(`quantity-${productId}`).value = quantity;

                    // Mettre à jour le sous-total affiché
                    document.getElementById(`subtotal-${productId}`).textContent = subtotal.toFixed(2);
                    // Mettre à jour le total affiché
                    document.getElementById('cart-total').textContent = total.toFixed(2);
                } else {
                    console.log('Error: No data returned from server');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            })
        .finally(() => {
            breaks = false;
        });
        });
    });
});
