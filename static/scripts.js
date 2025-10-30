// static/scripts.js

// API Base URL
const API_URL = '/api';

// Get token from localStorage
function getToken() {
    return localStorage.getItem('token');
}

// Set token
function setToken(token) {
    localStorage.setItem('token', token);
}

// Remove token
function removeToken() {
    localStorage.removeItem('token');
}

// API call with auth
async function apiCall(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers
    });
    
    if (response.status === 401) {
        removeToken();
        updateAuthUI();
    }
    
    return response;
}

// Update auth UI
async function updateAuthUI() {
    const authLink = document.getElementById("authLink");
    const adminLink = document.getElementById("adminLink");

    const token = localStorage.getItem("token");
    if (!token) {
        authLink.textContent = "Login";
        authLink.href = "/login";
        adminLink.style.display = "none"; // hide for guest users
        return;
    }

    try {
        const response = await fetch("/users/me", {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) {
            throw new Error("User not authenticated");
        }

        const user = await response.json();
        authLink.textContent = `Logout (${user.username})`;
        authLink.href = "#";
        authLink.onclick = () => {
            localStorage.removeItem("token");
            location.reload();
        };

        // ✅ Show Admin Dashboard only if user.is_admin == true
        if (user.is_admin) {
            adminLink.style.display = "block";
        } else {
            adminLink.style.display = "none";
        }

    } catch (error) {
        console.error("Error fetching user:", error);
        authLink.textContent = "Login";
        authLink.href = "/login";
        adminLink.style.display = "none";
    }
}


// Logout
function logout() {
    removeToken();
    updateAuthUI();
    alert('Logged out successfully');
    window.location.href = '/';
}

// Load featured products
async function loadFeaturedProducts() {
    try {
        const response = await fetch(`${API_URL}/products/featured`);
        
        if (!response.ok) {
            console.error('Error response:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('Error details:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const products = await response.json();
        console.log('Featured products loaded:', products);
        
        const container = document.getElementById('featuredProducts');
        if (!container) return;
        
        if (products.length === 0) {
            container.innerHTML = '<p style="text-align: center; padding: 2rem;">No featured products available</p>';
            return;
        }
        
        container.innerHTML = products.map(product => createProductCard(product)).join('');
    } catch (error) {
        console.error('Error loading featured products:', error);
        const container = document.getElementById('featuredProducts');
        if (container) {
            container.innerHTML = '<p style="text-align: center; padding: 2rem; color: red;">Error loading featured products. Please check console.</p>';
        }
    }
}

// Load all products
async function loadAllProducts() {
    try {
        const response = await fetch(`${API_URL}/products`);
        const products = await response.json();
        
        const container = document.getElementById('allProducts');
        if (!container) return;
        
        container.innerHTML = products.map(product => createProductCard(product)).join('');
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

// Load categories
async function loadCategories() {
    try {
        const response = await fetch(`${API_URL}/products/categories`);
        const categories = await response.json();
        
        const container = document.getElementById('categories');
        const filterSelect = document.getElementById('categoryFilter');
        const productCategorySelect = document.getElementById('productCategory');
        
        if (container) {
            container.innerHTML = categories.map(cat => 
                `<div class="category-card" onclick="filterByCategory('${cat}')">${cat}</div>`
            ).join('');
        }
        
        if (filterSelect) {
            filterSelect.innerHTML = '<option value="">All Categories</option>' +
                categories.map(cat => `<option value="${cat}">${cat}</option>`).join('');
        }
        
        // Update admin product form dropdown
        if (productCategorySelect) {
            productCategorySelect.innerHTML = '<option value="">Select Category</option>' +
                categories.map(cat => `<option value="${cat}">${cat}</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}
// Create product card HTML
function createProductCard(product) {
    const isCombo = product.category === 'Gift Combos';
    const badge = isCombo ? '<span style="background: #e74c3c; color: white; padding: 0.3rem 0.6rem; border-radius: 5px; font-size: 0.8rem; position: absolute; top: 10px; right: 10px;">🎁 FREE Gift</span>' : '';
    
    // Use actual image if available, otherwise use placeholder
    const imageDisplay = product.image_url && product.image_url !== '/static/uploads/default.jpg' 
        ? `<img src="${product.image_url}" alt="${product.name}" style="width: 100%; height: 100%; object-fit: cover;">` 
        : '<div style="font-size: 4rem;">🕯️</div>';
    
    return `
        <div class="product-card" onclick="viewProduct(${product.id})">
            <div style="position: relative;">
                ${badge}
                <div class="product-image">
                    ${imageDisplay}
                </div>
            </div>
            <div class="product-info">
                <div class="product-category">${product.category}</div>
                <h3 class="product-name">${product.name}</h3>
                <p class="product-description">${product.description.substring(0, 80)}...</p>
                <div class="product-price">₹${product.price}</div>
                <div class="product-actions">
                    <button class="btn btn-primary" onclick="event.stopPropagation(); addToCart(${product.id})">Add to Cart</button>
                    <button class="btn btn-secondary" onclick="event.stopPropagation(); viewProduct(${product.id})">View</button>
                </div>
            </div>
        </div>
    `;
}

// View product
function viewProduct(productId) {
    window.location.href = `/product/${productId}`;
}

// Add to cart
async function addToCart(productId, quantity = 1) {
    const token = getToken();
    
    if (!token) {
        alert('Please login to add items to cart');
        window.location.href = '/login';
        return;
    }
    
    try {
        const response = await apiCall('/cart', {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, quantity })
        });
        
        if (response.ok) {
            alert('Item added to cart!');
            updateCartCount();
        } else {
            const error = await response.json();
            alert(error.detail || 'Error adding to cart');
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        alert('Error adding to cart');
    }
}

// Update cart count
async function updateCartCount() {
    const token = getToken();
    const cartCount = document.getElementById('cartCount');
    
    if (!token || !cartCount) {
        if (cartCount) cartCount.textContent = '0';
        return;
    }
    
    try {
        const response = await apiCall('/cart');
        if (response.ok) {
            const items = await response.json();
            const count = items.reduce((sum, item) => sum + item.quantity, 0);
            cartCount.textContent = count;
        }
    } catch (error) {
        console.error('Error updating cart count:', error);
    }
}

// Show cart
function showCart() {
    window.location.href = '/cart';
}

// Filter by category
async function filterByCategory(category) {
    try {
        const response = await fetch(`${API_URL}/products?category=${encodeURIComponent(category)}`);
        const products = await response.json();
        
        const container = document.getElementById('allProducts');
        if (container) {
            container.innerHTML = products.map(product => createProductCard(product)).join('');
            scrollToProducts();
        }
    } catch (error) {
        console.error('Error filtering products:', error);
    }
}

// Filter by price
async function filterByPrice(minPrice, maxPrice) {
    try {
        const response = await fetch(`${API_URL}/products?min_price=${minPrice}&max_price=${maxPrice}`);
        const products = await response.json();
        
        const container = document.getElementById('allProducts');
        if (container) {
            container.innerHTML = products.map(product => createProductCard(product)).join('');
            scrollToProducts();
        }
    } catch (error) {
        console.error('Error filtering products:', error);
    }
}

// Apply filters
async function applyFilters() {
    const category = document.getElementById('categoryFilter')?.value || '';
    const sort = document.getElementById('sortFilter')?.value || '';
    
    try {
        let url = `${API_URL}/products?`;
        if (category) url += `category=${encodeURIComponent(category)}&`;
        
        const response = await fetch(url);
        let products = await response.json();
        
        // Sort products
        if (sort === 'price_asc') {
            products.sort((a, b) => a.price - b.price);
        } else if (sort === 'price_desc') {
            products.sort((a, b) => b.price - a.price);
        }
        
        const container = document.getElementById('allProducts');
        if (container) {
            container.innerHTML = products.map(product => createProductCard(product)).join('');
        }
    } catch (error) {
        console.error('Error applying filters:', error);
    }
}

// Search products
async function searchProducts() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput?.value || '';
    
    if (!query) {
        loadAllProducts();
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/products?search=${encodeURIComponent(query)}`);
        const products = await response.json();
        
        const container = document.getElementById('allProducts');
        if (container) {
            container.innerHTML = products.map(product => createProductCard(product)).join('');
            scrollToProducts();
        }
    } catch (error) {
        console.error('Error searching products:', error);
    }
}

// Scroll to products
function scrollToProducts() {
    const section = document.getElementById('productsSection');
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Subscribe to newsletter
async function subscribeNewsletter(event) {
    event.preventDefault();
    
    const email = document.getElementById('newsletterEmail')?.value;
    
    try {
        const response = await fetch(`${API_URL}/newsletter`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        
        if (response.ok) {
            alert('Successfully subscribed to newsletter!');
            document.getElementById('newsletterEmail').value = '';
        } else {
            const error = await response.json();
            alert(error.detail || 'Error subscribing');
        }
    } catch (error) {
        console.error('Error subscribing:', error);
        alert('Error subscribing to newsletter');
    }
}

// Send contact message
async function sendMessage(event) {
    event.preventDefault();
    
    const name = document.getElementById('contactName')?.value;
    const email = document.getElementById('contactEmail')?.value;
    const mobile = document.getElementById('contactMobile')?.value;
    const message = document.getElementById('contactMessage')?.value;
    
    try {
        const response = await fetch(`${API_URL}/contact`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({name, email, mobile ,message })
        });
        
        if (response.ok) {
            alert('Message sent successfully!');
            document.getElementById('contactName').value = '';
            document.getElementById('contactEmail').value = '';
            document.getElementById('contactMobile').value = '';
            document.getElementById('contactMessage').value = '';
        } else {
            alert('Error sending message');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        alert('Error sending message');
    }
}

// Product page functions
async function loadProductDetail(productId) {
    try {
        const response = await fetch(`${API_URL}/products/${productId}`);
        
        if (!response.ok) {
            throw new Error('Product not found');
        }
        
        const product = await response.json();
        console.log('Product loaded:', product);
        
        const container = document.getElementById('productDetail');
        if (!container) return;
        
        // Use actual image if available
        const imageDisplay = product.image_url && product.image_url !== '/static/uploads/default.jpg' 
            ? `<img src="${product.image_url}" alt="${product.name}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 15px;">` 
            : '<div style="font-size: 10rem;">🕯️</div>';
        
        const isCombo = product.category === 'Gift Combos';
        const comboBadge = isCombo ? '<div style="background: #e74c3c; color: white; padding: 0.5rem 1rem; border-radius: 8px; display: inline-block; margin-bottom: 1rem;">🎁 FREE Gift Included</div>' : '';
        
        container.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; max-width: 1200px; margin: 0 auto;">
                <div>
                    <div style="width: 100%; height: 500px; background: var(--accent); border-radius: 15px; display: flex; align-items: center; justify-content: center; overflow: hidden; box-shadow: 0 5px 15px var(--shadow);">
                        ${imageDisplay}
                    </div>
                </div>
                <div>
                    ${comboBadge}
                    <div class="product-category" style="font-size: 1rem;">${product.category}</div>
                    <h1 style="font-size: 2.5rem; margin: 1rem 0; color: var(--dark);">${product.name}</h1>
                    <p style="font-size: 1.1rem; color: #666; margin: 1.5rem 0; line-height: 1.8;">${product.description}</p>
                    <div style="font-size: 2.5rem; color: var(--primary); font-weight: bold; margin: 2rem 0;">₹${product.price}</div>
                    
                    <div style="background: var(--accent); padding: 1rem; border-radius: 8px; margin: 1.5rem 0;">
                        <p style="margin: 0.5rem 0;"><strong>Stock Available:</strong> ${product.stock} units</p>
                        <p style="margin: 0.5rem 0;"><strong>Category:</strong> ${product.category}</p>
                    </div>
                    
                    <div style="display: flex; gap: 1rem; align-items: center; margin: 2rem 0;">
                        <label style="font-weight: bold;">Quantity:</label>
                        <input type="number" id="productQuantity" value="1" min="1" max="${product.stock}" 
                               style="width: 100px; padding: 0.75rem; border: 2px solid var(--primary); border-radius: 8px; font-size: 1rem; text-align: center;">
                    </div>
                    
                    <div style="display: flex; gap: 1rem;">
                        <button class="btn btn-primary" style="flex: 2; padding: 1.2rem; font-size: 1.2rem;" 
                                onclick="addToCartFromDetail(${product.id})">
                            🛒 Add to Cart
                        </button>
                        <button class="btn btn-secondary" style="flex: 1; padding: 1.2rem; font-size: 1.2rem;" 
                                onclick="window.location.href='/'">
                            ← Back
                        </button>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 4rem; padding: 2rem; background: white; border-radius: 15px; box-shadow: 0 5px 15px var(--shadow);">
                <h2 style="color: var(--secondary); margin-bottom: 1.5rem;">Product Details</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem;">
                    <div>
                        <h3 style="color: var(--primary); margin-bottom: 0.5rem;">✨ Handcrafted Quality</h3>
                        <p style="color: #666;">Each candle is carefully handcrafted with premium materials for the best experience.</p>
                    </div>
                    <div>
                        <h3 style="color: var(--primary); margin-bottom: 0.5rem;">🌿 Natural Ingredients</h3>
                        <p style="color: #666;">Made with natural wax and high-quality fragrance oils that are safe and eco-friendly.</p>
                    </div>
                    <div>
                        <h3 style="color: var(--primary); margin-bottom: 0.5rem;">🎁 Perfect Gift</h3>
                        <p style="color: #666;">Beautifully packaged, making it an ideal gift for any celebration or occasion.</p>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading product:', error);
        const container = document.getElementById('productDetail');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem;">
                    <h2 style="color: var(--secondary); margin-bottom: 1rem;">Product Not Found</h2>
                    <p style="color: #666; margin-bottom: 2rem;">Sorry, we couldn't find the product you're looking for.</p>
                    <button class="btn btn-primary" onclick="window.location.href='/'">← Back to Home</button>
                </div>
            `;
        }
    }
}

function addToCartFromDetail(productId) {
    const quantity = parseInt(document.getElementById('productQuantity')?.value || 1);
    addToCart(productId, quantity);
}



// Cart page functions
async function loadCart() {
    const token = getToken();
    
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    try {
        const response = await apiCall('/cart');
        const items = await response.json();
        
        const container = document.getElementById('cartItems');
        const summary = document.getElementById('cartSummary');
        
        if (!container) return;
        
        if (items.length === 0) {
            container.innerHTML = '<p style="text-align: center; padding: 2rem;">Your cart is empty</p>';
            if (summary) summary.innerHTML = '';
            return;
        }
        
        let total = 0;
        
        container.innerHTML = items.map(item => {
            const itemTotal = item.product.price * item.quantity;
            total += itemTotal;
            
            return `
                <div class="cart-item">
                    <div class="cart-item-image">🕯️</div>
                    <div class="cart-item-info">
                        <h3>${item.product.name}</h3>
                        <p>₹${item.product.price}</p>
                    </div>
                    <div class="cart-item-actions">
                        <button class="quantity-btn" onclick="updateCartQuantity(${item.id}, ${item.quantity - 1})">-</button>
                        <span style="padding: 0 1rem; font-weight: bold;">${item.quantity}</span>
                        <button class="quantity-btn" onclick="updateCartQuantity(${item.id}, ${item.quantity + 1})">+</button>
                    </div>
                    <div style="font-weight: bold;">₹${itemTotal}</div>
                    <button class="btn btn-secondary" style="padding: 0.5rem;" onclick="removeFromCart(${item.id})">Remove</button>
                </div>
            `;
        }).join('');
        
        if (summary) {
            summary.innerHTML = `
                <h2>Order Summary</h2>
                <div style="margin: 2rem 0;">
                    <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                        <span>Subtotal:</span>
                        <span>₹${total}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                        <span>Shipping:</span>
                        <span>FREE</span>
                    </div>
                    <hr style="margin: 1rem 0;">
                    <div style="display: flex; justify-content: space-between; font-size: 1.5rem; font-weight: bold;">
                        <span>Total:</span>
                        <span style="color: var(--primary);">₹${total}</span>
                    </div>
                </div>
                <button class="btn btn-primary" style="width: 100%; padding: 1rem;" onclick="proceedToCheckout()">Proceed to Checkout</button>
            `;
        }
    } catch (error) {
        console.error('Error loading cart:', error);
    }
}

async function updateCartQuantity(itemId, newQuantity) {
    if (newQuantity < 1) {
        removeFromCart(itemId);
        return;
    }
    
    try {
        const response = await apiCall(`/cart/${itemId}?quantity=${newQuantity}`, {
            method: 'PUT'
        });
        
        if (response.ok) {
            loadCart();
            updateCartCount();
        }
    } catch (error) {
        console.error('Error updating quantity:', error);
    }
}

async function removeFromCart(itemId) {
    try {
        const response = await apiCall(`/cart/${itemId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadCart();
            updateCartCount();
        }
    } catch (error) {
        console.error('Error removing item:', error);
    }
}

function proceedToCheckout() {
    window.location.href = '/checkout';
}

// Checkout page
async function loadCheckout() {
    const token = getToken();
    
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    try {
        const response = await apiCall('/cart');
        const items = await response.json();
        
        if (items.length === 0) {
            alert('Your cart is empty');
            window.location.href = '/cart';
            return;
        }
        
        const total = items.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
        
        const summary = document.getElementById('checkoutSummary');
        if (summary) {
            summary.innerHTML = `
                <h3>Order Items</h3>
                ${items.map(item => `
                    <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                        <span>${item.product.name} x ${item.quantity}</span>
                        <span>₹${item.product.price * item.quantity}</span>
                    </div>
                `).join('')}
                <hr style="margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; font-size: 1.3rem; font-weight: bold;">
                    <span>Total:</span>
                    <span style="color: var(--primary);">₹${total}</span>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading checkout:', error);
    }
}

async function placeOrder(event) {
    event.preventDefault();
    
    const address = document.getElementById('shippingAddress')?.value;
    const phone = document.getElementById('shippingPhone')?.value;
    const paymentMethod = document.getElementById('paymentMethod')?.value;
    
    try {
        const response = await apiCall('/orders', {
            method: 'POST',
            body: JSON.stringify({
                shipping_address: address,
                phone: phone,
                payment_method: paymentMethod
            })
        });
        
        if (response.ok) {
            const order = await response.json();
            alert(`Order placed successfully! Order ID: ${order.id}`);
            updateCartCount();
            window.location.href = '/';
        } else {
            const error = await response.json();
            alert(error.detail || 'Error placing order');
        }
    } catch (error) {
        console.error('Error placing order:', error);
        alert('Error placing order');
    }
}

// Auth functions
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('loginUsername')?.value;
    const password = document.getElementById('loginPassword')?.value;
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            setToken(data.access_token);
            alert('Login successful!');
            window.location.href = '/';
        } else {
            alert('Invalid credentials');
        }
    } catch (error) {
        console.error('Error logging in:', error);
        alert('Error logging in');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const email = document.getElementById('registerEmail')?.value;
    const username = document.getElementById('registerUsername')?.value;
    const fullName = document.getElementById('registerFullName')?.value;
    const phone = document.getElementById('registerPhone')?.value;
    const password = document.getElementById('registerPassword')?.value;
    
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email,
                username,
                full_name: fullName,
                phone,
                password
            })
        });
        
        if (response.ok) {
            alert('Registration successful! Please login.');
            window.location.href = '/login';
        } else {
            const error = await response.json();
            alert(error.detail || 'Error registering');
        }
    } catch (error) {
        console.error('Error registering:', error);
        alert('Error registering');
    }
}

// Admin functions
async function loadAdminDashboard() {
    const token = getToken();
    
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    try {
        // Load stats
        const productsRes = await fetch(`${API_URL}/products`);
        const products = await productsRes.json();
        
        const ordersRes = await apiCall('/admin/orders');
        const orders = await ordersRes.json();
        
        document.getElementById('totalProducts').textContent = products.length;
        document.getElementById('totalOrders').textContent = orders.length;
        
        const revenue = orders.reduce((sum, order) => sum + order.total_amount, 0);
        document.getElementById('totalRevenue').textContent = `₹${revenue}`;
        
        // Load orders table
        const ordersTable = document.getElementById('ordersTable');
        if (ordersTable) {
            ordersTable.innerHTML = orders.map(order => `
                <tr>
                    <td>${order.id}</td>
                    <td>₹${order.total_amount}</td>
                    <td>${order.status}</td>
                    <td>${order.payment_method}</td>
                    <td>${new Date(order.created_at).toLocaleDateString()}</td>
                </tr>
            `).join('');
        }
        
        // Load products table
        const productsTable = document.getElementById('productsTable');
        if (productsTable) {
            productsTable.innerHTML = products.map(product => `
                <tr>
                    <td>${product.id}</td>
                    <td>${product.name}</td>
                    <td>${product.category}</td>
                    <td>₹${product.price}</td>
                    <td>${product.stock}</td>
                    <td>
                        <button class="btn btn-secondary" style="padding: 0.3rem 0.6rem;" 
                                onclick="deleteProduct(${product.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading admin dashboard:', error);
    }
}

async function deleteProduct(productId) {
    if (!confirm('Are you sure you want to delete this product?')) return;
    
    try {
        const response = await apiCall(`/products/${productId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Product deleted successfully');
            loadAdminDashboard();
        }
    } catch (error) {
        console.error('Error deleting product:', error);
    }
}