// Loading indicator
document.addEventListener('DOMContentLoaded', function() {
    // Add loading class to body when navigation starts
    document.addEventListener('click', function(e) {
        const link = e.target.closest('a');
        if (link && !link.target && !e.ctrlKey && !e.shiftKey && !e.metaKey && !e.altKey) {
            document.body.classList.add('loading');
        }
    });

    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tippy(tooltip, {
            content: tooltip.getAttribute('data-tooltip'),
            placement: 'top',
            animation: 'scale',
        });
    });

    // Smooth scroll to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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

    // Enhanced mobile menu with animations
    const menuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.mobile-menu');
    const overlay = document.createElement('div');
    overlay.className = 'mobile-menu-overlay hidden fixed inset-0 bg-black bg-opacity-50 z-40';
    document.body.appendChild(overlay);

    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            overlay.classList.toggle('hidden');
            document.body.classList.toggle('overflow-hidden');
            
            // Animate menu items
            const menuItems = mobileMenu.querySelectorAll('li');
            menuItems.forEach((item, index) => {
                item.style.animation = mobileMenu.classList.contains('hidden') 
                    ? ''
                    : `slideIn 0.3s ease forwards ${index * 0.1}s`;
            });
        });

        overlay.addEventListener('click', function() {
            mobileMenu.classList.add('hidden');
            overlay.classList.add('hidden');
            document.body.classList.remove('overflow-hidden');
        });
    }

    // Enhanced form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('border-red-500', 'shake');
                    
                    // Remove shake animation after it completes
                    setTimeout(() => {
                        field.classList.remove('shake');
                    }, 500);

                    // Show error message
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('p');
                        errorMsg.className = 'error-message text-red-500 text-sm mt-1';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                    errorMsg.textContent = `${field.getAttribute('placeholder') || 'This field'} is required`;
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });

        // Remove error styling on input
        form.querySelectorAll('input, textarea').forEach(field => {
            field.addEventListener('input', function() {
                this.classList.remove('border-red-500');
                const errorMsg = this.nextElementSibling;
                if (errorMsg && errorMsg.classList.contains('error-message')) {
                    errorMsg.remove();
                }
            });
        });
    });

    // Newsletter form enhancement
    const newsletterForm = document.querySelector('form[action*="newsletter_signup"]');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = this.querySelector('input[type="email"]');
            const submitButton = this.querySelector('button[type="submit"]');
            
            if (emailInput.value.trim()) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<svg class="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Subscribing...';
                
                // Submit the form
                this.submit();
            }
        });
    }

    // Comment form enhancement
    const commentForm = document.querySelector('form[action*="post_detail"]');
    if (commentForm) {
        const commentTextarea = commentForm.querySelector('textarea');
        const charCount = document.createElement('div');
        charCount.className = 'text-sm text-gray-500 mt-1';
        commentTextarea.parentNode.insertBefore(charCount, commentTextarea.nextSibling);

        commentTextarea.addEventListener('input', function() {
            const remaining = 500 - this.value.length;
            charCount.textContent = `${remaining} characters remaining`;
            if (remaining < 50) {
                charCount.classList.add('text-yellow-500');
            } else {
                charCount.classList.remove('text-yellow-500');
            }
        });
    }

    // Image lazy loading with blur-up effect
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    lazyImages.forEach(img => {
        img.style.filter = 'blur(5px)';
        img.style.transition = 'filter 0.3s';
        
        img.addEventListener('load', function() {
            img.style.filter = 'none';
        });
    });
});

// Infinite scroll for blog posts
let loading = false;
let page = 1;

function loadMorePosts() {
    if (loading) return;
    
    const postsContainer = document.querySelector('.space-y-8');
    if (!postsContainer) return;

    const lastPost = postsContainer.lastElementChild;
    if (!lastPost) return;

    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !loading) {
            loading = true;
            page++;

            fetch(`?page=${page}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newPosts = doc.querySelectorAll('.space-y-8 > article');
                
                if (newPosts.length) {
                    newPosts.forEach(post => {
                        const clone = post.cloneNode(true);
                        postsContainer.appendChild(clone);
                    });
                    loading = false;
                } else {
                    observer.disconnect();
                }
            });
        }
    });

    observer.observe(lastPost);
}

// Initialize infinite scroll if we're on the blog listing page
if (document.querySelector('.space-y-8')) {
    loadMorePosts();
}
