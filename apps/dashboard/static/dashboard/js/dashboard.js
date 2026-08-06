function toggleSidebar(){

    document
    .getElementById("sidebar")
    .classList.toggle("active");

}

document.addEventListener("DOMContentLoaded", function () {

    console.log("Teacher Dashboard Loaded");

});


const ctx = document.getElementById("courseChart");

if (ctx) {

    new Chart(ctx, {

        type: "line",

        data: {

            labels: [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun"
            ],

            datasets: [

                {

                    label: "Student Enrollments",

                    data: [5, 12, 18, 22, 28, 35],

                    borderWidth: 3,

                    fill: true,

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

        }

    });

}
