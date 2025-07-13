// Nextwave Company Website - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initThemeToggle();
    initSearch();
    initScrollToTop();
    initAnimations();
    initContactForm();
    initJobFilters();
    initBlogFilters();
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
});

// Theme Toggle Functionality
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            setTheme(newTheme);
            
            // Send theme preference to server
            fetch('/api/toggle-theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ theme: newTheme })
            });
        });
    }
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Global Search Functionality
function initSearch() {
    const searchInput = document.getElementById('globalSearch');
    const searchBtn = document.getElementById('searchBtn');
    const searchResults = document.getElementById('searchResults');
    
    if (searchInput && searchBtn && searchResults) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value);
            }, 300);
        });
        
        searchBtn.addEventListener('click', function() {
            performSearch(searchInput.value);
        });
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch(this.value);
            }
        });
    }
}

function performSearch(query) {
    const searchResults = document.getElementById('searchResults');
    
    if (!query.trim()) {
        searchResults.innerHTML = '';
        return;
    }
    
    // Show loading spinner
    searchResults.innerHTML = '<div class="text-center"><div class="loading-spinner"></div></div>';
    
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data.results);
        })
        .catch(error => {
            console.error('Search error:', error);
            searchResults.innerHTML = '<div class="text-center text-danger">Search failed. Please try again.</div>';
        });
}

function displaySearchResults(results) {
    const searchResults = document.getElementById('searchResults');
    
    if (results.length === 0) {
        searchResults.innerHTML = '<div class="text-center text-muted">No results found</div>';
        return;
    }
    
    const resultHtml = results.map(result => `
        <div class="search-result-item">
            <a href="${result.url}" onclick="closeSearchDropdown()">
                <div class="fw-bold">${result.title}</div>
                <div class="search-result-type">${result.type}</div>
            </a>
        </div>
    `).join('');
    
    searchResults.innerHTML = resultHtml;
}

function closeSearchDropdown() {
    // Close the search dropdown after clicking a result
    const dropdown = document.querySelector('#searchToggle').nextElementSibling;
    if (dropdown) {
        const bsDropdown = bootstrap.Dropdown.getInstance(dropdown);
        if (bsDropdown) {
            bsDropdown.hide();
        }
    }
}

// Scroll to Top Button
function initScrollToTop() {
    // Create scroll to top button
    const scrollBtn = document.createElement('button');
    scrollBtn.className = 'scroll-to-top';
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.title = 'Back to top';
    document.body.appendChild(scrollBtn);
    
    // Show/hide button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollBtn.classList.add('show');
        } else {
            scrollBtn.classList.remove('show');
        }
    });
    
    // Scroll to top when clicked
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Animations on Scroll
function initAnimations() {
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.service-card, .blog-card, .job-card, .team-member, .feature-item');
    animatedElements.forEach(el => observer.observe(el));
}

// Contact Form Enhancement
function initContactForm() {
    const contactForm = document.querySelector('#contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            // Show loading state
            submitBtn.innerHTML = '<span class="loading-spinner"></span> Sending...';
            submitBtn.disabled = true;
            
            // Re-enable button after form submission (whether success or failure)
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }
}

// Job Filters
function initJobFilters() {
    const jobFilters = document.querySelectorAll('.job-filter');
    
    jobFilters.forEach(filter => {
        filter.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });
}

// Blog Filters
function initBlogFilters() {
    const blogFilters = document.querySelectorAll('.blog-filter');
    
    blogFilters.forEach(filter => {
        filter.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });
}

// Utility Functions
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 90px; right: 20px; z-index: 1050; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Form Validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^\+?[\d\s\-\(\)]+$/;
    return re.test(phone);
}

// File Upload Helper
function handleFileUpload(input, maxSize = 5 * 1024 * 1024) { // 5MB default
    const file = input.files[0];
    
    if (!file) return true;
    
    if (file.size > maxSize) {
        showNotification('File size must be less than 5MB', 'danger');
        input.value = '';
        return false;
    }
    
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Only PDF and Word documents are allowed', 'danger');
        input.value = '';
        return false;
    }
    
    return true;
}

// Smooth Scrolling for Anchor Links
document.addEventListener('click', function(e) {
    if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

// Lazy Loading for Images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading if there are lazy images
if (document.querySelectorAll('img[data-src]').length > 0) {
    initLazyLoading();
}

// Navbar color change on scroll
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Auto-hide alerts after 5 seconds
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 5000);

// Print function
function printPage() {
    window.print();
}

// Share functionality
function shareContent(title, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            url: url
        });
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(url).then(() => {
            showNotification('Link copied to clipboard!', 'success');
        });
    }
}

// Export functions for global use
window.NextwaveJS = {
    showNotification,
    formatDate,
    truncateText,
    validateEmail,
    validatePhone,
    handleFileUpload,
    shareContent,
    printPage
};