// Main JavaScript file for AETHOS
// This file contains the core frontend functionality

// Terminal functionality
class Terminal {
    constructor() {
        this.history = [];
        this.currentCommand = '';
        this.init();
    }

    init() {
        // Terminal initialization code
        console.log('AETHOS Terminal initialized');
    }
}

// Initialize terminal when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const terminal = new Terminal();
    
    // Add event listeners for terminal interactions
    const terminalInput = document.getElementById('terminal-input');
    if (terminalInput) {
        terminalInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                // Handle command submission
                const command = this.value.trim();
                if (command) {
                    terminal.executeCommand(command);
                    this.value = '';
                }
            }
        });
    }
});

// File upload handling
function handleFileUpload(file) {
    // Validate file type and size
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    const maxSize = 20 * 1024 * 1024; // 20MB

    if (!allowedTypes.includes(file.type)) {
        showError('Please upload a valid image file (JPEG, PNG, GIF, or WebP)');
        return false;
    }

    if (file.size > maxSize) {
        showError('File size must be less than 20MB');
        return false;
    }

    return true;
}

// Error handling
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    } else {
        alert(message);
    }
}

// API communication
async function sendCommand(command, imageData = null) {
    try {
        const formData = new FormData();
        formData.append('command', command);
        
        if (imageData) {
            formData.append('image', imageData);
        }

        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.text();
    } catch (error) {
        console.error('Error sending command:', error);
        showError('Failed to process command. Please try again.');
        return null;
    }
}

// Export functions for use in other modules
window.AETHOS = {
    Terminal,
    handleFileUpload,
    sendCommand,
    showError
};
