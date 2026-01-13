/**
 * Form Validation Utility
 * Provides reusable validation functions with SweetAlert2 integration
 */

const FormValidator = {
    // Brand color for consistent UI
    brandColor: '#6c5ce7',

    // Validation rules
    rules: {
        required: (value, fieldName) => {
            if (!value || value.trim() === '') {
                return { valid: false, message: `${fieldName} is required` };
            }
            return { valid: true };
        },

        email: (value) => {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                return { valid: false, message: 'Please enter a valid email address' };
            }
            return { valid: true };
        },

        minLength: (value, min, fieldName) => {
            if (value.length < min) {
                return { valid: false, message: `${fieldName} must be at least ${min} characters` };
            }
            return { valid: true };
        },

        maxLength: (value, max, fieldName) => {
            if (value.length > max) {
                return { valid: false, message: `${fieldName} must not exceed ${max} characters` };
            }
            return { valid: true };
        },

        password: (value) => {
            // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
            if (value.length < 8) {
                return { valid: false, message: 'Password must be at least 8 characters long' };
            }
            if (!/[A-Z]/.test(value)) {
                return { valid: false, message: 'Password must contain at least one uppercase letter' };
            }
            if (!/[a-z]/.test(value)) {
                return { valid: false, message: 'Password must contain at least one lowercase letter' };
            }
            if (!/[0-9]/.test(value)) {
                return { valid: false, message: 'Password must contain at least one number' };
            }
            return { valid: true };
        },

        match: (value1, value2, fieldName) => {
            if (value1 !== value2) {
                return { valid: false, message: `${fieldName} do not match` };
            }
            return { valid: true };
        },

        username: (value) => {
            // Alphanumeric and underscores only, 3-20 characters
            const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
            if (!usernameRegex.test(value)) {
                return { valid: false, message: 'Username must be 3-20 characters and contain only letters, numbers, and underscores' };
            }
            return { valid: true };
        }
    },

    // Show error alert
    showError: function (message) {
        Swal.fire({
            icon: 'error',
            title: 'Validation Error',
            text: message,
            confirmButtonColor: this.brandColor,
            confirmButtonText: 'OK'
        });
    },

    // Show success alert
    showSuccess: function (message) {
        Swal.fire({
            icon: 'success',
            title: 'Success',
            text: message,
            confirmButtonColor: this.brandColor,
            timer: 2000,
            timerProgressBar: true
        });
    },

    // Validate a single field
    validateField: function (value, validations) {
        for (let validation of validations) {
            const result = validation(value);
            if (!result.valid) {
                this.showError(result.message);
                return false;
            }
        }
        return true;
    },

    // Validate entire form
    validateForm: function (formData) {
        for (let field in formData) {
            const { value, validations } = formData[field];
            if (!this.validateField(value, validations)) {
                return false;
            }
        }
        return true;
    }
};

// Make it globally available
window.FormValidator = FormValidator;
