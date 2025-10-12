// Mobile Optimizations JavaScript
// جافاسكريبت تحسينات الأجهزة المحمولة

document.addEventListener('DOMContentLoaded', function() {
    // Initialize mobile optimizations
    initMobileOptimizations();
    setupTouchGestures();
    optimizeForMobile();
    handleOrientationChange();
});

// Initialize mobile optimizations
function initMobileOptimizations() {
    // Check if device is mobile
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isTablet = /iPad|Android/i.test(navigator.userAgent) && window.innerWidth >= 768;
    
    if (isMobile) {
        document.body.classList.add('mobile-device');
    }
    
    if (isTablet) {
        document.body.classList.add('tablet-device');
    }
    
    // Optimize viewport for mobile
    optimizeViewport();
    
    // Setup mobile navigation
    setupMobileNavigation();
    
    // Optimize forms for mobile
    optimizeMobileForms();
    
    // Setup touch-friendly interactions
    setupTouchInteractions();
}

// Optimize viewport for mobile
function optimizeViewport() {
    // Prevent zoom on input focus (iOS)
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            const viewport = document.querySelector('meta[name="viewport"]');
            if (viewport) {
                viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
            }
        });
        
        input.addEventListener('blur', function() {
            const viewport = document.querySelector('meta[name="viewport"]');
            if (viewport) {
                viewport.setAttribute('content', 'width=device-width, initial-scale=1.0');
            }
        });
    });
}

// Setup mobile navigation
function setupMobileNavigation() {
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    const dropdowns = document.querySelectorAll('.dropdown');
    
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            mobileToggle.classList.toggle('active');
            
            // Toggle hamburger animation
            const icon = mobileToggle.querySelector('i');
            if (navMenu.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
            
            // Prevent body scroll when menu is open
            document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
        });
        
        // Close menu when clicking on nav links
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 992) {
                    navMenu.classList.remove('active');
                    mobileToggle.classList.remove('active');
                    document.body.style.overflow = '';
                    
                    const icon = mobileToggle.querySelector('i');
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            });
        });
        
        // Handle dropdown menus on mobile
        dropdowns.forEach(dropdown => {
            const dropdownLink = dropdown.querySelector('.nav-link');
            const dropdownMenu = dropdown.querySelector('.dropdown-menu');
            
            if (dropdownLink && dropdownMenu) {
                dropdownLink.addEventListener('click', function(e) {
                    if (window.innerWidth <= 992) {
                        e.preventDefault();
                        dropdown.classList.toggle('active');
                        
                        // Animate dropdown
                        if (dropdown.classList.contains('active')) {
                            dropdownMenu.style.maxHeight = dropdownMenu.scrollHeight + 'px';
                        } else {
                            dropdownMenu.style.maxHeight = '0';
                        }
                    }
                });
            }
        });
    }
}

// Optimize forms for mobile
function optimizeMobileForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            // Add mobile-specific attributes
            if (input.type === 'email') {
                input.setAttribute('autocomplete', 'email');
                input.setAttribute('inputmode', 'email');
            }
            
            if (input.type === 'tel') {
                input.setAttribute('autocomplete', 'tel');
                input.setAttribute('inputmode', 'tel');
            }
            
            if (input.type === 'number') {
                input.setAttribute('inputmode', 'numeric');
            }
            
            // Improve focus handling on mobile
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
                
                // Scroll input into view on mobile
                if (window.innerWidth <= 768) {
                    setTimeout(() => {
                        this.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                    }, 300);
                }
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
            });
        });
    });
}

// Setup touch-friendly interactions
function setupTouchInteractions() {
    // Add touch feedback to buttons
    const buttons = document.querySelectorAll('.btn, button');
    
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.classList.add('touch-active');
        });
        
        button.addEventListener('touchend', function() {
            setTimeout(() => {
                this.classList.remove('touch-active');
            }, 150);
        });
    });
    
    // Add touch feedback to cards
    const cards = document.querySelectorAll('.service-card, .team-card, .testimonial-card');
    
    cards.forEach(card => {
        card.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
        });
        
        card.addEventListener('touchend', function() {
            this.style.transform = '';
        });
    });
}

// Setup touch gestures
function setupTouchGestures() {
    let startX = 0;
    let startY = 0;
    let endX = 0;
    let endY = 0;
    
    // Swipe gestures for navigation
    document.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchend', function(e) {
        endX = e.changedTouches[0].clientX;
        endY = e.changedTouches[0].clientY;
        
        const diffX = startX - endX;
        const diffY = startY - endY;
        
        // Check if it's a horizontal swipe
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
            if (diffX > 0) {
                // Swipe left - could trigger next action
                handleSwipeLeft();
            } else {
                // Swipe right - could trigger previous action
                handleSwipeRight();
            }
        }
    });
    
    // Pull to refresh gesture
    let startY_refresh = 0;
    let isPulling = false;
    
    document.addEventListener('touchstart', function(e) {
        if (window.scrollY === 0) {
            startY_refresh = e.touches[0].clientY;
            isPulling = true;
        }
    });
    
    document.addEventListener('touchmove', function(e) {
        if (isPulling && window.scrollY === 0) {
            const currentY = e.touches[0].clientY;
            const pullDistance = currentY - startY_refresh;
            
            if (pullDistance > 100) {
                // Show pull to refresh indicator
                showPullToRefreshIndicator();
            }
        }
    });
    
    document.addEventListener('touchend', function(e) {
        if (isPulling) {
            const endY_refresh = e.changedTouches[0].clientY;
            const pullDistance = endY_refresh - startY_refresh;
            
            if (pullDistance > 100) {
                // Trigger refresh
                triggerRefresh();
            }
            
            isPulling = false;
            hidePullToRefreshIndicator();
        }
    });
}

// Handle swipe gestures
function handleSwipeLeft() {
    // Could be used for navigation or carousel
    console.log('Swiped left');
}

function handleSwipeRight() {
    // Could be used for navigation or carousel
    console.log('Swiped right');
}

// Pull to refresh functionality
function showPullToRefreshIndicator() {
    let indicator = document.querySelector('.pull-to-refresh-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'pull-to-refresh-indicator';
        indicator.innerHTML = '<i class="fas fa-sync-alt"></i> اسحب للتحديث';
        document.body.insertBefore(indicator, document.body.firstChild);
    }
    indicator.style.display = 'block';
}

function hidePullToRefreshIndicator() {
    const indicator = document.querySelector('.pull-to-refresh-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

function triggerRefresh() {
    // Refresh page content
    window.location.reload();
}

// Handle orientation change
function handleOrientationChange() {
    window.addEventListener('orientationchange', function() {
        // Delay to ensure orientation change is complete
        setTimeout(() => {
            // Recalculate dimensions
            optimizeForMobile();
            
            // Adjust chat popup size
            adjustChatPopupForOrientation();
            
            // Trigger resize event
            window.dispatchEvent(new Event('resize'));
        }, 500);
    });
}

// Optimize for mobile devices
function optimizeForMobile() {
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // Optimize images for mobile
        optimizeImagesForMobile();
        
        // Adjust font sizes
        adjustFontSizesForMobile();
        
        // Optimize animations
        optimizeAnimationsForMobile();
    }
}

// Optimize images for mobile
function optimizeImagesForMobile() {
    const images = document.querySelectorAll('img');
    
    images.forEach(img => {
        // Add lazy loading
        if (!img.hasAttribute('loading')) {
            img.setAttribute('loading', 'lazy');
        }
        
        // Optimize image quality for mobile
        if (img.src && !img.dataset.optimized) {
            img.dataset.optimized = 'true';
        }
    });
}

// Adjust font sizes for mobile
function adjustFontSizesForMobile() {
    const root = document.documentElement;
    
    if (window.innerWidth <= 480) {
        root.style.setProperty('--base-font-size', '14px');
    } else if (window.innerWidth <= 768) {
        root.style.setProperty('--base-font-size', '15px');
    } else {
        root.style.setProperty('--base-font-size', '16px');
    }
}

// Optimize animations for mobile
function optimizeAnimationsForMobile() {
    const isMobile = window.innerWidth <= 768;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    if (isMobile || prefersReducedMotion) {
        // Reduce animation duration
        document.documentElement.style.setProperty('--animation-duration', '0.2s');
        
        // Disable complex animations
        const complexAnimations = document.querySelectorAll('.floating-shape, .parallax-element');
        complexAnimations.forEach(element => {
            element.style.animation = 'none';
            element.style.transform = 'none';
        });
    }
}

// Adjust chat popup for orientation
function adjustChatPopupForOrientation() {
    const chatPopup = document.querySelector('.chat-popup');
    
    if (chatPopup && window.innerWidth <= 768) {
        if (window.innerHeight < window.innerWidth) {
            // Landscape mode
            chatPopup.style.height = '90vh';
            chatPopup.style.width = '70%';
        } else {
            // Portrait mode
            chatPopup.style.height = '75vh';
            chatPopup.style.width = '95%';
        }
    }
}

// Performance optimizations for mobile
function optimizePerformanceForMobile() {
    // Debounce scroll events
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        
        scrollTimeout = setTimeout(() => {
            // Handle scroll events
            updateScrollProgress();
        }, 16); // ~60fps
    });
    
    // Optimize resize events
    let resizeTimeout;
    window.addEventListener('resize', function() {
        if (resizeTimeout) {
            clearTimeout(resizeTimeout);
        }
        
        resizeTimeout = setTimeout(() => {
            optimizeForMobile();
        }, 250);
    });
}

// Update scroll progress
function updateScrollProgress() {
    const scrollProgress = document.querySelector('.scroll-progress-bar');
    if (scrollProgress) {
        const scrollTop = window.pageYOffset;
        const docHeight = document.body.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        
        scrollProgress.style.width = scrollPercent + '%';
    }
}

// Initialize performance optimizations
optimizePerformanceForMobile();

// Add CSS for touch feedback
const touchStyles = document.createElement('style');
touchStyles.textContent = `
    .touch-active {
        opacity: 0.7;
        transform: scale(0.95);
        transition: all 0.1s ease;
    }
    
    .pull-to-refresh-indicator {
        position: fixed;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        background: var(--primary-color);
        color: white;
        padding: 10px 20px;
        border-radius: 0 0 10px 10px;
        font-size: 14px;
        z-index: 9999;
        display: none;
    }
    
    .pull-to-refresh-indicator i {
        animation: spin 1s linear infinite;
        margin-left: 5px;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @media (max-width: 768px) {
        .dropdown-menu {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }
        
        .dropdown.active .dropdown-menu {
            max-height: 300px;
        }
    }
`;

document.head.appendChild(touchStyles);

