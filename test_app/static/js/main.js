/**
 * OpenShot Cloud - Main JavaScript
 * Handles global functionality for the web application
 */

// Wait for the document to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // Enable tooltips everywhere
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Flash message auto-hide
    const flashMessages = document.querySelectorAll('.alert:not(.alert-permanent)');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.classList.add('fade');
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);
    });
    
    // Add loading indicator to form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
                
                // Store original text for restoration after form submission
                submitButton.dataset.originalText = originalText;
            }
        });
    });
    
    // Handle API requests with error handling
    window.apiRequest = async function(url, method = 'GET', data = null, headers = {}) {
        try {
            // Add authorization header if token exists
            const token = localStorage.getItem('auth_token');
            if (token) {
                headers.Authorization = `Bearer ${token}`;
            }
            
            // Set default headers
            headers['Content-Type'] = headers['Content-Type'] || 'application/json';
            
            // Configure request options
            const options = {
                method: method,
                headers: headers,
            };
            
            // Add body for non-GET requests
            if (method !== 'GET' && data) {
                options.body = JSON.stringify(data);
            }
            
            // Make the request
            const response = await fetch(url, options);
            
            // Parse response
            const responseData = await response.json();
            
            // Check if response was successful
            if (!response.ok) {
                throw new Error(responseData.error || 'An error occurred');
            }
            
            return responseData;
        } catch (error) {
            console.error('API request error:', error);
            
            // Show error message in UI
            showNotification(error.message || 'An error occurred', 'danger');
            
            // Re-throw error for additional handling
            throw error;
        }
    };
    
    // Notification function
    window.showNotification = function(message, type = 'info') {
        const notificationContainer = document.getElementById('notification-container');
        
        // Create container if it doesn't exist
        if (!notificationContainer) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.style.position = 'fixed';
            container.style.top = '20px';
            container.style.right = '20px';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add to container
        document.getElementById('notification-container').appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 500);
        }, 5000);
    };
});