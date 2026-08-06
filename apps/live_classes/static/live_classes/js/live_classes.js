document.addEventListener("DOMContentLoaded", function () {

    console.log("live class loaded");

    // ============================
    // Thumbnail Preview
    // ============================

    const thumbnailInput = document.querySelector(
        'input[type="file"]'
    );

    const preview = document.getElementById(
        "thumbnailPreview"
    );

    if (thumbnailInput && preview) {

        thumbnailInput.addEventListener(
            "change",
            function (event) {

                const file = event.target.files[0];

                if (file) {

                    preview.src = URL.createObjectURL(file);

                    preview.style.display = "block";

                }

            }
        );

    }

    // ============================
    // Auto Calculate Duration
    // ============================

    const startInput = document.querySelector(
        'input[name="start_datetime"]'
    );

    const endInput = document.querySelector(
        'input[name="end_datetime"]'
    );

    const durationInput = document.querySelector(
        'input[name="duration"]'
    );

    function calculateDuration() {

        if (
            startInput &&
            endInput &&
            durationInput &&
            startInput.value &&
            endInput.value
        ) {

            const start = new Date(startInput.value);

            const end = new Date(endInput.value);

            const minutes = Math.round(
                (end - start) / 60000
            );

            if (minutes > 0) {

                durationInput.value = minutes;

            }

        }

    }

    if (startInput && endInput) {

        startInput.addEventListener(
            "change",
            calculateDuration
        );

        endInput.addEventListener(
            "change",
            calculateDuration
        );

    }

    // ============================
    // Recording URL Toggle
    // ============================

    const recordedCheckbox = document.querySelector(
        'input[name="is_recorded"]'
    );

    const recordingUrl = document.querySelector(
        'input[name="recording_url"]'
    );

    function toggleRecording() {

        if (
            recordedCheckbox &&
            recordingUrl
        ) {

            recordingUrl.disabled = !recordedCheckbox.checked;

            if (!recordedCheckbox.checked) {

                recordingUrl.value = "";

            }

        }

    }

    if (recordedCheckbox && recordingUrl) {

        toggleRecording();

        recordedCheckbox.addEventListener(
            "change",
            toggleRecording
        );

    }

    // ============================
    // Delete Confirmation
    // ============================

    const deleteForms = document.querySelectorAll(
        "form.delete-form"
    );

    deleteForms.forEach(function (form) {

        form.addEventListener(
            "submit",
            function (event) {

                if (
                    !confirm(
                        "Are you sure you want to delete this live class?"
                    )
                ) {

                    event.preventDefault();

                }

            }
        );

    });

    // ============================
    // Meeting Link Validation
    // ============================

    const meetingLink = document.querySelector(
        'input[name="meeting_link"]'
    );

    if (meetingLink) {

        meetingLink.addEventListener(
            "blur",
            function () {

                const value = meetingLink.value.trim();

                if (
                    value &&
                    !value.startsWith("http://") &&
                    !value.startsWith("https://")
                ) {

                    alert(
                        "Meeting link should start with http:// or https://"
                    );

                    meetingLink.focus();

                }

            }
        );

    }

    // ============================
    // Countdown Timer
    // ============================

    const countdowns = document.querySelectorAll(
        ".countdown"
    );

    countdowns.forEach(function (element) {

        const targetDate = new Date(
            element.dataset.datetime
        );

        function updateCountdown() {

            const now = new Date();

            const diff = targetDate - now;

            if (diff <= 0) {

                element.innerHTML =
                    "Live Now";

                return;

            }

            const days = Math.floor(
                diff / (1000 * 60 * 60 * 24)
            );

            const hours = Math.floor(
                (diff / (1000 * 60 * 60)) % 24
            );

            const minutes = Math.floor(
                (diff / (1000 * 60)) % 60
            );

            element.innerHTML =
                days +
                "d " +
                hours +
                "h " +
                minutes +
                "m";

        }

        updateCountdown();

        setInterval(
            updateCountdown,
            60000
        );

    });

});