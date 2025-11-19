// ==========================================
// CONFIGURACIÓN Y ESTADO GLOBAL
// ==========================================

const API_URL = 'http://localhost:5000/api';

const state = {
    currentUser: null,
    users: [],
    products: [],
    cart: [],
    pagos: [],
    facturas: []
};

// ==========================================
// INICIALIZACIÓN
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    initApp();
    setupEventListeners();
    loadInitialData();
});

function initApp() {
    // Cargar datos del localStorage
    const savedUsers = localStorage.getItem('users');
    const savedProducts = localStorage.getItem('products');
    const savedCart = localStorage.getItem('cart');
    const savedCurrentUser = localStorage.getItem('currentUser');

    if (savedUsers) state.users = JSON.parse(savedUsers);
    if (savedProducts) state.products = JSON.parse(savedProducts);
    if (savedCart) state.cart = JSON.parse(savedCart);
    if (savedCurrentUser) state.currentUser = JSON.parse(savedCurrentUser);

    // Si no hay usuarios, crear uno por defecto
    if (state.users.length === 0) {
        state.users.push({
            id: 1,
            nombre: 'Juan Pérez',
            email: 'juan@example.com'
        });
        saveToLocalStorage('users');
    }

    // Si no hay usuario actual, usar el primero
    if (!state.currentUser) {
        state.currentUser = state.users[0];
        saveToLocalStorage('currentUser');
    }

    // Si no hay productos, crear algunos por defecto
    if (state.products.length === 0) {
        createDefaultProducts();
    }

    updateUserDisplay();
    updateCartCount();
}

function createDefaultProducts() {
    const defaultProducts = [
        { nombre: 'Laptop Dell XPS 13', categoria: 'Electrónica', precio: 1299.99, stock: 5, descripcion: 'Portátil ultradelgada con procesador Intel i7', emoji: '💻' },
        { nombre: 'iPhone 14 Pro', categoria: 'Electrónica', precio: 999.99, stock: 8, descripcion: 'Smartphone de última generación', emoji: '📱' },
        { nombre: 'Auriculares Sony WH-1000XM5', categoria: 'Electrónica', precio: 399.99, stock: 12, descripcion: 'Cancelación de ruido premium', emoji: '🎧' },
        { nombre: 'Camiseta Nike Dri-FIT', categoria: 'Ropa', precio: 34.99, stock: 25, descripcion: 'Camiseta deportiva transpirable', emoji: '👕' },
        { nombre: 'Zapatillas Adidas Ultraboost', categoria: 'Ropa', precio: 179.99, stock: 15, descripcion: 'Zapatillas para running', emoji: '👟' },
        { nombre: 'Jeans Levi\'s 501', categoria: 'Ropa', precio: 89.99, stock: 20, descripcion: 'Jeans clásicos de corte recto', emoji: '👖' },
        { nombre: 'Cafetera Nespresso', categoria: 'Hogar', precio: 149.99, stock: 10, descripcion: 'Cafetera de cápsulas automática', emoji: '☕' },
        { nombre: 'Aspiradora Robot Roomba', categoria: 'Hogar', precio: 299.99, stock: 7, descripcion: 'Limpieza automática inteligente', emoji: '🤖' },
        { nombre: 'Lámpara LED Philips Hue', categoria: 'Hogar', precio: 59.99, stock: 18, descripcion: 'Iluminación inteligente RGB', emoji: '💡' },
        { nombre: 'Pelota de Fútbol Nike', categoria: 'Deportes', precio: 29.99, stock: 30, descripcion: 'Pelota oficial de competición', emoji: '⚽' },
        { nombre: 'Bicicleta de Montaña Trek', categoria: 'Deportes', precio: 899.99, stock: 4, descripcion: 'MTB con suspensión completa', emoji: '🚴' },
        { nombre: 'Pesas Ajustables 20kg', categoria: 'Deportes', precio: 149.99, stock: 12, descripcion: 'Set de pesas para entrenamiento', emoji: '🏋️' },
        { nombre: 'El Quijote - Cervantes', categoria: 'Libros', precio: 19.99, stock: 50, descripcion: 'Clásico de la literatura española', emoji: '📖' },
        { nombre: 'Sapiens - Yuval Harari', categoria: 'Libros', precio: 24.99, stock: 35, descripcion: 'Historia de la humanidad', emoji: '📚' },
        { nombre: 'Harry Potter Collection', categoria: 'Libros', precio: 79.99, stock: 15, descripcion: 'Colección completa de 7 libros', emoji: '🧙' }
    ];

    state.products = defaultProducts.map((prod, index) => ({
        id: index + 1,
        ...prod
    }));

    saveToLocalStorage('products');
}

// ==========================================
// EVENT LISTENERS
// ==========================================

function setupEventListeners() {
    // Tabs navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // Usuario
    document.getElementById('btnCambiarUsuario').addEventListener('click', openUserModal);
    document.getElementById('formNuevoUsuario').addEventListener('submit', createNewUser);

    // Productos
    document.getElementById('searchProduct').addEventListener('input', filterProducts);
    document.getElementById('categoryFilter').addEventListener('change', filterProducts);

    // Carrito
    document.getElementById('btnVaciarCarrito').addEventListener('click', clearCart);
    document.getElementById('btnProcederPago').addEventListener('click', proceedToPayment);

    // Pagos
    document.getElementById('btnCancelarPago').addEventListener('click', cancelPayment);
    document.getElementById('formPago').addEventListener('submit', processPayment);
    document.getElementById('btnRefreshPagos').addEventListener('click', loadPagos);

    // Facturas
    document.getElementById('btnRefreshFacturas').addEventListener('click', loadFacturas);

    // Admin
    document.getElementById('formProducto').addEventListener('submit', addProduct);

    // Modals
    document.querySelectorAll('.modal-close').forEach(el => {
        el.addEventListener('click', () => closeModal(el.closest('.modal')));
    });

    // Click fuera del modal para cerrar
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal(modal);
        });
    });
}

// ==========================================
// NAVEGACIÓN DE TABS
// ==========================================

function switchTab(tabName) {
    // Actualizar botones
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    // Actualizar contenido
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');

    // Cargar datos según la tab
    switch(tabName) {
        case 'productos':
            renderProducts();
            break;
        case 'carrito':
            renderCart();
            break;
        case 'pagos':
            loadPagos();
            break;
        case 'facturas':
            loadFacturas();
            break;
        case 'admin':
            renderAdminProducts();
            break;
    }
}

// ==========================================
// GESTIÓN DE USUARIOS
// ==========================================

function openUserModal() {
    const modal = document.getElementById('modalUsuario');
    renderUsersList();
    modal.classList.add('active');
}

function renderUsersList() {
    const container = document.getElementById('usersList');
    container.innerHTML = state.users.map(user => `
        <div class="user-item ${state.currentUser?.id === user.id ? 'active' : ''}" 
             onclick="selectUser(${user.id})">
            <div class="user-name">${user.nombre}</div>
            <div class="user-email">${user.email}</div>
        </div>
    `).join('');
}

function selectUser(userId) {
    state.currentUser = state.users.find(u => u.id === userId);
    saveToLocalStorage('currentUser');
    updateUserDisplay();
    closeModal(document.getElementById('modalUsuario'));
    showToast('Usuario cambiado correctamente', 'success');
}

function createNewUser(e) {
    e.preventDefault();
    const nombre = document.getElementById('newUserName').value;
    const email = document.getElementById('newUserEmail').value;

    const newUser = {
        id: Math.max(...state.users.map(u => u.id), 0) + 1,
        nombre,
        email
    };

    state.users.push(newUser);
    saveToLocalStorage('users');
    
    e.target.reset();
    renderUsersList();
    showToast('Usuario creado correctamente', 'success');
}

function updateUserDisplay() {
    document.getElementById('userName').textContent = 
        `Usuario: ${state.currentUser?.nombre || 'Invitado'}`;
}

// ==========================================
// GESTIÓN DE PRODUCTOS
// ==========================================

function renderProducts() {
    const container = document.getElementById('productGrid');
    const filteredProducts = getFilteredProducts();

    if (filteredProducts.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <div class="empty-state-icon">🔍</div>
                <p>No se encontraron productos</p>
            </div>
        `;
        return;
    }

    container.innerHTML = filteredProducts.map(product => `
        <div class="product-card">
            <div class="product-image">${product.emoji || '📦'}</div>
            <div class="product-info">
                <div class="product-category">${product.categoria}</div>
                <div class="product-name">${product.nombre}</div>
                <div class="product-description">${product.descripcion}</div>
                <div class="product-footer">
                    <div>
                        <div class="product-price">$${product.precio.toFixed(2)}</div>
                        <div class="product-stock ${product.stock === 0 ? 'out' : product.stock < 5 ? 'low' : ''}">
                            ${product.stock === 0 ? 'Agotado' : `Stock: ${product.stock}`}
                        </div>
                    </div>
                    <button class="btn btn-primary btn-sm" 
                            onclick="addToCart(${product.id})"
                            ${product.stock === 0 ? 'disabled' : ''}>
                        🛒 Agregar
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function filterProducts() {
    renderProducts();
}

function getFilteredProducts() {
    const searchTerm = document.getElementById('searchProduct').value.toLowerCase();
    const category = document.getElementById('categoryFilter').value;

    return state.products.filter(product => {
        const matchesSearch = product.nombre.toLowerCase().includes(searchTerm) ||
                            product.descripcion.toLowerCase().includes(searchTerm);
        const matchesCategory = !category || product.categoria === category;
        return matchesSearch && matchesCategory;
    });
}

// ==========================================
// GESTIÓN DEL CARRITO
// ==========================================

function addToCart(productId) {
    const product = state.products.find(p => p.id === productId);
    if (!product || product.stock === 0) return;

    const cartItem = state.cart.find(item => item.id === productId);

    if (cartItem) {
        if (cartItem.quantity < product.stock) {
            cartItem.quantity++;
            showToast('Cantidad actualizada', 'success');
        } else {
            showToast('Stock insuficiente', 'warning');
            return;
        }
    } else {
        state.cart.push({
            id: product.id,
            nombre: product.nombre,
            precio: product.precio,
            emoji: product.emoji,
            quantity: 1
        });
        showToast('Producto agregado al carrito', 'success');
    }

    saveToLocalStorage('cart');
    updateCartCount();
    renderProducts(); // Actualizar vista de productos
}

function removeFromCart(productId) {
    state.cart = state.cart.filter(item => item.id !== productId);
    saveToLocalStorage('cart');
    updateCartCount();
    renderCart();
    showToast('Producto eliminado del carrito', 'info');
}

function updateQuantity(productId, change) {
    const cartItem = state.cart.find(item => item.id === productId);
    const product = state.products.find(p => p.id === productId);

    if (!cartItem || !product) return;

    const newQuantity = cartItem.quantity + change;

    if (newQuantity <= 0) {
        removeFromCart(productId);
        return;
    }

    if (newQuantity > product.stock) {
        showToast('Stock insuficiente', 'warning');
        return;
    }

    cartItem.quantity = newQuantity;
    saveToLocalStorage('cart');
    renderCart();
}

function renderCart() {
    const container = document.getElementById('cartItems');

    if (state.cart.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🛒</div>
                <p>Tu carrito está vacío</p>
                <button class="btn btn-primary mt-2" onclick="switchTab('productos')">
                    Ir a la tienda
                </button>
            </div>
        `;
        updateCartSummary(0, 0, 0);
        return;
    }

    container.innerHTML = state.cart.map(item => `
        <div class="cart-item">
            <div class="cart-item-image">${item.emoji || '📦'}</div>
            <div class="cart-item-info">
                <div class="cart-item-name">${item.nombre}</div>
                <div class="cart-item-price">$${item.precio.toFixed(2)} c/u</div>
                <div class="cart-item-controls">
                    <button class="qty-btn" onclick="updateQuantity(${item.id}, -1)">−</button>
                    <span class="qty-display">${item.quantity}</span>
                    <button class="qty-btn" onclick="updateQuantity(${item.id}, 1)">+</button>
                </div>
            </div>
            <div class="cart-item-actions">
                <div class="cart-item-total">$${(item.precio * item.quantity).toFixed(2)}</div>
                <button class="btn btn-danger btn-sm" onclick="removeFromCart(${item.id})">
                    🗑️ Eliminar
                </button>
            </div>
        </div>
    `).join('');

    const subtotal = state.cart.reduce((sum, item) => sum + (item.precio * item.quantity), 0);
    const tax = subtotal * 0.12;
    const total = subtotal + tax;

    updateCartSummary(subtotal, tax, total);
}

function updateCartSummary(subtotal, tax, total) {
    document.getElementById('cartSubtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('cartTax').textContent = `$${tax.toFixed(2)}`;
    document.getElementById('cartTotal').textContent = `$${total.toFixed(2)}`;
}

function updateCartCount() {
    const count = state.cart.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById('cartCount').textContent = count;
}

function clearCart() {
    if (state.cart.length === 0) return;

    showConfirm(
        'Vaciar carrito',
        '¿Estás seguro de que deseas vaciar el carrito?',
        () => {
            state.cart = [];
            saveToLocalStorage('cart');
            updateCartCount();
            renderCart();
            showToast('Carrito vaciado', 'info');
        }
    );
}

// ==========================================
// GESTIÓN DE PAGOS
// ==========================================

function proceedToPayment() {
    if (state.cart.length === 0) {
        showToast('El carrito está vacío', 'warning');
        return;
    }

    if (!state.currentUser) {
        showToast('Debes seleccionar un usuario', 'warning');
        openUserModal();
        return;
    }

    const total = state.cart.reduce((sum, item) => sum + (item.precio * item.quantity), 0) * 1.12;
    const ordenId = `ORD-${Date.now()}`;

    document.getElementById('ordenId').value = ordenId;
    document.getElementById('montoTotal').value = `$${total.toFixed(2)}`;
    document.getElementById('paymentForm').style.display = 'block';

    switchTab('pagos');
    
    // Scroll al formulario
    setTimeout(() => {
        document.getElementById('paymentForm').scrollIntoView({ behavior: 'smooth' });
    }, 300);
}

function cancelPayment() {
    document.getElementById('paymentForm').style.display = 'none';
    document.getElementById('formPago').reset();
}

async function processPayment(e) {
    e.preventDefault();

    const ordenId = document.getElementById('ordenId').value;
    const metodoPago = document.getElementById('metodoPago').value;
    const total = state.cart.reduce((sum, item) => sum + (item.precio * item.quantity), 0) * 1.12;

    const items = state.cart.map(item => ({
        nombre: item.nombre,
        cantidad: item.quantity,
        precio: item.precio
    }));

    try {
        const response = await fetch(`${API_URL}/pagos/completo`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                orden_id: ordenId,
                usuario_id: state.currentUser.id,
                monto_total: total,
                metodo_pago: metodoPago,
                items: items
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Actualizar stock
            state.cart.forEach(cartItem => {
                const product = state.products.find(p => p.id === cartItem.id);
                if (product) {
                    product.stock -= cartItem.quantity;
                }
            });
            saveToLocalStorage('products');

            // Vaciar carrito
            state.cart = [];
            saveToLocalStorage('cart');
            updateCartCount();

            // Ocultar formulario
            cancelPayment();

            // Mostrar éxito
            showToast('¡Pago procesado exitosamente!', 'success');
            showToast(`Factura: ${data.factura.numero_factura}`, 'info');

            // Recargar lista de pagos
            loadPagos();
        } else {
            showToast(data.error || 'Error al procesar el pago', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error de conexión con el servidor', 'error');
    }
}

async function loadPagos() {
    try {
        const response = await fetch(`${API_URL}/pagos`);
        const pagos = await response.json();

        const container = document.getElementById('pagosList');

        if (!Array.isArray(pagos) || pagos.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">💳</div>
                    <p>No hay pagos registrados</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Orden</th>
                        <th>Usuario</th>
                        <th>Monto</th>
                        <th>Método</th>
                        <th>Estado</th>
                        <th>Fecha</th>
                    </tr>
                </thead>
                <tbody>
                    ${pagos.map(pago => `
                        <tr>
                            <td>#${pago.id}</td>
                            <td>${pago.orden_id}</td>
                            <td>Usuario ${pago.usuario_id}</td>
                            <td>$${pago.monto_total.toFixed(2)}</td>
                            <td>${formatMetodoPago(pago.metodo_pago)}</td>
                            <td><span class="badge badge-${pago.estado}">${pago.estado}</span></td>
                            <td>${formatDate(pago.fecha_creacion)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al cargar los pagos', 'error');
    }
}

async function loadFacturas() {
    try {
        const response = await fetch(`${API_URL}/facturas`);
        const facturas = await response.json();

        const container = document.getElementById('facturasList');

        if (!Array.isArray(facturas) || facturas.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📄</div>
                    <p>No hay facturas generadas</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Número</th>
                        <th>Orden</th>
                        <th>Usuario</th>
                        <th>Subtotal</th>
                        <th>Impuesto</th>
                        <th>Total</th>
                        <th>Fecha</th>
                    </tr>
                </thead>
                <tbody>
                    ${facturas.map(factura => `
                        <tr>
                            <td><strong>${factura.numero_factura}</strong></td>
                            <td>${factura.orden_id}</td>
                            <td>Usuario ${factura.usuario_id}</td>
                            <td>$${factura.subtotal.toFixed(2)}</td>
                            <td>$${factura.impuesto.toFixed(2)}</td>
                            <td><strong>$${factura.monto_total.toFixed(2)}</strong></td>
                            <td>${formatDate(factura.fecha_emision)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al cargar las facturas', 'error');
    }
}

// ==========================================
// ADMINISTRACIÓN DE PRODUCTOS
// ==========================================

function addProduct(e) {
    e.preventDefault();

    const emojis = ['📦', '🎁', '🛍️', '📱', '💻', '🎧', '👕', '👟', '☕', '📚'];
    
    const newProduct = {
        id: Math.max(...state.products.map(p => p.id), 0) + 1,
        nombre: document.getElementById('prodNombre').value,
        categoria: document.getElementById('prodCategoria').value,
        precio: parseFloat(document.getElementById('prodPrecio').value),
        stock: parseInt(document.getElementById('prodStock').value),
        descripcion: document.getElementById('prodDescripcion').value,
        emoji: emojis[Math.floor(Math.random() * emojis.length)]
    };

    state.products.push(newProduct);
    saveToLocalStorage('products');

    e.target.reset();
    renderAdminProducts();
    renderProducts();
    showToast('Producto agregado correctamente', 'success');
}

function renderAdminProducts() {
    const container = document.getElementById('adminProductList');

    if (state.products.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📦</div>
                <p>No hay productos en el inventario</p>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Categoría</th>
                    <th>Precio</th>
                    <th>Stock</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                ${state.products.map(product => `
                    <tr>
                        <td>#${product.id}</td>
                        <td>${product.emoji} ${product.nombre}</td>
                        <td>${product.categoria}</td>
                        <td>$${product.precio.toFixed(2)}</td>
                        <td class="${product.stock === 0 ? 'text-danger' : product.stock < 5 ? 'text-warning' : ''}">
                            ${product.stock}
                        </td>
                        <td>
                            <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})">
                                🗑️ Eliminar
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function deleteProduct(productId) {
    showConfirm(
        'Eliminar producto',
        '¿Estás seguro de que deseas eliminar este producto?',
        () => {
            state.products = state.products.filter(p => p.id !== productId);
            state.cart = state.cart.filter(item => item.id !== productId);
            saveToLocalStorage('products');
            saveToLocalStorage('cart');
            renderAdminProducts();
            renderProducts();
            updateCartCount();
            showToast('Producto eliminado', 'info');
        }
    );
}

// ==========================================
// UTILIDADES
// ==========================================

function saveToLocalStorage(key) {
    localStorage.setItem(key, JSON.stringify(state[key]));
}

function loadInitialData() {
    renderProducts();
    renderCart();
}

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatMetodoPago(metodo) {
    const map = {
        'tarjeta_credito': 'Tarjeta de Crédito',
        'tarjeta_debito': 'Tarjeta de Débito',
        'paypal': 'PayPal',
        'transferencia': 'Transferencia'
    };
    return map[metodo] || metodo;
}

// ==========================================
// MODALS Y NOTIFICACIONES
// ==========================================

function closeModal(modal) {
    modal.classList.remove('active');
}

function showConfirm(title, message, onConfirm) {
    const modal = document.getElementById('modalConfirm');
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmMessage').textContent = message;

    const btnOk = document.getElementById('btnConfirmOk');
    const btnCancel = document.getElementById('btnConfirmCancel');

    const handleOk = () => {
        onConfirm();
        cleanup();
    };

    const handleCancel = () => {
        cleanup();
    };

    const cleanup = () => {
        closeModal(modal);
        btnOk.removeEventListener('click', handleOk);
        btnCancel.removeEventListener('click', handleCancel);
    };

    btnOk.addEventListener('click', handleOk);
    btnCancel.addEventListener('click', handleCancel);

    modal.classList.add('active');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };

    toast.innerHTML = `
        <span style="font-size: 1.5rem;">${icons[type]}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}