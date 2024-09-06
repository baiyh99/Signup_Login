window.onload = function() {
    // Get the modal
    var signup_modal = document.getElementById('signup-modal');
    var signup_btn = document.getElementById('signup-btn');
    var signup_span = document.getElementsByClassName('signup_close')[0];


    var login_modal = document.getElementById('login-modal');
    var login_btn = document.getElementById('login-btn');
    var login_span = document.getElementsByClassName('login_close')[0];


    // 不同按键传回的内容不同 - 注册
    document.getElementById('signupGetVerification').addEventListener('click', function() {
        fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: 'signupGetVerification' })
        });
    });

    document.getElementById('signupSubmit').addEventListener('click', function() {
        fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: 'signupSubmit' })
        });
    });

    // Check if elements exist before setting event listeners
    if (signup_modal && signup_btn && signup_span) {
        signup_btn.onclick = function() {
            signup_modal.style.display = "block";
        }

        signup_span.onclick = function() {
            signup_modal.style.display = "none";
        }

        window.onclick = function(event) {
            if (event.target === signup_modal) {
                signup_modal.style.display = "none";
            }
        }
    } else {
        console.error("One or more elements were not found.");
    }

    // Check if elements exist before setting event listeners
    if (login_modal && login_btn && login_span) {
        login_btn.onclick = function() {
            login_modal.style.display = "block";
        }

        login_span.onclick = function() {
            login_modal.style.display = "none";
        }

        window.onclick = function(event) {
            if (event.target === login_modal) {
                login_modal.style.display = "none";
            }
        }
    } else {
        console.error("One or more elements were not found.");
    }
};