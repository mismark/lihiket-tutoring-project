/*
==========================================================
Subjects App JavaScript
==========================================================
*/

document.addEventListener("DOMContentLoaded", function () {

    console.log("Subjects App Loaded");

    initializeImagePreview();
    initializeDeleteConfirmation();
    initializeAutoDismissAlerts();
    initializeButtonLoading();
    initializeTooltips();
    initializeSearchFocus();
    initializeSmoothScroll();

});


/*==========================================================
Image Preview
==========================================================*/

function initializeImagePreview() {

    const imageInput = document.getElementById("id_image");
    const preview = document.getElementById("imagePreview");

    if (!imageInput || !preview) return;

    imageInput.addEventListener("change", function () {

        const file = this.files[0];

        if (!file) return;

        const reader = new FileReader();

        reader.onload = function (e) {

            preview.src = e.target.result;
            preview.style.display = "block";

        };

        reader.readAsDataURL(file);

    });

}


/*==========================================================
Delete Confirmation
==========================================================*/

function initializeDeleteConfirmation() {

    const deleteForms = document.querySelectorAll("form");

    deleteForms.forEach(function (form) {

        if (form.querySelector(".btn-danger")) {

            form.addEventListener("submit", function (e) {

                const confirmed = confirm(
                    "Are you sure you want to delete this subject?\n\nThis action cannot be undone."
                );

                if (!confirmed) {

                    e.preventDefault();

                }

            });

        }

    });

}


/*==========================================================
Auto Hide Alerts
==========================================================*/

function initializeAutoDismissAlerts() {

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        setTimeout(function () {

            alert.style.transition = "0.5s";
            alert.style.opacity = "0";

            setTimeout(function () {

                alert.remove();

            }, 500);

        }, 5000);

    });

}


/*==========================================================
Loading Buttons
==========================================================*/

function initializeButtonLoading() {

    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton = form.querySelector(
                "button[type='submit']"
            );

            if (submitButton) {

                submitButton.disabled = true;

                submitButton.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';

            }

        });

    });

}


/*==========================================================
Bootstrap Tooltips
==========================================================*/

function initializeTooltips() {

    if (typeof bootstrap === "undefined") return;

    const tooltipTriggerList =
        document.querySelectorAll('[data-bs-toggle="tooltip"]');

    tooltipTriggerList.forEach(function (tooltipTriggerEl) {

        new bootstrap.Tooltip(tooltipTriggerEl);

    });

}


/*==========================================================
Search Box
==========================================================*/

function initializeSearchFocus() {

    const search = document.querySelector("input[name='search']");

    if (!search) return;

    search.addEventListener("focus", function () {

        this.select();

    });

}


/*==========================================================
Smooth Scroll
==========================================================*/

function initializeSmoothScroll() {

    document.querySelectorAll("a[href^='#']").forEach(function (anchor) {

        anchor.addEventListener("click", function (e) {

            e.preventDefault();

            const target = document.querySelector(this.getAttribute("href"));

            if (target) {

                target.scrollIntoView({

                    behavior: "smooth"

                });

            }

        });

    });

}


/*==========================================================
Future Functions
==========================================================*/

// AJAX Search
// Dynamic Pagination
// Drag & Drop Upload
// Live Notifications
// DataTables Integration
// SweetAlert2 Confirmation
// Chart.js Integration
// Select2 Dropdowns
// Toast Notifications
// Dark Mode Support




document.querySelectorAll(".has-submenu > a").forEach(item => {

    item.addEventListener("click", function(e){

        e.preventDefault();

        this.parentElement.classList.toggle("active");

    });

});