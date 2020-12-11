// Valiables to validate
const form = document.querySelector('.box-form')//Selecciono el boton submit
const inputname = document.getElementById('box-form-username');//Selecciono el input Nombre de usuario
const inputpass = document.getElementById('box-form-pass');//Selecciono el input contraseña
const inputpasscheck = document.getElementById('box-form-passCheck');//Selecciono el input Check de contraseña
const msj = document.getElementById('msj');

/**
 * Listener
 */
form.addEventListener('submit', (e) =>{
    estado = false;
    if(inputname.textContent.length == 0){
        console.log('Digite un nombre de usuario');
        alert('Digite un nombre de usuario');
        msj.textContent = 'ups'
    }else if(inputpass.value.length == 0 || inputpass.nodeValue.length<8){
        alert('Debe ingresar una clave con mínimo 8 caracteres');
        console.log('Debe ingresar una clave con mínimo 8 caracteres');
        msj.textContent = 'ups'
    }else if(inputpass.nodeValue != inputpasscheck.nodeValue){
        alert('Sus contraseñas no coinciden');
        console.log('Sus contraseñas no coinciden');
        msj.textContent = 'ups'
    }else{
        estado = true;
    }
    
    if(estado== true){
        e.preventDefault();
    }
});