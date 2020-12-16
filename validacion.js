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
    if(inputname.value == ''){
        console.log('Digite un nombre de usuario');
        estado=true;
        //msj.value = 'ups';
        alert('Digite un nombre de usuario');
    }else if(inputpass.value.length == 0 || inputpass.value.length<8){
        console.log('Debe ingresar una clave con mínimo 8 caracteres');
        estado=true;
        //msj.value = 'ups'
        alert('Debe ingresar una clave con mínimo 8 caracteres');
    }else if(inputpass.value!= inputpasscheck.value){
        console.log('Sus contraseñas no coinciden');
        estado=true;
        //msj.value = 'ups'
        alert('Sus contraseñas no coinciden');
    }else{
        estado = false;
        console.log('Entré aqui-puede registrarse pasar!!')
    }

    if(estado == true){
        e.preventDefault();
        estado=false;
    }
});