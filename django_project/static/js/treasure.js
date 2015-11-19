// function to hide the reminder box
function hide_reminder(){
    el = document.getElementById('top');
    el.classList.add('hidden');
}

// add action listener to the reminder button
var cont_browsing = document.getElementById('continue-browsing');
cont_browsing.addEventListener("click", function(){hide_reminder()}, false);