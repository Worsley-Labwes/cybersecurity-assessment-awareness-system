// static/js/app.js
// Shared front-end behaviour for CAAS. Dashboard-specific chart code lives
// inline in dashboard.html (it needs Jinja-rendered URLs); this file is the
// place to add any additional cross-page interactivity as the prototype grows.

document.addEventListener("DOMContentLoaded", () => {
    // Auto-dismiss flash messages after 5 seconds
    document.querySelectorAll(".alert").forEach((alert) => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });
});
