// assets/js/track.js

document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("trackForm");
    const trackingInput = document.getElementById("tracking_number");

    if (form) {
        form.addEventListener("submit", function (e) {

            if (trackingInput.value.trim() === "") {
                e.preventDefault();
                alert("Please enter a tracking number.");
                trackingInput.focus();
            }

        });
    }

});