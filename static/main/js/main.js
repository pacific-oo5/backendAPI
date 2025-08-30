// Page transition handling
document.addEventListener('DOMContentLoaded', function() {
    // Initialize page transition
    const transitionOverlay = document.querySelector('.page-transition-overlay');

    // Hide overlay after page load
    setTimeout(() => {
        transitionOverlay.classList.remove('active');
    }, 500);

    // Add click event listeners to all internal links
    document.querySelectorAll('a').forEach(link => {
        if (link.href && link.href.indexOf(window.location.origin) !== -1 &&
            !link.href.includes('#') &&
            link.href !== window.location.href) {

            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetUrl = this.href;

                // Show transition overlay
                transitionOverlay.classList.add('active');

                // Navigate after delay
                setTimeout(() => {
                    window.location.href = targetUrl;
                }, 800);
            });
        }
    });

    // Add animation to elements
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.fade-in');

        elements.forEach(element => {
            const position = element.getBoundingClientRect();

            // If element is in viewport
            if(position.top < window.innerHeight && position.bottom >= 0) {
                element.style.opacity = 1;
                element.style.transform = 'translateY(0)';
            }
        });
    };

    // Initial call
    animateOnScroll();

    // Listen for scroll events
    window.addEventListener('scroll', animateOnScroll);
});

// Copy token function
function copyToken(token) {
    navigator.clipboard.writeText(token).then(() => {
        // Create and show notification
        const notification = document.createElement('div');
        notification.className = 'alert alert-success position-fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '1060';
        notification.style.minWidth = '300px';
        notification.innerHTML = `
            <i class="bi bi-check-circle-fill me-2"></i>
            Токен скопирован в буфер обмена
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        document.body.appendChild(notification);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }).catch(err => {
        console.error('Ошибка копирования: ', err);
    });
}