// assets/js/app.js

document.addEventListener("DOMContentLoaded", function () {

    console.log("Parcel Tracking System Loaded");

    // Auto-hide alert messages
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.display = "none";
        }, 5000);
    });

    // Confirm delete buttons
    document.querySelectorAll(".delete-btn").forEach(function (button) {
        button.addEventListener("click", function (e) {
            if (!confirm("Are you sure you want to delete this parcel?")) {
                e.preventDefault();
            }
        });
    });

    // Print button
    const printBtn = document.getElementById("printBtn");
    if (printBtn) {
        printBtn.addEventListener("click", function () {
            window.print();
        });
    }

    // Search table
    const search = document.getElementById("search");
    if (search) {
        search.addEventListener("keyup", function () {
            const value = this.value.toLowerCase();
            const rows = document.querySelectorAll("table tbody tr");

            rows.forEach(function (row) {
                row.style.display = row.textContent.toLowerCase().includes(value)
                    ? ""
                    : "none";
            });
        });
    }

});

// Confirm delete
function confirmDelete() {
    return confirm("Are you sure you want to delete this parcel?");
}

// Print page
function printPage() {
    window.print();
}