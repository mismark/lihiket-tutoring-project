document.addEventListener("DOMContentLoaded", function () {

    console.log("Assignments App Loaded");

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function(alert){

        setTimeout(function(){

            alert.classList.add("fade");

            setTimeout(function(){

                alert.remove();

            },500);

        },5000);

    });

});