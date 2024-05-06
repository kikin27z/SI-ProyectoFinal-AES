"use strict";
// Hasta que no cargue todo el contenido html no se ejecutara el script
document.addEventListener('DOMContentLoaded', ready, false);

var ocultarClave;
var txtClave;
var btnCifrar;
var btnDescifrar;
var txtTexto;


function verContrasena() {
    if (txtClave.type == 'password') {
        ocultarClave.style.backgroundPosition = '-44px -3px';
        txtClave.type = 'text';
    } else {
        ocultarClave.style.backgroundPosition = '0px -3px';
        txtClave.type = 'password';
    }
}

function prevenirRecargar(e) {
    e.preventDefault();
}
function cargarVariables() {
    ocultarClave = document.querySelector('.caja-derecha');
    txtClave = document.getElementById('pass');
    btnCifrar = document.getElementById('cifrar');
    btnDescifrar = document.getElementById('descifrar');
    txtTexto = document.getElementById('areatexto');
}

function cifrarTexto() {
    if(txtTexto.value == "" || txtClave.value == ""){ 
        alert("Rellene los campos");
        
    }else{
        $.ajax({
            url: '/cifrar',  // The endpoint in your Flask app
            data: { 'text': txtTexto.value, 'password': txtClave.value },
            type: 'POST',
            success: function (response) {
                txtTexto.value = response.cifrado;
            },
            error: function (error) {
                console.log("hubo error");
                console.log(error.mensaje);
            }
        });
    }
}
function descifrarTexto() {
    if(txtTexto.value == "" && txtClave.value == ""){ 
        alert("Rellene los campos");
        
    }else{
        $.ajax({
            url: '/descifrar',  // The endpoint in your Flask app
            data: { 'text': txtTexto.value, 'password': txtClave.value },
            type: 'POST',
            success: function (response) {
                console.log(response);
                txtTexto.value = response.cifrado;
                console.log("hubo exito");
                // Do something with the response
            },
            error: function (error) {
                console.log(error);
            }
        });
    }
}

function ready() {
    cargarVariables();

    ocultarClave.addEventListener('click', verContrasena);
    btnCifrar.addEventListener('click', cifrarTexto);
    btnDescifrar.addEventListener('click', descifrarTexto);
}
