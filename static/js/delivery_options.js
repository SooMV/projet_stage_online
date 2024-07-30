document.addEventListener('DOMContentLoaded', function() {
    const deliveryOptions = document.querySelectorAll('input[name="delivery_option"]');
    const targetDiv = document.querySelector('.flex.justify-evenly.items-center.mx-auto.mt-20');

    deliveryOptions.forEach(option => {
        option.addEventListener('change', function() {
            const selectedOption = this.value;
            fetch(`/ajax/load-delivery-option/?option=${selectedOption}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    targetDiv.innerHTML = data.html;
                })
                .catch(error => {
                    console.error('There was a problem with the fetch operation:', error);
                });
        });
    });
});

