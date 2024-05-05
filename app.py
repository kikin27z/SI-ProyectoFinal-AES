"""
py -m pip install Flask-Caching
py -m pip install Flask-MySQLdb
py -m pip install Flask
py -m pip install Flask-Session
py -m pip install Flask-MySQL
"""

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_caching import Cache
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib

app = Flask(__name__)

# Contraseña para encriptar las sesiones
app.secret_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6ImthcmltIHRva2VuIiwiaWF0IjoxNTE2MjM5MDIyfQ.yvlR6F7xRnCSBRHTUNmvC6Pcvc_gFZ1C6S6ncEIJltA'
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

    if request.method == 'POST' and 'usuario' in request.form and 'contrasena' in request.form:
        # Creo variables con los datos del formulario
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        # Encripta la contraseña
        hash = contrasena + app.secret_key
        hash = hashlib.sha1(hash.encode())
        contrasena = hash.hexdigest()
        print(contrasena)
        # Verifica si el usuario y la contraseña existen en la base de datos
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM cuentas WHERE usuario = %s AND contrasena = %s', (usuario, contrasena,))
        # Devuelve un registro y retorna el resultado
        cuenta = cursor.fetchone()

        if cuenta:
            # Crea la sesión del usuario, inicia sesión y retiene cierta info para trabajar con otras rutas
            session['loggedin'] = True
            session['id'] = cuenta['id']
            session['username'] = cuenta['usuario']

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

        # Verifica si la cuenta existe en la base de datos
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM cuentas WHERE usuario = %s', (usuario,))
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
            hash = contrasena + app.secret_key
            hash = hashlib.sha1(hash.encode())
            contrasena = hash.hexdigest()
            # Inserta la nueva cuenta en la base de datos
            cursor.execute('INSERT INTO cuentas (usuario,contrasena) VALUES  (%s, %s)', (usuario, contrasena,))
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

        return render_template('convertidor.html', cuenta=cuenta)
    
    # Usuario no ha iniciado sesión, redirige al inicio sesión
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)