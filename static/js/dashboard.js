document.addEventListener(
"DOMContentLoaded",
function(){


const btn=document.getElementById(
"sidebarToggle"
);


const sidebar=document.getElementById(
"sidebar"
);



if(btn && sidebar){


btn.onclick=function(){

sidebar.classList.toggle(
"active"
);


};


}


});