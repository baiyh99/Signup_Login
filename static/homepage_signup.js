window.onload = function() {
    // Get the modal
    var modal = document.getElementById('signup-modal');
    var btn = document.getElementById('signup-btn');

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName('close')[0];

    // Check if elements exist before setting event listeners
    if (btn && modal && span) {
        btn.onclick = function() {
            modal.style.display = "block";
        }

        span.onclick = function() {
            modal.style.display = "none";
        }

        window.onclick = function(event) {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        }
    } else {
        console.error("One or more elements were not found.");
    }
};