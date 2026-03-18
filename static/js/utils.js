// utils.js

// Error message extraction from API responses
export function getErrorMessage(error) {
    if (typeof error.detail === "string") {
        return error.detail;
    } else if (Array.isArray(error.detail)) {
        return error.detail.map((err) => err.msg).join(". ");
    }
    return "An error occurred. Please try again.";
}

// Show a Tailwind modal by ID (removes 'hidden' class)
export function showModal(modalId) {
    document.getElementById(modalId).classList.remove("hidden");
}

// Hide a Tailwind modal by ID (adds 'hidden' class)
export function hideModal(modalId) {
    document.getElementById(modalId).classList.add("hidden");
}