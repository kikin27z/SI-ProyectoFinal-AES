"use strict";

let btnForm = document.querySelector("#btn");
let captcha = document.querySelector(".captcha");
console.log(btnForm);
let form = document.querySelector("form");
form.addEventListener("submit", function(event) {
  var recaptcha = document.querySelector('#g-recaptcha-response').value;
  if (recaptcha === "") { 
    event.preventDefault();
    alert("Please check the reCAPTCHA");
  }
});

function name(params) {
    
}

function limpiarLogin() {
    let txtContrasena = document.querySelector("#contrasena");
    let txtUsuario = document.querySelector("#usuario");
    txtContrasena.value = "";
    txtUsuario.value = "";
}
limpiarLogin();