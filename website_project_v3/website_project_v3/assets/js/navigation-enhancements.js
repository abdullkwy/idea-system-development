
document.addEventListener('DOMContentLoaded', () => {
    // Sticky Navigation
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 100) {
                header.classList.add('sticky');
            } else {
                header.classList.remove('sticky');
            }
        });
    }

    // Scroll Progress Indicator
    const progressBar = document.querySelector('.scroll-progress-bar');
    if (progressBar) {
        window.addEventListener('scroll', () => {
            const totalHeight = document.body.scrollHeight - window.innerHeight;
            const progress = (window.scrollY / totalHeight) * 100;
            progressBar.style.width = progress + '%';
        });
    }

    // Mobile Navigation Toggle
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navMenu = document.querySelector('.nav-menu');
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            mobileToggle.querySelector('i').classList.toggle('fa-bars');
            mobileToggle.querySelector('i').classList.toggle('fa-times');
        });

        // Close mobile menu when a link is clicked
        navMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                mobileToggle.querySelector('i').classList.remove('fa-times');
                mobileToggle.querySelector('i').classList.add('fa-bars');
            });
        });
    }

    // Dropdown menu toggle for mobile
    const dropdowns = document.querySelectorAll('.nav-menu .dropdown > a');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) { // Adjust breakpoint as needed
                e.preventDefault();
                const dropdownMenu = dropdown.nextElementSibling;
                if (dropdownMenu) {
                    dropdownMenu.classList.toggle('active');
                    dropdown.querySelector('i').classList.toggle('fa-chevron-down');
                    dropdown.querySelector('i').classList.toggle('fa-chevron-up');
                }
            }
        });
    });

    // Quick Search (Placeholder - integrate with actual search functionality later)
    const searchInput = document.querySelector('.quick-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            console.log('Quick search query:', e.target.value);
            // Implement actual search logic here
        });
    }
});


