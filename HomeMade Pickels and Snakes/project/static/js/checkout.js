document.addEventListener('DOMContentLoaded', function () {
    // Load cart data from sessionStorage
    const cart = JSON.parse(sessionStorage.getItem('cart')) || [];
    const totalAmount = cart.reduce((total, item) => total + (item.price * item.quantity), 0);

    // Update hidden form fields
    const cartDataField = document.getElementById('cart-data');
    const totalAmountField = document.getElementById('total-amount');

    if (cartDataField) cartDataField.value = JSON.stringify(cart);
    if (totalAmountField) totalAmountField.value = totalAmount.toFixed(1);

    // Update order summary
    const summaryItems = document.getElementById('summary-items');
    const summaryTotal = document.getElementById('summary-total');

    if (summaryItems && summaryTotal) {
        let html = '';
        cart.forEach(item => {
            const itemTotal = item.price * item.quantity;
            html += `
                <div class="summary-item">
                    <span>${item.name} (${item.weight}g) × ${item.quantity}</span>
                    <span>₹${itemTotal.toFixed(1)}</span>
                </div>
            `;
        });

        summaryItems.innerHTML = html;
        summaryTotal.textContent = `₹${totalAmount.toFixed(1)}`;
    }

    // Form validation
    const form = document.getElementById('checkout-form');
    if (form) {
        form.addEventListener('submit', function (e) {
            if (cart.length === 0) {
                e.preventDefault();
                alert('Your cart is empty!');
                return;
            }
            // Additional validation can be added here
        });
    }
});