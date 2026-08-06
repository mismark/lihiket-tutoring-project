document.addEventListener("DOMContentLoaded", function () {

    console.log("lesson app loaded");

    // ===============================
    // Thumbnail Preview
    // ===============================

    const thumbnailInput = document.getElementById("id_thumbnail");
    const preview = document.getElementById("thumbnailPreview");

    if (thumbnailInput && preview) {

        thumbnailInput.addEventListener("change", function () {

            const file = this.files[0];

            if (file) {

                preview.src = URL.createObjectURL(file);
                preview.style.display = "block";

            }

        });

    }

    // ===============================
    // Delete Confirmation
    // ===============================

    document.querySelectorAll(".btn-danger").forEach(function(button){

        button.addEventListener("click", function(e){

            if(button.closest("form")){

                const confirmed = confirm(
                    "Are you sure you want to delete this lesson?"
                );

                if(!confirmed){

                    e.preventDefault();

                }

            }

        });

    });

    // ===============================
    // Auto Hide Alerts
    // ===============================

    setTimeout(function(){

        document.querySelectorAll(".alert").forEach(function(alert){

            alert.style.transition = "opacity .5s";

            alert.style.opacity = "0";

            setTimeout(function(){

                alert.remove();

            },500);

        });

    },5000);

    // ===============================
    // Card Hover Effect
    // ===============================

    document.querySelectorAll(".card").forEach(function(card){

        card.addEventListener("mouseenter",function(){

            card.style.transform="translateY(-4px)";

        });

        card.addEventListener("mouseleave",function(){

            card.style.transform="translateY(0)";

        });

    });

});