// assets/js/print.js

document.addEventListener("DOMContentLoaded", function () {

    // Print receipt
    const printBtn = document.getElementById("printReceipt");

    if (printBtn) {
        printBtn.addEventListener("click", function () {
            window.print();
        });
    }

    // Download PDF (if available)
    const pdfBtn = document.getElementById("downloadPDF");

    if (pdfBtn) {
        pdfBtn.addEventListener("click", function () {
            window.location.href = "export.php";
        });
    }

});