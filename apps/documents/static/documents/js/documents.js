console.log("document app loaded ");
// ========================================
// DOCUMENTS APP JAVASCRIPT
// ========================================

document.addEventListener("DOMContentLoaded", function () {

    // ==========================
    // Live Search
    // ==========================

    const searchInput = document.getElementById("documentSearch");

    if (searchInput) {

        searchInput.addEventListener("keyup", function () {

            const filter = this.value.toLowerCase();

            const table = document.getElementById("documentsTable");

            if (!table) return;

            const rows = table.querySelectorAll("tbody tr");

            rows.forEach(function (row) {

                const text = row.textContent.toLowerCase();

                row.style.display = text.includes(filter) ? "" : "none";

            });

        });

    }
    

    // ==========================
    // File Preview
    // ==========================

    const fileInput = document.querySelector('input[type="file"]');

    const selectedFile = document.getElementById("selectedFile");

    if (fileInput && selectedFile) {

        fileInput.addEventListener("change", function () {

            if (this.files.length > 0) {

                const file = this.files[0];

                const size = (file.size / 1024 / 1024).toFixed(2);

                selectedFile.innerHTML = `
                    <strong>${file.name}</strong><br>
                    Size: ${size} MB<br>
                    Type: ${file.type || "Unknown"}
                `;

            } else {

                selectedFile.textContent = "No file selected";

            }

        });

    }

    // ==========================
    // Delete Confirmation
    // ==========================

    const deleteForms = document.querySelectorAll(".delete-form");

    deleteForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const confirmed = confirm(
                "Are you sure you want to permanently delete this document?"
            );

            if (!confirmed) {

                event.preventDefault();

            }

        });

    });

    // ==========================
    // Auto Hide Alerts
    // ==========================

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        setTimeout(function () {

            alert.style.transition = "opacity 0.5s ease";

            alert.style.opacity = "0";

            setTimeout(function () {

                alert.remove();

            }, 500);

        }, 4000);

    });

    // ==========================
    // Button Loading State
    // ==========================

    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton = form.querySelector(
                'button[type="submit"]'
            );

            if (submitButton) {

                submitButton.disabled = true;

                submitButton.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';

            }

        });

    });

    // ==========================
    // Smooth Scroll to Top
    // ==========================

    const topButtons = document.querySelectorAll(".scroll-top");

    topButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            window.scrollTo({

                top: 0,

                behavior: "smooth"

            });

        });

    });

    // ==========================
    // Highlight Active Navigation
    // ==========================

    const currentPath = window.location.pathname;

    document.querySelectorAll("a").forEach(function (link) {

        if (link.getAttribute("href") === currentPath) {

            link.classList.add("active");

        }

    });

});