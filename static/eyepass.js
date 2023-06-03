let eyepass = document.getElementById("eyepass");
let password = document.getElementById("senha");

eyepass.onclick = function() {
    if(password.type == "password") {
        password.type = "text";
        eyepass.className = "fa-solid fa-eye";
    } else {
        password.type = "password";
        eyepass.className = "fa-solid fa-eye-slash";
    }
}

