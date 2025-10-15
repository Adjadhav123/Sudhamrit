// Mobile Enhancement JavaScript for Sudhamrit Dairy Farm

document.addEventListener('DOMContentLoaded', function() {
    
    // Mobile touch enhancements
    if (window.innerWidth <= 768) {
        // Improve touch targets on mobile
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            btn.style.minHeight = '44px';
            btn.style.minWidth = '44px';
        });
        
        // Add touch feedback for cards
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.98)';
            });
            
            card.addEventListener('touchend', function() {
                this.style.transform = 'scale(1)';
            });
        });
    }

    // Handle navbar collapse on mobile menu item click
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const navLinks = document.querySelectorAll('.nav-link:not(.dropdown-toggle)');
    
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 991) {
                const bootstrapCollapse = new bootstrap.Collapse(navbarCollapse, {
                    toggle: false
                });
                bootstrapCollapse.hide();
            }
        });
    });

    // Optimize image loading for mobile
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
    });

    // Add loading states for forms on mobile
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            }
        });
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Handle orientation change
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            window.scrollTo(0, window.scrollY);
        }, 100);
    });

    // Improve cart quantity controls for touch
    const quantityButtons = document.querySelectorAll('.quantity-btn');
    quantityButtons.forEach(btn => {
        btn.style.minHeight = '44px';
        btn.style.minWidth = '44px';
        btn.style.fontSize = '18px';
    });

    // Add swipe gesture for product cards (if applicable)
    let startX = null;
    let startY = null;

    document.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    });

    document.addEventListener('touchmove', function(e) {
        if (!startX || !startY) return;

        let diffX = startX - e.touches[0].clientX;
        let diffY = startY - e.touches[0].clientY;

        // Prevent horizontal scrolling on mobile
        if (Math.abs(diffX) > Math.abs(diffY)) {
            e.preventDefault();
        }
    });

    // Accessibility improvements for mobile
    const focusableElements = document.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    focusableElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.style.outline = '3px solid #22c55e';
            this.style.outlineOffset = '2px';
        });
        
        element.addEventListener('blur', function() {
            this.style.outline = '';
            this.style.outlineOffset = '';
        });
    });

    // Optimize performance for mobile devices
    if (/Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
        // Reduce animation duration for better performance
        const style = document.createElement('style');
        style.textContent = `
            *, *::before, *::after {
                animation-duration: 0.3s !important;
                transition-duration: 0.3s !important;
            }
        `;
        document.head.appendChild(style);
    }

    // Handle table responsiveness
    const tables = document.querySelectorAll('table:not(.table-responsive table)');
    tables.forEach(table => {
        if (!table.closest('.table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });

    // Add mobile-specific search behavior
    const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="search" i]');
    searchInputs.forEach(input => {
        // Prevent zoom on iOS
        input.style.fontSize = '16px';
        
        input.addEventListener('focus', function() {
            this.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    });

    // Handle modal responsiveness
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            if (window.innerWidth <= 768) {
                this.style.paddingLeft = '0';
                this.style.paddingRight = '0';
            }
        });
    });

    // Optimize cart calculations for mobile
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Debounce cart updates
    const cartUpdates = document.querySelectorAll('.quantity-btn');
    cartUpdates.forEach(btn => {
        btn.addEventListener('click', debounce(function() {
            // Cart update logic here
        }, 300));
    });

    // Enhanced dropdown functionality with better mobile support
    const mainProfileDropdown = document.querySelector('.nav-item.dropdown');
    const mainProfileToggle = document.querySelector('.nav-link.dropdown-toggle');
    const mainProfileMenu = document.querySelector('.dropdown-menu');
    const mainNavbarCollapse = document.querySelector('.navbar-collapse');
    
    if (mainProfileToggle && mainProfileMenu) {
        console.log('Setting up enhanced dropdown functionality'); // Debug
        
        // Function to initialize dropdown based on screen size
        function initializeDropdown() {
            const isMobile = window.innerWidth <= 991;
            
            if (!isMobile) {
                // Desktop mode - use Bootstrap default
                mainProfileToggle.setAttribute('data-bs-toggle', 'dropdown');
                mainProfileToggle.setAttribute('aria-expanded', 'false');
                
                // Clean up mobile event listeners by cloning the element
                const newToggle = mainProfileToggle.cloneNode(true);
                mainProfileToggle.parentNode.replaceChild(newToggle, mainProfileToggle);
                
                // Initialize Bootstrap dropdown
                try {
                    new bootstrap.Dropdown(newToggle);
                } catch (e) {
                    console.log('Bootstrap dropdown initialization failed:', e);
                }
                
            } else {
                // Mobile mode - custom implementation
                mainProfileToggle.removeAttribute('data-bs-toggle');
                
                // Add mobile click handler
                mainProfileToggle.addEventListener('click', handleMobileDropdownClick);
                
                // Add mobile touch handlers
                addMobileTouchHandlers();
                
                // Add outside click handler for mobile
                document.addEventListener('click', handleOutsideClick);
                
                // Handle navbar collapse events
                if (mainNavbarCollapse) {
                    mainNavbarCollapse.addEventListener('hidden.bs.collapse', hideMobileDropdown);
                    mainNavbarCollapse.addEventListener('shown.bs.collapse', hideMobileDropdown);
                }
            }
        }
        
        // Mobile dropdown click handler with touch support
        function handleMobileDropdownClick(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const isVisible = mainProfileMenu.classList.contains('show') || 
                            mainProfileMenu.style.display === 'block' ||
                            window.getComputedStyle(mainProfileMenu).display === 'block';
            
            console.log('Mobile dropdown clicked, currently visible:', isVisible);
            
            if (isVisible) {
                hideMobileDropdown();
            } else {
                showMobileDropdown();
            }
        }
        
        // Add touch event handlers for better mobile experience
        function addMobileTouchHandlers() {
            if (window.innerWidth <= 991) {
                // Add touch feedback
                mainProfileToggle.addEventListener('touchstart', function() {
                    this.style.transform = 'scale(0.98)';
                }, { passive: true });
                
                mainProfileToggle.addEventListener('touchend', function() {
                    this.style.transform = 'scale(1)';
                }, { passive: true });
                
                // Add touch feedback for dropdown items
                mainProfileMenu.querySelectorAll('.dropdown-item').forEach(item => {
                    item.addEventListener('touchstart', function() {
                        this.style.backgroundColor = 'rgba(34, 197, 94, 0.1)';
                    }, { passive: true });
                    
                    item.addEventListener('touchend', function() {
                        setTimeout(() => {
                            this.style.backgroundColor = '';
                        }, 150);
                    }, { passive: true });
                });
            }
        }
        
        // Show mobile dropdown
        function showMobileDropdown() {
            mainProfileMenu.classList.add('show');
            mainProfileMenu.style.display = 'block';
            mainProfileDropdown.classList.add('show');
            mainProfileToggle.setAttribute('aria-expanded', 'true');
            console.log('Mobile dropdown shown');
        }
        
        // Hide mobile dropdown
        function hideMobileDropdown() {
            mainProfileMenu.classList.remove('show');
            mainProfileMenu.style.display = 'none';
            mainProfileDropdown.classList.remove('show');
            mainProfileToggle.setAttribute('aria-expanded', 'false');
            console.log('Mobile dropdown hidden');
        }
        
        // Handle outside clicks
        function handleOutsideClick(e) {
            if (window.innerWidth <= 991 && !mainProfileDropdown.contains(e.target)) {
                hideMobileDropdown();
            }
        }
        
        // Initialize dropdown on page load
        initializeDropdown();
        
        // Handle menu item clicks for both desktop and mobile
        mainProfileMenu.querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', function() {
                if (window.innerWidth <= 991) {
                    hideMobileDropdown();
                    
                    // Close navbar on mobile if it's open
                    if (mainNavbarCollapse && mainNavbarCollapse.classList.contains('show')) {
                        const bootstrapCollapse = new bootstrap.Collapse(mainNavbarCollapse, {
                            toggle: false
                        });
                        bootstrapCollapse.hide();
                    }
                }
            });
        });
        
        // Handle window resize with debouncing
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                console.log('Window resized, reinitializing dropdown');
                hideMobileDropdown(); // Close any open dropdowns
                initializeDropdown(); // Reinitialize based on new screen size
            }, 250);
        });
        
    } else {
        console.log('Profile dropdown elements not found'); // Debug
    }

    // Profile dropdown specific improvements
    const profileDropdownToggle = document.querySelector('.nav-item.dropdown .dropdown-toggle');
    if (profileDropdownToggle) {
        // Truncate long usernames on very small screens
        if (window.innerWidth <= 576) {
            const usernameSpan = profileDropdownToggle.querySelector('span');
            if (usernameSpan && usernameSpan.textContent.length > 12) {
                usernameSpan.textContent = usernameSpan.textContent.substring(0, 10) + '...';
            }
        }
    }
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js').then(function(registration) {
            console.log('SW registered: ', registration);
        }).catch(function(registrationError) {
            console.log('SW registration failed: ', registrationError);
        });
    });
}