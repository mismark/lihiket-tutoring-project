"use strict";

/*
==========================================
Quiz JavaScript
==========================================
*/

document.addEventListener("DOMContentLoaded", function () {

    console.log("Quizzes Loaded");

});

/*
==========================================
Confirm Quiz Submission
==========================================
*/

const quizForm = document.getElementById("quizForm");

if (quizForm){

    quizForm.addEventListener("submit", function(e){

        const confirmed = confirm(
            "Are you sure you want to submit this quiz?"
        );

        if(!confirmed){

            e.preventDefault();

        }

    });

}

/*
==========================================
Highlight Selected Answer
==========================================
*/

document.querySelectorAll(".form-check-input").forEach(function(input){

    input.addEventListener("change", function(){

        document.querySelectorAll(".form-check").forEach(function(card){

            card.classList.remove("border-primary");

        });

        this.closest(".form-check")
            .classList.add("border-primary");

    });

});