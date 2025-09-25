// Custom JavaScript for IKr Platform

// Global utility functions
const IKR = {
    // Initialize all components
    init() {
        this.initTooltips();
        this.initAnimations();
        this.initForms();
        this.initNavigation();
    },

    // Initialize Bootstrap tooltips
    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    },

    // Initialize scroll animations
    initAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                }
            });
        }, observerOptions);

        // Observe all cards and feature elements
        document.querySelectorAll('.card, .feature-icon').forEach(el => {
            observer.observe(el);
        });
    },

    // Form enhancements
    initForms() {
        // Add loading state to form buttons
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                    submitBtn.disabled = true;
                }
            });
        });

        // Auto-format phone numbers
        document.querySelectorAll('input[type="tel"]').forEach(input => {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.startsWith('254')) {
                    value = '+' + value;
                } else if (value.startsWith('0')) {
                    value = '+254' + value.substring(1);
                }
                e.target.value = value;
            });
        });
    },

    // Navigation enhancements
    initNavigation() {
        // Highlight current page in navigation
        const currentPath = window.location.pathname;
        document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    },

    // Show success message
    showMessage(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    },

    // Format currency
    formatCurrency(amount, currency = 'KES') {
        return new Intl.NumberFormat('en-KE', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    // API helper
    async apiCall(url, options = {}) {
        const defaults = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };

        const config = { ...defaults, ...options };
        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    },

    // Get CSRF token
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    IKR.init();
});

// Shopping cart functionality
class ShoppingCart {
    constructor() {
        this.items = JSON.parse(localStorage.getItem('cart') || '[]');
        this.updateCartUI();
    }

    addItem(productId, quantity = 1, variant = null) {
        const existingItem = this.items.find(item => 
            item.productId === productId && item.variant === variant
        );

        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            this.items.push({ productId, quantity, variant, addedAt: Date.now() });
        }

        this.saveCart();
        this.updateCartUI();
        IKR.showMessage('Item added to cart!', 'success');
    }

    removeItem(productId, variant = null) {
        this.items = this.items.filter(item => 
            !(item.productId === productId && item.variant === variant)
        );
        this.saveCart();
        this.updateCartUI();
    }

    updateQuantity(productId, quantity, variant = null) {
        const item = this.items.find(item => 
            item.productId === productId && item.variant === variant
        );
        if (item) {
            item.quantity = Math.max(0, quantity);
            if (item.quantity === 0) {
                this.removeItem(productId, variant);
            } else {
                this.saveCart();
                this.updateCartUI();
            }
        }
    }

    clear() {
        this.items = [];
        this.saveCart();
        this.updateCartUI();
    }

    getItemCount() {
        return this.items.reduce((total, item) => total + item.quantity, 0);
    }

    saveCart() {
        localStorage.setItem('cart', JSON.stringify(this.items));
    }

    updateCartUI() {
        const cartBadge = document.querySelector('.cart-badge');
        if (cartBadge) {
            const count = this.getItemCount();
            cartBadge.textContent = count;
            cartBadge.style.display = count > 0 ? 'block' : 'none';
        }
    }
}

// Initialize shopping cart
window.cart = new ShoppingCart();

// Product quick view functionality
function showProductQuickView(productId) {
    // This would open a modal with product details
    // Implementation depends on your specific needs
    console.log('Quick view for product:', productId);
}

// Newsletter subscription
async function subscribeNewsletter(email) {
    try {
        await IKR.apiCall('/api/newsletter/subscribe/', {
            method: 'POST',
            body: { email }
        });
        IKR.showMessage('Successfully subscribed to newsletter!', 'success');
    } catch (error) {
        IKR.showMessage('Failed to subscribe. Please try again.', 'danger');
    }
}