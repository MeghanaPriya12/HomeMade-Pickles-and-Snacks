// Initialize cart from sessionStorage or create empty cart
let cart = JSON.parse(sessionStorage.getItem('cart')) || [];

// Add to cart buttons event listeners
document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', function () {
        const productId = this.dataset.productId;
        const productName = this.dataset.productName;
        const card = this.closest('.product-card');

        // Get selected weight and price
        const selectedWeight = card.querySelector('input[name^="weight"]:checked').value;
        const price = parseFloat(card.querySelector('input[name^="weight"]:checked').dataset.price);

        // Get quantity
        const quantity = parseInt(card.querySelector('.qty-input').value);

        // Add item to cart
        addToCart(productId, productName, selectedWeight, price, quantity);
    });
});

// Quantity selector buttons
document.querySelectorAll('.qty-btn').forEach(button => {
    button.addEventListener('click', function () {
        const input = this.parentElement.querySelector('.qty-input');
        let value = parseInt(input.value);

        if (this.classList.contains('minus') && value > 1) {
            value--;
        } else if (this.classList.contains('plus')) {
            value++;
        }

        input.value = value;
    });
});

// Function to add item to cart
function addToCart(id, name, weight, price, quantity) {
    // Check if item already exists in cart
    const existingItem = cart.find(item =>
        item.id === id && item.weight === weight);

    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            id: id,
            name: name,
            weight: weight,
            price: price,
            quantity: quantity
        });
    }

    // Update session storage
    sessionStorage.setItem('cart', JSON.stringify(cart));

    // Update cart UI
    updateCartUI();

    // Show success message
    alert(`${name} (${weight}g) added to cart!`);
}

// Function to update cart UI
function updateCartUI() {
    const cartContainer = document.getElementById('cart-container');
    if (!cartContainer) return;

    if (cart.length === 0) {
        cartContainer.innerHTML = '<p class="empty-cart-message">Your cart is empty. Start shopping now!</p>';
        return;
    }

    // Generate cart items HTML
    let html = '';
    let total = 0;

    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;

        html += `
            <div class="cart-item">
                <div class="cart-item-details">
                    <h4>${item.name} (${item.weight}g)</h4>
                    <p>₹${item.price.toFixed(1)} × ${item.quantity}</p>
                </div>
                <div class="cart-item-price">
                    <p>₹${itemTotal.toFixed(1)}</p>
                    <button class="remove-item" data-id="${item.id}" data-weight="${item.weight}">×</button>
                </div>
            </div>
        `;
    });

    // Add total and checkout button
    html += `
        <div class="cart-total">
            <p>Total: ₹${total.toFixed(1)}</p>
        </div>
    `;

    cartContainer.innerHTML = html;

    // Add event listeners to remove buttons
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', function () {
            const id = this.dataset.id;
            const weight = this.dataset.weight;
            removeFromCart(id, weight);
        });
    });
}

// Function to remove item from cart
function removeFromCart(id, weight) {
    cart = cart.filter(item => !(item.id === id && item.weight === weight));
    sessionStorage.setItem('cart', JSON.stringify(cart));
    updateCartUI();
}

// Initialize cart UI on page load
updateCartUI();

// Checkout button event listener
const checkoutBtn = document.getElementById('checkout-btn');
if (checkoutBtn) {
    checkoutBtn.addEventListener('click', function (e) {
        if (cart.length === 0) {
            e.preventDefault();
            alert('Your cart is empty. Please add items before checkout.');
        }
    });
}