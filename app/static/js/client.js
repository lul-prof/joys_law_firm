document.addEventListener('DOMContentLoaded', function() {
    // Mobile sidebar toggle
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }

    // Document upload form
    const uploadButton = document.querySelector('[data-toggle="upload-form"]');
    const uploadForm = document.getElementById('uploadForm');
    
    if (uploadButton && uploadForm) {
        uploadButton.addEventListener('click', function() {
            uploadForm.style.display = uploadForm.style.display === 'none' ? 'block' : 'none';
        });
    }

    // File input preview
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            const fileLabel = this.nextElementSibling;
            if (fileLabel) {
                fileLabel.textContent = fileName || 'Choose file';
            }
        });
    }

    // Message form handling
    const newMessageButton = document.querySelector('[data-toggle="message-form"]');
    const messageForm = document.getElementById('newMessageForm');
    
    if (newMessageButton && messageForm) {
        newMessageButton.addEventListener('click', function() {
            messageForm.style.display = messageForm.style.display === 'none' ? 'block' : 'none';
        });
    }

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Appointment cancellation confirmation
    const cancelButtons = document.querySelectorAll('[data-action="cancel-appointment"]');
    cancelButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to cancel this appointment?')) {
                e.preventDefault();
            }
        });
    });

    // Password confirmation validation
    const passwordForm = document.querySelector('form[data-type="password-update"]');
    if (passwordForm) {
        const newPassword = passwordForm.querySelector('#new_password');
        const confirmPassword = passwordForm.querySelector('#confirm_password');
        
        function validatePassword() {
            if (newPassword.value !== confirmPassword.value) {
                confirmPassword.setCustomValidity("Passwords don't match");
            } else {
                confirmPassword.setCustomValidity('');
            }
        }

        newPassword.addEventListener('change', validatePassword);
        confirmPassword.addEventListener('change', validatePassword);
    }

    // Auto-dismiss flash messages
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });

    // Real-time message updates
    function checkNewMessages() {
        fetch('/client/messages/check')
            .then(response => response.json())
            .then(data => {
                if (data.new_messages > 0) {
                    // Update UI to show new messages
                    const messagesBadge = document.querySelector('.messages-badge');
                    if (messagesBadge) {
                        messagesBadge.textContent = data.new_messages;
                        messagesBadge.style.display = 'inline';
                    }
                }
            });
    }

    // Check for new messages every 30 seconds
    if (document.querySelector('.messages-badge')) {
        setInterval(checkNewMessages, 30000);
    }

    // Document preview
    const previewButtons = document.querySelectorAll('[data-action="preview-document"]');
    previewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const documentUrl = this.dataset.url;
            const documentTitle = this.dataset.title;
            
            // Create modal for document preview
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${documentTitle}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <iframe src="${documentUrl}" width="100%" height="500px"></iframe>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            new bootstrap.Modal(modal).show();
        });
    });
});