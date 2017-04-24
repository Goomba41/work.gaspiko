// Get the modal
var main = document.getElementById('main');

// Get the main window
var modal = document.getElementById('myModal');

// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var close = document.getElementById("close-button");

// When the user clicks on the button, open the modal 
btn.onclick = function() {
    modal.style.display = "block";
    main.style.visible = "hidden";
}

// When the user clicks on <span> (x), close the modal
close.onclick = function() {
    modal.style.display = "none";
    main.style.overflow = "auto";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
        main.style.overflow = "auto";
    }
}
