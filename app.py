"""
py -m pip install Flask-Caching
py -m pip install Flask-MySQLdb
py -m pip install Flask
py -m pip install Flask-Session
py -m pip install Flask-MySQL
py -m pip install pycryptodome
py -m pip install cryptography
"""

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_caching import Cache
from flask import jsonify
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from Crypto.Random import get_random_bytes
from cryptography.fernet import Fernet


app = Flask(__name__)

# Contraseña para encriptar las sesiones
app.secret_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6ImthcmltIHRva2VuIiwiaWF0IjoxNTE2MjM5MDIyfQ.yvlR6F7xRnCSBRHTUNmvC6Pcvc_gFZ1C6S6ncEIJltA'
app.usuarioIV =  b'mD\x9b*\x05$\x18\x17\xe3\xdcIqc\x88\xa7\xfb'
app.contrasenaIV = b'\xf5\x9f\x83\x8d\xb4\xaev\xfe\x06m\xa5ya\x836\x1f'
app.contrasenaClave = "b221d9dbb083a7f33428d7c2a3c3198ae925614d70210e28716ccaa7cd4ddb79"
app.usuarioClave = "0e8d124994d74f4bf03ec83febff6fcba0b7c8cc0e01c3d5f2d9a4b07498a6a5"

app.config['CACHE_TYPE'] = 'simple'
# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'JFK_jfk27'
app.config['MYSQL_DB'] = 'aes'

# Iniciar MySQL
mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if 'loggedin' in session:
        return redirect(url_for('home'))
    # Mensaje en caso de error al ingresar
    msg = ''

    # Verifica si el usuario ha enviado el formulario
    if request.method == 'POST' and 'usuario' in request.form and 'contrasena' in request.form:
        # Creo variables con los datos del formulario
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        # Encripta la contraseña
        contrasena = encriptar_mensaje_aes(contrasena, app.contrasenaClave,app.contrasenaIV)
        usuario = encriptar_mensaje_aes(usuario, app.usuarioClave,app.usuarioIV)

        # Verifica si el usuario y la contraseña existen en la base de datos
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM cuentas WHERE usuario = %s AND contrasena = %s', (usuario, contrasena,))
        # Devuelve un registro y retorna el resultado
        cuenta = cursor.fetchone()

        if cuenta:
            # Crea la sesión del usuario, inicia sesión y retiene cierta info para trabajar con otras rutas
            usuariodescifrado = desencriptar_mensaje_aes(cuenta['usuario'], app.usuarioClave)
            
            cuenta['usuario'] = usuariodescifrado
            session['loggedin'] = True
            session['id'] = cuenta['id']
            session['username'] = usuariodescifrado

            # Redirige a la página de inicio
            return redirect(url_for('home'))
        else:
            # Si la cuenta no existe o la contraseña es incorrecta
            msg = '¡Usuario o contraseña incorrecta, intente de nuevo!'

    return render_template('index.html', msg=msg)


@app.route('/logout')
def logout():
    
    #Borra la sessión del usuario, cierra sesión
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)

    print(session)
    # Redirige al inicio sesión
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    msg = ''
    
    if request.method == 'POST' and 'usuario' in request.form and 'contrasena' in request.form and 'contrasena_confirmar' in request.form:
        # Create variables for easy access
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        contrasena_confirmar = request.form['contrasena_confirmar']

        usuarioEncriptado = encriptar_mensaje_aes(usuario, app.usuarioClave,app.usuarioIV)

        # Verifica si la cuenta existe en la base de datos
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM cuentas WHERE usuario = %s', (usuarioEncriptado,))
        account = cursor.fetchone()

        # Verificación de los datos del formulario, en caso de que no cumpla con las condiciones,
        # se mostrará un mensaje de error
        if account:
            msg = '¡Cuenta existente, intente de nuevo!'
        elif not re.match(r'[A-Za-z0-9]{4,}', usuario):
            msg = '¡Usuario debe contener unicamente números o letras y al menos 4 caracteres!'
        elif not re.match(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{4,}', contrasena):
            msg = '¡La contraseña debe contener al menos un número, una mayuscula, una minuscula y un caracter especial!'
        elif contrasena != contrasena_confirmar:
            msg = '¡Las contraseñas no coinciden!'
        elif not usuario or not contrasena or not contrasena_confirmar:
            msg = '¡Llenar todo el formulario, por favor!'
        else:
            # Encripta la contraseña
            usuario = encriptar_mensaje_aes(usuario, app.usuarioClave)
            contrasena = encriptar_mensaje_aes(contrasena, app.contrasenaClave,app.contrasenaIV)
            
            # Inserta la nueva cuenta en la base de datos
            cursor.execute('INSERT INTO cuentas (usuario,contrasena) VALUES  (%s, %s)', (usuarioEncriptado, contrasena,))
            mysql.connection.commit()
            msg = '¡Cuenta creada exitosamente!'
    
    return render_template('register.html', msg=msg)


@app.route('/')
def home():
    # Verifica si el usuario ha iniciado sesión
    print(session)
    if 'loggedin' in session:
        # Usuario ha iniciado sesión, mostrar la página de inicio
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM cuentas WHERE id = %s', (session['id'],))
        cuenta = cursor.fetchone()
        cuenta['usuario'] = desencriptar_mensaje_aes(cuenta['usuario'], app.usuarioClave)
        return render_template('convertidor.html', cuenta=cuenta)
    
    # Usuario no ha iniciado sesión, redirige al inicio sesión
    return redirect(url_for('login'))

@app.route('/cifrar', methods=['POST'])
def cifrar():
    text = request.form['text']
    password = request.form['password']
    cifrado = encriptar_mensaje_aes(text, password)
    return jsonify({'status': 'success', 'message': 'Text received successfully', 'cifrado':cifrado}), 200


@app.route('/descifrar', methods=['POST'])
def descifrar():
    text = request.form['text']
    password = request.form['password']
    key = SHA256.new(password.encode()).digest()
    iv = base64.b64decode(text)[:16]
    text = base64.b64decode(text)[16:]
    # Descifra la contraseña
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        cifrado = unpad(cipher.decrypt(text), AES.block_size)
        cifrado = cifrado.decode('utf-8')
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Clave de descifrado incorrecta','cifrado': 'La clave de cifrado es incorrecta o los datos proporcionados no son válidos.'}), 200
    
    return jsonify({'status': 'success', 'message': 'Text decrypted successfully', 'cifrado': cifrado}), 200


def encriptar_mensaje_aes(mensaje, clave, random = ""):
    key_sha256 = SHA256.new(clave.encode()).digest()  # Hash the password to get a 32-byte key
    if(random == ""):
        iv = get_random_bytes(16)
    else:
        iv = random
    
    cipher = AES.new(key_sha256, AES.MODE_CBC, iv)
    cifrado = cipher.encrypt(pad(mensaje.encode(), AES.block_size))
    cifrado = base64.b64encode(iv + cifrado)  # Prepend the IV to the ciphertext
    cifrado = cifrado.decode('utf-8').strip()
    return cifrado

def desencriptar_mensaje_aes(mensaje, clave):
    key = SHA256.new(clave.encode()).digest()
    iv = base64.b64decode(mensaje)[:16]
    mensaje = base64.b64decode(mensaje)[16:]

    # Descifra la contraseña
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cifrado = unpad(cipher.decrypt(mensaje), AES.block_size)
    cifrado = cifrado.decode('utf-8')
    return cifrado

if __name__ == '__main__':
    app.run(debug=True)
